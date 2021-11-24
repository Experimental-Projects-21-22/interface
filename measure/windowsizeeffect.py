import time

import numpy as np
from matplotlib import pyplot as plt

from utils.delays import DelayLines
from .scheme import BaseScheme

START_DELAY = 20
END_DELAY = 80
ITERATIONS = END_DELAY - START_DELAY


class WindowSizeEffect(BaseScheme):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, data_shape=(6, ITERATIONS), iterations=ITERATIONS, **kwargs)

        # Desired delays
        self.data[0] = np.linspace(START_DELAY, END_DELAY, ITERATIONS)
        # Optimal steps for the delays
        self.data[1] = DelayLines.CA.calculate_steps(self.data[0])
        self.data[2] = DelayLines.CB.calculate_steps(self.data[0])

    def metadata(self) -> dict:
        metadata = super().metadata
        metadata.update({
            'start_delay': START_DELAY,
            'end_delay':   END_DELAY,
            'iterations':  ITERATIONS,
        })
        return metadata

    def setup(self):
        # Set the interferometer rotation to a known state.
        self.interferometer.set_rotation(0)
        # Set the coincidence circuit to its initial state.
        self.coincidence_circuit.toggle_verbose()
        for delay_line in DelayLines:
            steps = delay_line.calculate_steps(START_DELAY)
            self.coincidence_circuit.set_delay(steps, delay_line)

    def iteration(self, i):
        # Set the desired state
        self.coincidence_circuit.set_delay(self.data[1, i], DelayLines.CA)
        self.coincidence_circuit.set_delay(self.data[2, i], DelayLines.CB)
        self.coincidence_circuit.clear_counters()
        # Wait for the data to be acquired.
        time.sleep(0.5)
        # Obtain the data
        self.data[1:, i] = self.coincidence_circuit.save_and_read_counts()

    @staticmethod
    def analyse(data):
        delays = data[0]
        counts1 = data[3]
        counts2 = data[4]
        coincidences = data[5]

        plt.plot(delays, counts1, label='Counts 1')
        plt.plot(delays, counts2, label='Counts 2')
        plt.plot(delays, coincidences, label='Coincidences')
        plt.ylabel('Counts')
        plt.xlabel('Steps')
        plt.show()
