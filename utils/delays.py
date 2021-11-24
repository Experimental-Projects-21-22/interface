from enum import Enum, auto
from functools import lru_cache
from typing import overload

import numpy as np
# The maximum number of steps.
from loguru import logger

DELAY_STEPS: int = 2 ** 8 - 1
# File containing the calibration data.
DELAY_LINE_CALIBRATION_FILE = f'{__file__.strip("delays.py")}../data/calibration/delay_lines.csv'


@overload
def validate_delay_steps(steps: np.ndarray) -> np.ndarray:
    ...


@overload
def validate_delay_steps(steps: int) -> int:
    ...


def validate_delay_steps(steps):
    """
    Raises a ValueError if the delay step is not in the range [0, DELAY_STEPS]. Else it returns steps.
    """
    if not np.all(0 <= steps <= DELAY_STEPS):
        raise ValueError(f'Delay step must be in the range [0, {DELAY_STEPS}].')
    return steps


class DelayLines(Enum):
    """
    Provides an enum with the delay lines in our coincidence circuit. The delay lines are calibrated at run time with
    once and a cached version is used for future calls. The calibration is performed using a linear fit. This class
    furthermore provides several methods to calculate and convert delays for the delay lines.
    """

    # noinspection PyMethodParameters
    def _generate_next_value_(name, start, count, last_values):
        """
        Generates enum values for the delay lines in the form `(name, index)`. Here index is used for looking up the
        calibration data.

        Please note that this method is called by the enum module. Most IDEs will think `name` should be `self`, you
        should ignore this. For this method `name` is the name of the enum value.
        """
        index = start + count - 1
        logger.debug(f'Registering delay line {name} with index {index}.')
        return name, index

    # The enum values should be in the same order as the data in the calibration file.
    CA = auto()
    WA = auto()
    CB = auto()
    WB = auto()

    @classmethod
    @lru_cache(maxsize=1)
    def _calibration(cls) -> np.ndarray:
        """
        Calculates the calibration data for the delay lines. The calibration data is a 2x4 matrix. The first row
        contains the slope of the delay. The second row contains the minimum delay.
        """
        logger.info('Calculating delay line calibration data.')
        calibration_data: np.ndarray = np.loadtxt(DELAY_LINE_CALIBRATION_FILE, delimiter=',', skiprows=1)

        # noinspection PyTypeChecker
        return np.polyfit(calibration_data[:, 0], calibration_data[:, 1:], 1)

    def __str__(self):
        """
        :return: the name of the delay line, used for pretty printing.
        """
        return self.name

    @property
    def index(self) -> int:
        """
        :return: the index of the delay line, used for looking up the calibration data.
        """
        return self.value[1]

    @overload
    def calculate_delay(self, steps: np.ndarray) -> np.ndarray:
        ...

    @overload
    def calculate_delay(self, steps: int) -> float:
        ...

    def calculate_delay(self, steps):
        """
        Calculates the delay (in ns) for a given number of steps.
        :param steps: the number of steps.
        :return: a delay value in ns (including the offset or zero-delay).
        """
        validate_delay_steps(steps)
        return self.minimum_delay + self.delay_step * steps

    @overload
    def calculate_steps(self, delay: np.ndarray) -> np.ndarray:
        ...

    @overload
    def calculate_steps(self, delay: float) -> int:
        ...

    def calculate_steps(self, delay):
        """
        Calculates the number of steps for a given delay and rounds the result to the nearest possible integer. This
        means that the returned value is always between 0 and DELAY_STEPS.
        :param delay: the delay in ns.
        :return: the number of steps resulting in the closest possible delay.
        """
        optimal_step = (delay - self.minimum_delay) / self.delay_step
        optimal_step = np.round(optimal_step).astype(int)
        return validate_delay_steps(optimal_step)

    @property
    def maximum_delay(self) -> float:
        """
        :return: the maximum delay in ns.
        """
        return self.calculate_delay(DELAY_STEPS)

    @property
    def minimum_delay(self) -> float:
        """
        :return: the minimum delay in ns.
        """
        return self._calibration()[1, self.index]

    @property
    def delay_step(self) -> float:
        """
        :return: the delay step in ns.
        """
        return self._calibration()[0, self.index]
