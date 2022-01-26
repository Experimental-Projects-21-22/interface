"""
This file, interface.py, provides several classes to interface with the Arduinos that control our experiment.

Written by:
    Julian van Doorn <j.c.b.van.doorn@umail.leidenuniv.nl>
    Douwe Remmelts <remmeltsdouwe@gmail.com>
    Bálint Bosman <b.bosman@umail.leidenuniv.nl>

CCD interface code based on code previously written by Matthijs Rog.
"""
import re
from time import sleep
from typing import Tuple, TypeVar

import numpy as np
from loguru import logger
from serial import Serial

from utils.delays import DelayLines, validate_delay_steps
from utils.steps import validate_interferometer_steps

try:
    import ftd2xx as ftd
except ImportError:
    logger.warning("FTD2XX library not found, do not use the CCD interface.")
    ftd = None
except OSError:
    logger.warning("FTD2XX binaries not found, do not use the CCD interface.")
    ftd = None

COUNTER_REGEX = re.compile(r'(\d+),(\d+),(\d+)')
DELAY_REGEX = re.compile(r'(\d+)')

# Used for type hints.
C = TypeVar('C', bound='Arduino')


class Arduino(Serial):
    """
    An interface to an Arduino. Behaves almost identical to the Serial class of pyserial. However, it overwrites some
    methods that make it easier to work with the Arduino.
    """

    ARDUINO_EOL = b'\r\n'

    def __init__(self, *args, name: str = "Arduino", **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

        logger.info(f"Serial interface to the {self.name} initialized.")

    def send_command(self, command):
        """
        Identical to the write method of Serial, however this method will automatically encode the data if it is a str
        and explicitly appends a newline (\n) character if it is not present. This avoid that the Arduino can receive
        two concatenated strings if commands are rapidly sent after each other.
        """
        if not isinstance(command, str):
            logger.debug(f"Automatically converting command from {type(command).__name__} to str.")
            command = str(command)

        logger.info(f"Sending the following command to the {self.name}: {command}")
        if not command.endswith('\n'):
            logger.debug("Appending a newline (\\n) to command.")
            command += '\n'
        self.write(command.encode())

    def __enter__(self: C) -> C:
        logger.info(f"Serial interface to the {self.name} is being opened.")
        super().__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        logger.info(f"Serial interface to the {self.name} is being closed.")
        super().__exit__(*args, **kwargs)
        return self

    def readline(self, **kwargs) -> str:
        """
        Performs a super call to readline. This function reads until it encounters a '\n'. However, since the Arduino
        uses '\r\n' as its EOL character we want to strip both of these. For ease of use this function will
        automatically decode the bytes.

        :param kwargs: optional characters to pass to the super call.
        :return: a str containing all text up to (excluding) the newline characters.
        """
        message = super().readline(**kwargs)
        message = message.rstrip(self.ARDUINO_EOL).decode()

        # logger.debug(f"Received the following data from the {self.name}: {message}.")
        return message

    def find_pattern(self, pattern: re.Pattern) -> re.Match:
        """
        Reads lines until it finds a line that matches the specified pattern.
        :param pattern: the pattern to match the lines against.
        :return: a match to the pattern.
        """
        while True:
            message = self.readline()
            match = pattern.fullmatch(message)

            if match:
                return match


class CoincidenceCircuit(Arduino):
    """
    Class to control the coincidence circuit. This consists of the delay lines as well as the counters.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, name='coincidence circuit', **kwargs)

    def toggle_verbose(self):
        """
        Turns verbose mode on or off on the Arduino.
        """
        self.send_command('VERB')

    def clear_counters(self):
        """
        Clears all the counts on the counters. Note that the registers remain unaffected.
        """
        self.send_command('CLEAR')

    def save_counts_to_register(self):
        """
        Saves the counts in the counters to their register. This allows them to be read out by the Arduino.
        """
        self.send_command('SAVE')

    def read_counts_from_register(self) -> Tuple[int, int, int]:
        """
        Reads the counts from the registers of the counter chips.
        :return: a tuple with the count on each counter.
        """
        self.send_command('READ')
        match = self.find_pattern(COUNTER_REGEX)
        # noinspection PyTypeChecker
        return tuple([int(x) for x in match.group(1, 2, 3)])

    def save_and_read_counts(self) -> Tuple[int, int, int]:
        """
        Combines save_counts_to_register with read_counts_from_register. See their docstrings.
        """
        self.save_counts_to_register()
        return self.read_counts_from_register()

    def set_delay(self, steps: int, delay_line: DelayLines):
        """
        Sets the delay of the specified delay line to the specified value.
        :param steps: value where step * d + d0 is the delay in ns.
        """
        steps = validate_delay_steps(steps)

        logger.debug(
            f"Setting delay of {delay_line.name} to {steps} steps ({delay_line.calculate_delays(steps):3f} [ns]).")

        self.send_command(steps)
        self.send_command('SD' + str(delay_line))

    def measure(self, time: int) -> Tuple[int, int, int]:
        """
        Clears the counters and measures for the specified time. Should be the preferred method for gathering data.
        :param time: the time in s to measure for.
        :return: a tuple with the counts on each counter.
        """
        self.send_command(time)
        self.send_command('MEASURE')
        match = self.find_pattern(COUNTER_REGEX)
        # noinspection PyTypeChecker
        return tuple([int(x) for x in match.group(1, 2, 3)])


class Interferometer(Arduino):
    def __init__(self, *args, **kwargs):
        logger.warning("Please turn OFF the stepper PSU! Press enter to continue.")
        input()

        super().__init__(*args, name='interferometer', **kwargs)

        logger.warning("Please turn ON the stepper PSU! Press enter to continue.")
        input()

    def rotate(self, steps: int, delay: float = 1.0):
        """
        Rotates the interferometer by the specified number of steps. The delay makes sure that the Arduino has time
        to process the command.
        :param steps: amount of steps to take.
        :param delay: the delay in s to wait after the command is sent.
        """
        steps = validate_interferometer_steps(steps)
        self.send_command(steps)
        sleep(delay)


class CCDInterface:
    # Integration time in microseconds.
    INTEGRATION_TIME = 10000
    # Number of shots per acquisition.
    NUMBER_OF_SHOTS = 1
    # The CCD port either 0 or 1.
    CCD_PORT = 1
    # Timeouts in milliseconds.
    TIMEOUT = 500
    # Number of pixels in the CCD.
    PIXELS = 3648

    def __init__(self):
        if not ftd:
            raise ImportError('Could not import FTD2XX library, as such the CCD interface is not available.')

        # Initialize the CCD.
        self.ccd = ftd.open(self.CCD_PORT)
        # Set the timeouts for the CCD.
        self.cdd.setTimeouts(self.TIMEOUT, self.TIMEOUT)

        # Set the integration time.
        self.ccd.write(b"\xc1")
        self.ccd.write(self.INTEGRATION_TIME.to_bytes(4, 'big'))
        _ = self.ccd.read(self.CCD_PORT)

    def snapshot(self) -> np.ndarray:
        """
        Takes a snapshot from the CCD.
        :return: the snapshot as a numpy array.
        """
        self.ccd.write(b"\xc6")

        # Wait for the CCD to finish.
        queue = 0
        while queue < 2 * self.PIXELS:
            queue = self.ccd.getQueueStatus()

        # encode the received bits as 16-bit integers
        response = self.ccd.read(2 * self.PIXELS)
        data = np.frombuffer(response, dtype='>u2')
        return data
