"""
This file, interface.py, provides several classes to interface with the Arduinos that control our experiment.

Written by:
    Julian van Doorn <j.c.b.van.doorn@umail.leidenuniv.nl>
    Douwe Remmelts <remmeltsdouwe@gmail.com>
"""
import re
from typing import List, Tuple

from loguru import logger
from serial import Serial

DELAY_LINES: List[str] = ['CA', 'WA', 'CB', 'WB']

COUNTER_REGEX = re.compile(r'(\d+),(\d+),(\d+)')


class Arduino(Serial):
    """
    An interface to an Arduino. Behaves almost identical to the Serial class of pyserial. However, it overwrites some
    methods that make it easier to work with the Arduino.
    """

    ARDUINO_EOL = b'\r\n'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def write(self, data):
        """
        Identical to the write method of Serial, however this method will automatically encode the data if it is a str.
        """
        if isinstance(data, str):
            super().write(data.encode())
        else:
            super().write(data)

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

        logger.info(message)
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


class Coincidence(Arduino):
    """
    Class to control the coincidence circuit. This consists of the delay lines as well as the counters.
    """

    def toggle_verbose(self):
        """
        Turns verbose mode on or off on the Arduino.
        """
        self.write('VERB')

    def clear_counters(self):
        """
        Clears all the counts on the counters. Note that the registers remain unaffected.
        """
        self.write('CLEAR')

    def save_counts_to_register(self):
        """
        Saves the counts in the counters to their register. This allows them to be read out by the Arduino.
        """
        self.write('SAVE')

    def read_counts_from_register(self) -> Tuple[int, ...]:
        """
        Reads the counts from the registers of the counter chips.
        :return:
        """
        self.write('READ')
        match = self.find_pattern(COUNTER_REGEX)
        counts = tuple([int(x) for x in match.group(1, 2, 3)])
        return counts

    def save_and_read_counts(self) -> Tuple[int, ...]:
        """
        Combines save_counts_to_register with read_counts_from_register. See their docstrings.
        """
        self.save_counts_to_register()
        return self.read_counts_from_register()

    def set_delay(self, delay: int, delay_line: str):
        """
        Sets the delay of the specified delay line to the specified value.
        :param delay: the delay as an integer where delay * 0.25ns is the actual delay.
        """
        assert delay_line in DELAY_LINES, "Invalid delay line specified"
        self.write(str(delay))
        self.write('SD' + delay_line)

    def increment_delay(self, delay: int, delay_line: str):
        """
        Increments the delay of the specified delay line with the specified value.
        :param delay: the delay as an integer where delay * 0.25ns is the actual delay.
        """
        assert delay_line in DELAY_LINES, "Invalid delay line specified"
        self.write(str(delay))
        self.write('ID' + delay_line)

    def decrement_delay(self, delay: int, delay_line: str):
        """
        Decrements the delay of the specified delay line with the specified value.
        :param delay: the delay as an integer where delay * 0.25ns is the actual delay.
        """
        assert delay_line in DELAY_LINES, "Invalid delay line specified"
        self.write(str(delay))
        self.write('DD' + delay_line)


class Stepper(Arduino):
    # Class to control the stepper motor
    def rotate(self, angle):
        # Rotates the stepper motor to a specified angle
        pass
