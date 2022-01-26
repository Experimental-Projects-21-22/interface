import numpy as np
from loguru import logger
from matplotlib import pyplot as plt
from numpy.lib.npyio import NpzFile
from scipy.optimize import curve_fit
from scipy.special import gamma

from measure.schemes.window_shift_effect import WindowShiftEffect
from utils.delays import DelayLines

files = [
    "/Users/julian/PycharmProjects/interface/data/WindowShiftEffect/2022-01-18-17:18:22.npz",
    "/Users/julian/PycharmProjects/interface/data/WindowShiftEffect/2022-01-18-17:20:26.npz",
    "/Users/julian/PycharmProjects/interface/data/WindowShiftEffect/2022-01-18-17:22:58.npz",
    "/Users/julian/PycharmProjects/interface/data/WindowShiftEffect/2022-01-18-17:25:02.npz",
    "/Users/julian/PycharmProjects/interface/data/WindowShiftEffect/2022-01-18-17:27:25.npz",
    "/Users/julian/PycharmProjects/interface/data/WindowShiftEffect/2022-01-18-17:29:29.npz",
    "/Users/julian/PycharmProjects/interface/data/WindowShiftEffect/2022-01-18-17:31:45.npz",
    "/Users/julian/PycharmProjects/interface/data/WindowShiftEffect/2022-01-18-17:33:49.npz",
    "/Users/julian/PycharmProjects/interface/data/WindowShiftEffect/2022-01-18-17:36:17.npz",
    "/Users/julian/PycharmProjects/interface/data/WindowShiftEffect/2022-01-18-17:38:21.npz",
    "/Users/julian/PycharmProjects/interface/data/WindowShiftEffect/2022-01-18-17:41:20.npz",
    "/Users/julian/PycharmProjects/interface/data/WindowShiftEffect/2022-01-18-17:43:23.npz",
    "/Users/julian/PycharmProjects/interface/data/WindowShiftEffect/2022-01-18-17:45:42.npz",
    "/Users/julian/PycharmProjects/interface/data/WindowShiftEffect/2022-01-18-17:47:45.npz",
]

targeted_window_sizes = np.zeros((len(files),))
variances = np.zeros((len(files),))

for i, file in enumerate(files):
    # noinspection PyTypeChecker
    file_contents: NpzFile = np.load(file)
    # Retrieve the data and metadata.
    metadata = {key: file_contents[key] for key in file_contents.files if key != 'data'}
    data = file_contents['data']

    targeted_window_sizes[i] = metadata['window_size']

    shift_line_C = DelayLines.CA if metadata['shift_A'] else DelayLines.CB
    fixed_line_C = DelayLines.CB if metadata['shift_A'] else DelayLines.CA

    fixed_delay = fixed_line_C.calculate_delays(metadata['fixed_delay_C'])
    delay = shift_line_C.calculate_delays(data[0, :]) - fixed_delay

    counts1 = data[2, :]
    counts2 = data[3, :]
    coincidences = data[4, :]

    p0 = (0, targeted_window_sizes[i] - 11, 1, 150, 15000)
    popt, _ = curve_fit(WindowShiftEffect._distribution, delay, coincidences, p0=p0)
    variances[i] = popt[1] ** 2 * gamma(3 / popt[2]) / gamma(1 / popt[2])

    plt.title(f"Targeted window size: {targeted_window_sizes[i]} ({2 * (targeted_window_sizes[i] - 11.15):.2f}) ns")
    plt.grid()
    plt.xlabel(f"Relative delay [ns]")
    plt.ylabel(f"Coincidences")
    plt.plot(delay, coincidences, '.')
    plt.plot(np.arange(np.min(delay), np.max(delay), 0.1),
             WindowShiftEffect._distribution(np.arange(np.min(delay), np.max(delay), 0.1), *popt))
    plt.show()


def linear(x, a, b):
    return a * x + b


deviations = np.sqrt(variances)

popt, _ = curve_fit(linear, targeted_window_sizes, deviations)
logger.success(f"The exponential fit is: {popt}")
logger.success(f"Minimum delay is: {-popt[1] / popt[0]:.2f}")

plt.title("Targeted window Size vs. Deviation")
plt.xlabel("Targeted window Size")
plt.ylabel("Deviation")

plt.plot(targeted_window_sizes, deviations, 'o', label="data")
plt.plot(targeted_window_sizes, linear(targeted_window_sizes, *popt), label="fit")

plt.show()
