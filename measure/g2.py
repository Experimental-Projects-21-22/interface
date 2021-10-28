import time

import numpy as np
from matplotlib import pyplot as plt

from interface import DELAY_LINES
from .scheme import BaseScheme


class G2(BaseScheme):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, data_shape=(4, 5), iterations=5, **kwargs)

        self.data[0] = np.arange(5)

    def setup(self):
        # Set the interferometer rotation to a known state.
        self.interferometer.set_rotation(0)
        # Set the coincidence circuit to its initial state.
        self.coincidence_circuit.toggle_verbose()
        for delay_line in DELAY_LINES:
            self.coincidence_circuit.set_delay(0, delay_line)

    def iteration(self, i):
        # Set the desired state
        self.coincidence_circuit.set_delay(self.data[0, i], 'WA')
        self.coincidence_circuit.set_delay(self.data[0, i], 'CA')
        self.coincidence_circuit.clear_counters()
        # Wait for the data to be acquired.
        time.sleep(0.5)
        # Obtain the data
        self.data[1:, i] = self.coincidence_circuit.save_and_read_counts()

    @staticmethod
    def analyse(data):
        delays = data[0]
        counts1 = data[1]
        counts2 = data[2]
        coincidences = data[3]

        g2 = coincidences / (counts1 * counts2)

        plt.plot(delays, g2)
        plt.ylabel('g2')
        plt.xlabel('delay')
        plt.show()
