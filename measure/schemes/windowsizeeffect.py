import time

import numpy as np
from matplotlib import pyplot as plt

from measure.scheme import BaseScheme
from utils.delays import DelayLines

BASE_DELAY = 20
START_DELAY = BASE_DELAY
END_DELAY = min(DelayLines.WA.maximum_delay, DelayLines.WB.maximum_delay)
ITERATIONS = int(END_DELAY - START_DELAY)


class WindowSizeEffect(BaseScheme):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, data_points=5, iterations=ITERATIONS, **kwargs)

        # Desired delays.
        desired_delays = np.linspace(START_DELAY, END_DELAY, ITERATIONS)
        # Optimal steps for the delays.
        self.data[0] = DelayLines.WA.calculate_steps(desired_delays)
        self.data[1] = DelayLines.WB.calculate_steps(desired_delays)

    @property
    def metadata(self) -> dict:
        metadata = super().metadata
        metadata.update({
            'base_delay':  BASE_DELAY,
            'start_delay': START_DELAY,
            'end_delay':   END_DELAY,
            'iterations':  ITERATIONS,
        })
        return metadata

    def setup(self):
        # Set the interferometer rotation to a known state.
        self.interferometer.set_rotation(0)
        for delay_line in DelayLines:
            steps = delay_line.calculate_steps(BASE_DELAY)
            self.coincidence_circuit.set_delay(steps, delay_line)

    def iteration(self, i):
        # Set the desired state
        self.coincidence_circuit.set_delay(self.data[0, i], DelayLines.WA)
        self.coincidence_circuit.set_delay(self.data[1, i], DelayLines.WB)
        self.coincidence_circuit.clear_counters()
        # Wait for the data to be acquired.
        time.sleep(1)
        # Obtain the data
        self.data[2:, i] = self.coincidence_circuit.save_and_read_counts()

    @staticmethod
    def analyse(data):
        delay_WA = DelayLines.WA.calculate_delays(data[0, :])
        delay_WB = DelayLines.WB.calculate_delays(data[1, :])

        delays = np.mean(np.asarray([
            delay_WA,
            delay_WB,
        ]), axis=0)
        counts1 = data[2, :]
        counts2 = data[3, :]
        coincidences = data[4, :]

        plt.scatter(delay_WA, counts1, label='Counts 1', marker='+', alpha=0.5)
        plt.scatter(delay_WB, counts2, label='Counts 2', marker='+', alpha=0.5)
        plt.scatter(delays, coincidences, label='Coincidences', marker='x')
        plt.ylabel('Counts')
        plt.xlabel('Delay [ns]')
        plt.legend()
        plt.show()
