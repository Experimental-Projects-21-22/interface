import time

import numpy as np
from matplotlib import pyplot as plt

from measure.scheme import BaseScheme
from utils.delays import DelayLines

start_delay = 20
end_delay = 60
iterations = end_delay - start_delay


class G2(BaseScheme):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, data_points=4, iterations=iterations, **kwargs)

        self.data[0] = np.linspace(start_delay, end_delay, iterations)

    def setup(self):
        # Set the interferometer rotation to a known state.
        self.interferometer.set_rotation(0)
        # Set the coincidence circuit to its initial state.
        self.coincidence_circuit.toggle_verbose()
        for delay_line in DelayLines:
            steps = delay_line.calculate_steps(start_delay)
            self.coincidence_circuit.set_delay(steps, delay_line)

    def iteration(self, i):
        # Set the desired state
        steps = DelayLines.CA.calculate_steps(self.data[0, i])
        self.coincidence_circuit.set_delay(steps, DelayLines.CA)
        steps = DelayLines.CB.calculate_steps(self.data[0, i])
        self.coincidence_circuit.set_delay(steps, DelayLines.CB)
        self.coincidence_circuit.clear_counters()
        # Wait for the data to be acquired.
        time.sleep(0.5)
        # Obtain the data
        self.data[1:, i] = self.coincidence_circuit.save_and_read_counts()

    @staticmethod
    def analyse(data, **metadata):
        delays = data[0]
        counts1 = data[1]
        counts2 = data[2]
        coincidences = data[3]

        g2 = coincidences / (counts1 * counts2)

        plt.plot(delays, g2)
        plt.ylabel('g2')
        plt.xlabel('delay')
        plt.show()
