from unittest import TestCase

from interface import CoincidenceCircuit


class TestDelayValidation(TestCase):
    def setUp(self):
        self.coincidence_circuit = CoincidenceCircuit()

    def test_bounds(self):
        # Float values should be between 0 and 63.75ns.
        self.assertRaises(ValueError, lambda: self.coincidence_circuit.validate_delay(-0.25))
        self.assertRaises(ValueError, lambda: self.coincidence_circuit.validate_delay(64.))
        # Integer values should be between 0 and 2 ** 8 - 1
        self.assertRaises(ValueError, lambda: self.coincidence_circuit.validate_delay(-1))
        self.assertRaises(ValueError, lambda: self.coincidence_circuit.validate_delay(2 ** 8))

    def test_step_size(self):
        # Only float values that are multiples of 0.25ns should be accepted.
        self.assertRaises(ValueError, lambda: self.coincidence_circuit.validate_delay(0.26))
        self.coincidence_circuit.validate_delay(0.25)


class TestDelayConversion(TestCase):
    def setUp(self):
        self.coincidence_circuit = CoincidenceCircuit()

    def test_delay_to_int(self):
        # Check if the bounds properly map -- if so assume the rest does as well.
        self.assertEqual(0, self.coincidence_circuit.delay_to_int(0.))
        self.assertEqual(2 ** 8 - 1, self.coincidence_circuit.delay_to_int(63.75))

    def test_int_to_delay(self):
        # Check if the bounds properly map -- if so assume the rest does as well.
        self.assertEqual(0., self.coincidence_circuit.int_to_delay(0))
        self.assertEqual(63.75, self.coincidence_circuit.int_to_delay(2 ** 8 - 1))
