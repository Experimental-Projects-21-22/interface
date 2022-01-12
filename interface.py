"""
This file, interface.py, provides several classes to interface with the Arduinos that control our experiment.

Written by:
    Julian van Doorn <j.c.b.van.doorn@umail.leidenuniv.nl>
    Douwe Remmelts <remmeltsdouwe@gmail.com>
"""
import re
from typing import Tuple, TypeVar

from loguru import logger
from serial import Serial

from utils.delays import DelayLines, validate_delay_steps

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
        super().__init__(*args, name='interferometer', **kwargs)

    # Class to control the stepper motor
    def set_rotation(self, angle):
        pass

    def rotate(self, angle):
        # Rotates the stepper motor to a specified angle
        pass
