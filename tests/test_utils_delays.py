from unittest import TestCase

import numpy as np

from utils.delays import DELAY_LINE_CALIBRATION_FILE, DELAY_STEPS, DelayLine, validate_delay_step


class TestDelayLines(TestCase):
    def test_calibration_cache(self):
        # Clear the cache to make sure it's empty.
        DelayLine._calibration.cache_clear()
        # Call the function twice.
        DelayLine._calibration()
        DelayLine._calibration()

        # There should be one cache hit.
        self.assertEqual(DelayLine._calibration.cache_info().hits, 1)
        # There should be one cache miss.
        self.assertEqual(DelayLine._calibration.cache_info().misses, 1)

    def test_calculate_delay_bounds(self):
        # Step values should be between 0 and 2 ** 8 - 1
        self.assertRaises(ValueError, lambda: validate_delay_step(-1))
        self.assertRaises(ValueError, lambda: validate_delay_step(2 ** 8))

        validate_delay_step(0)
        validate_delay_step(DELAY_STEPS - 1)

    def test_CA_calibration(self):
        """
        There is nothing special about CA. However we picked to test the various methods of the delay lines.
        """
        CA_data = np.loadtxt(DELAY_LINE_CALIBRATION_FILE, delimiter=',', skiprows=1, usecols=(0, 1))
        # noinspection PyTypeChecker
        CA_calibration: np.ndarray = np.polyfit(CA_data[:, 0], CA_data[:, 1], 1)

        # Check some basic calibration values.
        self.assertEqual(DelayLine.CA.delay_step, CA_calibration[0])
        self.assertEqual(DelayLine.CA.minimum_delay, CA_calibration[1])
        self.assertEqual(DelayLine.CA.maximum_delay, CA_calibration[1] + CA_calibration[0] * DELAY_STEPS)

        # Check that a specific delay is correctly calculated.
        self.assertEqual(DelayLine.CA.calculate_delay(0), DelayLine.CA.minimum_delay)
        self.assertEqual(DelayLine.CA.calculate_delay(DELAY_STEPS), DelayLine.CA.maximum_delay)

        self.assertEqual(DelayLine.CA.calculate_delay(42), DelayLine.CA.minimum_delay + 42 * DelayLine.CA.delay_step)

    def test_index_values(self):
        self.assertEqual(DelayLine.CA.index, 0)
        self.assertEqual(DelayLine.WB.index, 3)
