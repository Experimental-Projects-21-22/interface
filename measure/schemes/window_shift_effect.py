import numpy as np
from loguru import logger
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import gamma

from measure.scheme import BaseScheme
from utils.delays import DelayLines

LOWER_DELAY_LIMIT = 20
UPPER_DELAY_LIMIT = 80

MEASURE_TIME = 1

WINDOW_SIZE = 12
REGION_SIZE = 20
ITERATIONS = 2 * 4 * REGION_SIZE

CORRECTION_FACTOR = 0


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
    def _plot_counts(cls, delay, counts1, counts2, coincidences, popt, metadata):
        fig, count_axis = plt.subplots()

        plt.title(f"Window Shift Effect ({'A' if metadata['shift_A'] else 'B'})\n"
                  + f"{metadata['timestamp']}"
                  )

        # Create single count axis
        count_axis.set_ylim([0, np.max([counts1, counts2]) * 1.1])
        count_axis.set_xlabel('Delay between lines [ns]')
        count_axis.set_ylabel('Counts')

        # Create coincidence count axis
        coincidence_axis = count_axis.twinx()
        coincidence_axis.set_ylabel('Coincidences')

        # Plot single counts
        count_axis.scatter(delay, counts1, marker='.', label='Counts 1')
        count_axis.scatter(delay, counts2, marker='.', label='Counts 2')
        # Plot coincidences
        coincidence_axis.scatter(delay, coincidences, label='Coincidences', marker='x', c='g')

        # Plot fit
        fit_delay = np.arange(np.min(delay), np.max(delay), 0.1)
        coincidence_axis.plot(fit_delay, cls._distribution(fit_delay, *popt), label='Fit', c='r')

        # Create proper legend
        handles, labels = count_axis.get_legend_handles_labels()
        handles += coincidence_axis.get_legend_handles_labels()[0]
        labels += coincidence_axis.get_legend_handles_labels()[1]
        plt.legend(handles, labels)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def _distribution(delay: np.ndarray, mu: float, alpha: float, beta: float, offset: float,
                      size: float) -> np.ndarray:
        # https://en.wikipedia.org/wiki/Generalized_normal_distribution
        return offset + size * beta / (2 * alpha * gamma(1 / beta)) * np.exp(-(np.abs(delay - mu) / alpha) ** beta)

    @classmethod
    def analyse(cls, data, metadata):
        shift_line_C = DelayLines.CA if metadata['shift_A'] else DelayLines.CB
        fixed_line_C = DelayLines.CB if metadata['shift_A'] else DelayLines.CA

        fixed_delay = fixed_line_C.calculate_delays(metadata['fixed_delay_C'])
        delay = shift_line_C.calculate_delays(data[0, :]) - fixed_delay
        correction = metadata['correction_factor'] if metadata['shift_A'] else -metadata['correction_factor']
        delay += correction

        counts1 = data[2, :]
        counts2 = data[3, :]
        coincidences = data[4, :]

        p0 = (0, 1, 2, 150, 15000)
        popt, _ = curve_fit(cls._distribution, delay, coincidences, p0=p0)

        logger.success(f"Fit parameters: {popt}")
        logger.success(f"Mean: {popt[0]:.2e}, Variance: {popt[1] ** 2 * gamma(3 / popt[2]) / gamma(1 / popt[2]):.2e}")
        logger.success(f"Mean counts on detector 1: {np.mean(counts1):.0f}")
        logger.success(f"Mean counts on detector 2: {np.mean(counts2):.0f}")

        # Plot the data.
        cls._plot_counts(delay, counts1, counts2, coincidences, popt, metadata)
