import numpy as np
from loguru import logger
from matplotlib import pyplot as plt

from measure.scheme import BaseScheme
from utils.delays import DelayLines

LOWER_DELAY_LIMIT = 20
UPPER_DELAY_LIMIT = 80

MEASURE_TIME = 1

WINDOW_SIZE = 12
REGION_SIZE = 20
ITERATIONS = 2 * 4 * REGION_SIZE

CORRECTION_FACTOR = 0

WINDOW_ESTIMATE = 1.1


class WindowShiftEffect(BaseScheme):
    def __init__(self, *args, shift_A: bool = True, **kwargs):
        super().__init__(*args, data_points=5, iterations=ITERATIONS, **kwargs)

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

        # Middle of the achievable delay range
        fixed_delay = LOWER_DELAY_LIMIT + REGION_SIZE
        self.fixed_delay_C = self.fixed_line_C.calculate_steps(fixed_delay)
        self.fixed_delay_W = self.fixed_line_W.calculate_steps(fixed_delay + WINDOW_SIZE)

        # Add a correction so that the windows are centered around 0.
        correction = CORRECTION_FACTOR if shift_A else -CORRECTION_FACTOR
        fixed_delay -= correction

        start_delay = fixed_delay - REGION_SIZE
        end_delay = fixed_delay + REGION_SIZE
        desired_delays = np.linspace(start_delay, end_delay, self._iterations)

        # Optimal steps for the delays.
        self.data[0] = self.shift_line_C.calculate_steps(desired_delays)
        self.data[1] = self.shift_line_W.calculate_steps(desired_delays + WINDOW_SIZE)

    @property
    def metadata(self) -> dict:
        metadata = super().metadata
        metadata.update({
            'window_size':       WINDOW_SIZE,
            'region_size':       REGION_SIZE,
            'shift_A':           self.shift_A,
            'fixed_delay_C':     self.fixed_delay_C,
            'correction_factor': CORRECTION_FACTOR,
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
        self.data[2:, i] = self.coincidence_circuit.measure(MEASURE_TIME)

    @classmethod
    def analyse(cls, data, metadata):
        fig, count_axis = plt.subplots()

        count_axis.set_xlabel('Delay between lines [ns]')
        coincidence_axis = count_axis.twinx()

        count_axis.set_ylabel('Counts')
        coincidence_axis.set_ylabel('Coincidences')

        if metadata['shift_A']:
            title = "Window Shift Effect (A)"
            shift_line_C = DelayLines.CA
            fixed_line_C = DelayLines.CB
        else:
            title = "Window Shift Effect (B)"
            shift_line_C = DelayLines.CB
            fixed_line_C = DelayLines.CA

        plt.title(title + f"\n{metadata['window_size']} ns window, {metadata['correction_factor']} ns correction")

        fixed_delay = fixed_line_C.calculate_delays(metadata['fixed_delay_C'])
        delay = shift_line_C.calculate_delays(data[0, :]) - fixed_delay
        delay += metadata['correction_factor'] if metadata['shift_A'] else -metadata['correction_factor']

        delay_zero_idx = np.argmin(np.abs(delay))
        print(metadata['fixed_delay_C'])
        print(data[0][delay_zero_idx])
        print(data[1][delay_zero_idx])

        counts1 = data[2, :]
        counts2 = data[3, :]
        coincidences = data[4, :]

        count_axis.set_ylim([0, np.max([counts1, counts2]) * 1.1])
        coincidence_axis.set_ylim([0, 300])

        center_peak = delay[coincidences.argsort()[-1]]

        # We now have excellent estimates, so fit the whole thing.
        logger.success(f"Mean counts on detector 1: {np.mean(counts1):.0f}")
        logger.success(f"Mean counts on detector 2: {np.mean(counts2):.0f}")
        logger.success(f"Center coincidence peak: {center_peak:.2f}")

        if np.all(counts1 == counts2):
            count_axis.errorbar(delay, counts1, xerr=np.sqrt(shift_line_C.calculate_delays_std(data[0, :])),
                                fmt='.', label='Single Counts')
        else:
            count_axis.errorbar(delay, counts1, xerr=np.sqrt(shift_line_C.calculate_delays_std(data[0, :])),
                                fmt='.', label='Counts 1')
            count_axis.errorbar(delay, counts2, xerr=np.sqrt(shift_line_C.calculate_delays_std(data[1, :])),
                                fmt='.', label='Counts 2')
        coincidence_axis.scatter(delay, coincidences, label='Coincidences', marker='x', c='g')

        handles, labels = count_axis.get_legend_handles_labels()
        handles += coincidence_axis.get_legend_handles_labels()[0]
        labels += coincidence_axis.get_legend_handles_labels()[1]

        plt.tight_layout()
        plt.legend(handles, labels)
        plt.show()
