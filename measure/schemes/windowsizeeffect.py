import time

import numpy as np
from matplotlib import pyplot as plt

from measure.scheme import BaseScheme
from utils.delays import DelayLines

START_DELAY = 20
END_DELAY = 80
ITERATIONS = END_DELAY - START_DELAY


class WindowSizeEffect(BaseScheme):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, data_shape=(5, ITERATIONS), iterations=ITERATIONS, **kwargs)

        # Desired delays.
        desired_delays = np.linspace(START_DELAY, END_DELAY, ITERATIONS)
        # Optimal steps for the delays.
        self.data[0] = DelayLines.CA.calculate_steps(desired_delays)
        self.data[1] = DelayLines.CB.calculate_steps(desired_delays)

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
        for delay_line in DelayLines:
            steps = delay_line.calculate_steps(START_DELAY)
            self.coincidence_circuit.set_delay(steps, delay_line)

    def iteration(self, i):
        # Set the desired state
        self.coincidence_circuit.set_delay(self.data[0, i], DelayLines.CA)
        self.coincidence_circuit.set_delay(self.data[1, i], DelayLines.CB)
        self.coincidence_circuit.clear_counters()
        # Wait for the data to be acquired.
        time.sleep(0.5)
        # Obtain the data
        self.data[2:, i] = self.coincidence_circuit.save_and_read_counts()

    @staticmethod
    def analyse(data):
        delays = np.mean(np.asarray([
            DelayLines.CA.calculate_delays(data[0, :]),
            DelayLines.CB.calculate_delays(data[1, :]),
        ]))
        counts1 = data[2]
        counts2 = data[3]
        coincidences = data[4]

        plt.plot(delays, counts1, label='Counts 1')
        plt.plot(delays, counts2, label='Counts 2')
        plt.plot(delays, coincidences, label='Coincidences')
        plt.ylabel('Counts')
        plt.xlabel('Steps')
        plt.show()
