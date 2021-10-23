"""
This file, interface.py, provides several classes to interface with the Arduinos that control our experiment.

Written by:
    Julian van Doorn <j.c.b.van.doorn@umail.leidenuniv.nl>
    Douwe Remmelts <remmeltsdouwe@gmail.com>
"""
from typing import List

from serial import Serial

DELAY_LINES: List[str] = ['CA', 'WA', 'CB', 'WB']


class Arduino(Serial):
    """
    An interface to an Arduino. Behaves almost identical to the Serial class of pyserial. Currently the only difference
    is that this class will automatically encode a str when passed to the write method. Object should be instantiated
    (or is recommended to be done so) using a with statement.
    """

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


class Coincidence(Arduino):
    """
    Class to control the coincidence circuit. This consists of the delay lines as well as the counters.
    """

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

    def read_counts_from_register(self):
        """
        Reads the counts from the registers of the counter chips.
        :return:
        """
        self.write('READ')
        return self.read()

    def save_and_read_counts(self):
        """
        Combines save_counts_to_register with read_counts_from_register. See their docstrings.
        """
        self.save_counts_to_register()
        self.read_counts_from_register()
        return self.read()

    def set_delay(self, delay: int, delay_line: str):
        """
        Sets the delay of the specified delay line to the specified value.
        :param delay: the delay as an integer where delay * 0.25ns is the actual delay.
        """
        assert delay_line in DELAY_LINES, "Invalid delay line specified"
        self.write(delay.to_bytes(length=8, byteorder='little', signed=False))
        self.write('SD' + delay_line)

    def increment_delay(self, delay: int, delay_line: str):
        """
        Increments the delay of the specified delay line with the specified value.
        :param delay: the delay as an integer where delay * 0.25ns is the actual delay.
        """
        assert delay_line in DELAY_LINES, "Invalid delay line specified"
        self.write(delay.to_bytes(length=8, byteorder='little', signed=False))
        self.write('ID' + delay_line)

    def decrement_delay(self, delay: int, delay_line: str):
        """
        Decrements the delay of the specified delay line with the specified value.
        :param delay: the delay as an integer where delay * 0.25ns is the actual delay.
        """
        assert delay_line in DELAY_LINES, "Invalid delay line specified"
        self.write(delay.to_bytes(length=8, byteorder='little', signed=False))
        self.write('DD' + delay_line)


class Stepper(Arduino):
    # Class to control the stepper motor
    def rotate(self, angle):
        # Rotates the stepper motor to a specified angle
        pass
