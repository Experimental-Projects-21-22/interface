import time

import numpy as np
from matplotlib import pyplot as plt

from measure.scheme import BaseScheme
from utils.delays import DelayLines

WINDOW_SIZE = 11.25

FIXED_DELAY_CB = DelayLines.CB.maximum_delay / 2
FIXED_DELAY_WB = FIXED_DELAY_CB + WINDOW_SIZE

# START_DELAY = DelayLines.CA.minimum_delay
# END_DELAY = DelayLines.WA.maximum_delay - WINDOW_SIZE
START_DELAY = FIXED_DELAY_CB - 7
END_DELAY = FIXED_DELAY_CB + 7
ITERATIONS = int(END_DELAY - START_DELAY) * 4


class WindowShiftEffect(BaseScheme):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, data_points=5, iterations=ITERATIONS, **kwargs)

        # Desired delays.
        desired_delays = np.linspace(START_DELAY, END_DELAY, ITERATIONS)
        # Optimal steps for the delays.
        self.data[0] = DelayLines.CA.calculate_steps(desired_delays)
        self.data[1] = DelayLines.WA.calculate_steps(desired_delays + WINDOW_SIZE)

    @property
    def metadata(self) -> dict:
        metadata = super().metadata
        metadata.update({
            'window_size':    WINDOW_SIZE,
            'fixed_delay_wb': FIXED_DELAY_WB,
            'fixed_delay_cb': FIXED_DELAY_CB,
            'start_delay':    START_DELAY,
            'end_delay':      END_DELAY,
        })
        return metadata

    def setup(self):
        self.coincidence_circuit.set_delay(DelayLines.CB.calculate_steps(FIXED_DELAY_CB), DelayLines.CB)
        self.coincidence_circuit.set_delay(DelayLines.WB.calculate_steps(FIXED_DELAY_WB), DelayLines.WB)

    def iteration(self, i):
        # Set the desired state
        self.coincidence_circuit.set_delay(self.data[0, i], DelayLines.CA)
        self.coincidence_circuit.set_delay(self.data[1, i], DelayLines.WA)
        self.coincidence_circuit.clear_counters()
        # Wait for the data to be acquired.
        time.sleep(1)
        # Obtain the data
        self.data[2:, i] = self.coincidence_circuit.save_and_read_counts()

    @staticmethod
    def analyse(data):
        delay = DelayLines.CA.calculate_delays(data[0, :]) - FIXED_DELAY_CB

        counts1 = data[2, :]
        counts2 = data[3, :]
        coincidences = data[4, :]

        plt.scatter(delay, counts1, label='Counts 1', marker='+', alpha=0.5)
        plt.scatter(delay, counts2, label='Counts 2', marker='+', alpha=0.5)
        plt.scatter(delay, coincidences, label='Coincidences', marker='x')
        plt.ylabel('Counts')
        plt.xlabel('Delay between lines [ns]')
        plt.legend()
        plt.show()
