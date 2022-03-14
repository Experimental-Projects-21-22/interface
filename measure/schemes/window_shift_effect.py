"""
Written by:
    Julian van Doorn <j.c.b.van.doorn@umail.leidenuniv.nl>
    Douwe Remmelts <remmeltsdouwe@gmail.com>
"""

import numpy as np
from loguru import logger
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import erf

from measure.scheme import BaseScheme
from utils.delays import DelayLines

LOWER_DELAY_LIMIT = 20

MEASURE_TIME = 1

WINDOW_SIZE = 12
REGION_SIZE = 6
ITERATIONS = 2 * 4 * REGION_SIZE

CA_INDEX = 0
WA_INDEX = 1
CB_INDEX = 2
WB_INDEX = 3
C1_INDEX = 4
C2_INDEX = 5
CO_INDEX = 6


class WindowShiftEffect(BaseScheme):
    def __init__(self, *args, shift_A: bool = True, **kwargs):
        super().__init__(*args, data_points=7, iterations=ITERATIONS, **kwargs)
        self.shift_A = shift_A

        fixed_delay = LOWER_DELAY_LIMIT + REGION_SIZE
        start_delay = fixed_delay - REGION_SIZE
        # start_delay = 16
        end_delay = fixed_delay + REGION_SIZE
        # end_delay = 16

        desired_delays = np.linspace(start_delay, end_delay, self._iterations)

        if shift_A:
            self.data[CA_INDEX, :] = DelayLines.CA.calculate_steps(desired_delays)
            self.data[WA_INDEX, :] = DelayLines.WA.calculate_steps(desired_delays + WINDOW_SIZE)
            self.data[CB_INDEX, :] = np.tile(DelayLines.CB.calculate_steps(fixed_delay), self._iterations)
            self.data[WB_INDEX, :] = np.tile(DelayLines.WB.calculate_steps(fixed_delay + WINDOW_SIZE), self._iterations)
        else:
            self.data[CA_INDEX, :] = np.tile(DelayLines.CA.calculate_steps(fixed_delay), self._iterations)
            self.data[WA_INDEX, :] = np.tile(DelayLines.WA.calculate_steps(fixed_delay + WINDOW_SIZE), self._iterations)
            self.data[CB_INDEX, :] = DelayLines.CB.calculate_steps(desired_delays)
            self.data[WB_INDEX, :] = DelayLines.WB.calculate_steps(desired_delays + WINDOW_SIZE)

    @property
    def metadata(self) -> dict:
        metadata = super().metadata
        metadata.update({
            'window_size': WINDOW_SIZE,
            'region_size': REGION_SIZE,
            'shift_A':     self.shift_A,
        })
        return metadata

    def setup(self):
        pass

    def iteration(self, i):
        # Set the desired state
        self.coincidence_circuit.set_delay(self.data[CA_INDEX, i], DelayLines.CA)
        self.coincidence_circuit.set_delay(self.data[WA_INDEX, i], DelayLines.WA)
        self.coincidence_circuit.set_delay(self.data[CB_INDEX, i], DelayLines.CB)
        self.coincidence_circuit.set_delay(self.data[WB_INDEX, i], DelayLines.WB)

        counts1, counts2, coincidences = self.coincidence_circuit.measure(MEASURE_TIME)
        self.data[C1_INDEX, i] = counts1
        self.data[C2_INDEX, i] = counts2
        self.data[CO_INDEX, i] = coincidences

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
    def _distribution(delay: np.ndarray, Nd: float, N: float, sigma: float, delay_offset: float,
                      window: float) -> np.ndarray:
        return Nd + N / 2 * (erf((delay - delay_offset + window) / (np.sqrt(2 * np.pi) * sigma))
                             - erf((delay - delay_offset - window) / (np.sqrt(2 * np.pi) * sigma)))

    @classmethod
    def analyse(cls, data, metadata):
        if metadata['shift_A']:
            delay = DelayLines.CA.calculate_delays(data[CA_INDEX, :]) - DelayLines.CB.calculate_delays(
                data[CB_INDEX, :])
        else:
            delay = DelayLines.CB.calculate_delays(data[CB_INDEX, :]) - DelayLines.CA.calculate_delays(
                data[CA_INDEX, :])

        counts1 = data[C1_INDEX, :]
        counts2 = data[C2_INDEX, :]
        coincidences = data[CO_INDEX, :]

        p0 = (np.min(coincidences), np.max(coincidences), 1, 0, (metadata['window_size'] - 11) * 2)
        popt, _ = curve_fit(cls._distribution, delay, coincidences, p0=p0)

        logger.success(f"Fit parameters: {popt}")
        logger.success(f"Mean counts on detector 1: {np.mean(counts1):.0f}")
        logger.success(f"Mean counts on detector 2: {np.mean(counts2):.0f}")

        # Plot the data.
        cls._plot_counts(delay, counts1, counts2, coincidences, popt, metadata)
