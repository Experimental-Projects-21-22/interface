import time

import numpy as np
from loguru import logger
from matplotlib import pyplot as plt

from measure.scheme import BaseScheme
from utils.delays import DelayLines

WINDOW_SIZE = 12
REGION_SIZE = 4

COINCIDENCE_THRESHOLD = 0.05


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
        start_delay = self.fixed_line_C.maximum_delay / 2 - REGION_SIZE
        end_delay = self.fixed_line_C.maximum_delay / 2 + REGION_SIZE
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

    @classmethod
    def analyse(cls, data, metadata):
        if metadata['shift_A']:
            plt.title("Window Shift Effect (A)")
            shift_line_C = DelayLines.CA
            fixed_line_C = DelayLines.CB
        else:
            plt.title("Window Shift Effect (B)")
            shift_line_C = DelayLines.CB
            fixed_line_C = DelayLines.CA
        fixed_delay = fixed_line_C.calculate_delays(metadata['fixed_delay_C'])
        delay = shift_line_C.calculate_delays(data[0, :]) - fixed_delay

        counts1 = data[2, :]
        counts2 = data[3, :]
        coincidences = data[4, :]

        # Approximate the coincidence window
        mask = (coincidences > COINCIDENCE_THRESHOLD * counts1) & (coincidences > COINCIDENCE_THRESHOLD * counts2)
        indices = np.asarray(np.where(mask[1:] != mask[:-1])).flatten()
        window_left_indices = indices[::2]
        window_right_indices = indices[1::2] + 1
        window_left_delay = delay[window_left_indices]
        window_right_delay = delay[window_right_indices]

        no_coincidence_window = len(window_left_delay) == 0 or len(window_right_delay) == 0
        multiple_coincidence_windows = len(window_left_delay) > 1 and len(window_right_delay) > 1
        if multiple_coincidence_windows:
            logger.info(f"Found {len(window_left_delay)} coincidence windows.")
        elif not no_coincidence_window:
            logger.info(f"Window of length: {(window_right_delay - window_left_delay)[0]:.2f}ns.")
            logger.info(f"Window is centered around: {(window_left_delay + window_right_delay)[0] / 2:.2f}ns.")

        plt.scatter(delay, counts1, label='Counts 1', marker='+', alpha=0.5)
        plt.scatter(delay, counts2, label='Counts 2', marker='+', alpha=0.5)
        plt.scatter(delay, coincidences, label='Coincidences', marker='x')

        for ldelay in window_left_delay:
            plt.axvline(ldelay, color='r', linestyle='--', alpha=0.5)
        for rdelay in window_right_delay:
            plt.axvline(rdelay, color='r', linestyle='--', alpha=0.5)

        plt.ylabel('Counts')
        plt.xlabel('Delay between lines [ns]')
        plt.legend()
        plt.show()
