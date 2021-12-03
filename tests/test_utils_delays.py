from unittest import TestCase

import numpy as np

from utils import DELAY_LINE_CALIBRATION_FILE, DELAY_STEPS
from utils.delays import DelayLines, validate_delay_steps


class TestDelayLines(TestCase):
    def test_error_propagation(self):
        for delay_line in DelayLines:
            # If we take no steps the STD should be equal to the error in the minimum delay.
            self.assertAlmostEqual(delay_line.calculate_delays_std(0),
                                   np.sqrt(delay_line._calibration()[1][1, delay_line.index]))
            # The error in the delay step should always be smaller than the error in the minimum delay.
            self.assertTrue(np.sqrt(delay_line._calibration()[1][1, delay_line.index])
                            < np.sqrt(delay_line._calibration()[0][1, delay_line.index]))

    def test_delay_line_approximate_step(self):
        # Check if the values are expected according to the data sheet of the delay lines.
        for delay_line in DelayLines:
            self.assertAlmostEqual(delay_line.minimum_delay, 16.5, delta=3)
            self.assertAlmostEqual(delay_line.delay_step, 0.25, delta=0.05)

    def test_validation_typing(self):
        test_value = 1.
        self.assertEqual(type(validate_delay_steps(test_value)), int)

        test_array = np.array([1., 2., 3.])
        self.assertEqual(validate_delay_steps(test_array).dtype, int)

    def test_calibration_cache(self):
        # Clear the cache to make sure it's empty.
        DelayLines._calibration.cache_clear()
        # Call the function twice.
        DelayLines._calibration()
        DelayLines._calibration()

        # There should be one cache hit.
        self.assertEqual(DelayLines._calibration.cache_info().hits, 1)
        # There should be one cache miss.
        self.assertEqual(DelayLines._calibration.cache_info().misses, 1)

    def test_calculate_steps_bounds(self):
        # Step values should be between a 10ns and 100ns are just not possible.
        self.assertRaises(ValueError, lambda: DelayLines.CA.calculate_steps(10))
        self.assertRaises(ValueError, lambda: DelayLines.CA.calculate_steps(100))

        # Two delays that are barely possible (but somewhere in between) should be possible.
        DelayLines.CA.calculate_steps(20)
        DelayLines.CA.calculate_steps(75)

    def test_calculate_delay_bounds(self):
        # Step values should be between 0 and 2 ** 8 - 1
        self.assertRaises(ValueError, lambda: validate_delay_steps(-1))
        self.assertRaises(ValueError, lambda: validate_delay_steps(2 ** 8))

        validate_delay_steps(0)
        validate_delay_steps(DELAY_STEPS - 1)

    def test_CA_calibration(self):
        """
        There is nothing special about CA. However we picked to test the various methods of the delay lines.
        """
        calibration_data = np.loadtxt(DELAY_LINE_CALIBRATION_FILE, delimiter=',', skiprows=1, usecols=(0, 1, 2))
        # noinspection PyTypeChecker
        CA_calibration: np.ndarray = np.polyfit(calibration_data[:, 0], calibration_data[:, 1], 1,
                                                w=1 / calibration_data[:, 2])

        # Check minimum, maximum and delay step.
        self.assertAlmostEqual(DelayLines.CA.delay_step, CA_calibration[0])
        self.assertAlmostEqual(DelayLines.CA.minimum_delay, CA_calibration[1])
        self.assertAlmostEqual(DelayLines.CA.maximum_delay, CA_calibration[1] + CA_calibration[0] * DELAY_STEPS)

        # Check basic step -> delay conversion.
        self.assertAlmostEqual(DelayLines.CA.calculate_delays(0), DelayLines.CA.minimum_delay)
        self.assertAlmostEqual(DelayLines.CA.calculate_delays(DELAY_STEPS), DelayLines.CA.maximum_delay)

        # Check some random step -> delay conversion.
        self.assertAlmostEqual(DelayLines.CA.calculate_delays(42),
                               DelayLines.CA.minimum_delay + 42 * DelayLines.CA.delay_step)

        # Check some random delay -> step conversion.
        self.assertAlmostEqual(DelayLines.CA.calculate_steps(DelayLines.CA.minimum_delay), 0)
        self.assertAlmostEqual(DelayLines.CA.calculate_steps(DelayLines.CA.maximum_delay), DELAY_STEPS)

        # Check some random delay -> step conversion.
        self.assertAlmostEqual(
            DelayLines.CA.calculate_steps(DelayLines.CA.minimum_delay + 42 * DelayLines.CA.delay_step), 42)

    def test_index_values(self):
        self.assertEqual(DelayLines.CA.index, 0)
        self.assertEqual(DelayLines.WB.index, 3)

    def test_delay_line_name(self):
        self.assertEqual(str(DelayLines.CA), 'CA')
        self.assertEqual(str(DelayLines.WB), 'WB')
