import time

import numpy as np
from matplotlib import pyplot as plt

from measure.scheme import BaseScheme
from utils.delays import DelayLines

WINDOW_SIZE = 11.25
REGION_SIZE = 7


class WindowShiftEffect(BaseScheme):
    def __init__(self, *args, shift_A: bool = True, **kwargs):
        super().__init__(*args, data_points=5, iterations=2 * 4 * REGION_SIZE, **kwargs)

        self.shift_A = shift_A
        if shift_A:
            self.shift_line_C = DelayLines.CA
            self.shift_line_W = DelayLines.WA
            self.fixed_line_C = DelayLines.CB
            self.fixed_line_W = DelayLines.WB
        else:
            self.shift_line_C = DelayLines.CB
            self.shift_line_W = DelayLines.WB
            self.fixed_line_C = DelayLines.CA
            self.fixed_line_W = DelayLines.WA

        self.fixed_delay_C = self.fixed_line_C.calculate_steps(self.fixed_line_C.maximum_delay / 2)
        self.fixed_delay_W = self.fixed_line_W.calculate_steps(self.fixed_line_W.maximum_delay / 2 + WINDOW_SIZE)

        # Desired delays.
        start_delay = self.fixed_delay_C - REGION_SIZE
        end_delay = self.fixed_delay_C + REGION_SIZE
        desired_delays = np.linspace(start_delay, end_delay, self._iterations)
        # Optimal steps for the delays.
        self.data[0] = self.shift_line_C.calculate_steps(desired_delays)
        self.data[1] = self.shift_line_W.calculate_steps(desired_delays + WINDOW_SIZE)

    @property
    def metadata(self) -> dict:
        metadata = super().metadata
        metadata.update({
            'window_size':   WINDOW_SIZE,
            'region_size':   REGION_SIZE,
            'shift_A':       self.shift_A,
            'fixed_delay_C': self.fixed_delay_C,
        })
        return metadata

    def setup(self):
        self.coincidence_circuit.set_delay(self.fixed_delay_C, self.fixed_line_C)
        self.coincidence_circuit.set_delay(self.fixed_delay_W, self.fixed_line_W)

    def iteration(self, i):
        # Set the desired state
        delay_C = self.data[0, i]
        delay_W = self.data[1, i]
        self.coincidence_circuit.set_delay(delay_C, self.shift_line_C)
        self.coincidence_circuit.set_delay(delay_W, self.shift_line_W)
        self.coincidence_circuit.clear_counters()
        # Wait for the data to be acquired.
        time.sleep(1)
        # Obtain the data
        self.data[2:, i] = self.coincidence_circuit.save_and_read_counts()

    @staticmethod
    def analyse(data, **metadata):
        if metadata['shift_A']:
            shift_line_C = DelayLines.CA
            fixed_line_C = DelayLines.CB
        else:
            shift_line_C = DelayLines.CB
            fixed_line_C = DelayLines.CA
        delay = shift_line_C.calculate_delays(data[0, :]) - fixed_line_C.calculate_delays(metadata['fixed_delay_C'])

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
