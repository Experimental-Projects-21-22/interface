"""
This file contains all the code to load, analyze and plot the data from the various WindowShiftEffect measurements we
performed. It will also fit some parameters of theoretical models to the data.

Written by:
    Julian van Doorn <j.c.b.van.doorn@umail.leidenuniv.nl>
    Douwe Remmelts <remmeltsdouwe@gmail.com>
"""

import numpy as np
from loguru import logger
from matplotlib import pyplot as plt
from numpy.lib.npyio import NpzFile
from scipy.optimize import curve_fit

from measure.schemes.window_shift_effect import WindowShiftEffect
from utils.delays import DelayLines

DATA_DIRECTORY = "data/WindowShiftEffect/"
FILES = [
    DATA_DIRECTORY + "2022-01-18-17:18:22.npz",
    DATA_DIRECTORY + "2022-01-18-17:20:26.npz",
    DATA_DIRECTORY + "2022-01-18-17:22:58.npz",
    DATA_DIRECTORY + "2022-01-18-17:25:02.npz",
    DATA_DIRECTORY + "2022-01-18-17:27:25.npz",
    DATA_DIRECTORY + "2022-01-18-17:29:29.npz",
    DATA_DIRECTORY + "2022-01-18-17:31:45.npz",
    DATA_DIRECTORY + "2022-01-18-17:33:49.npz",
    DATA_DIRECTORY + "2022-01-18-17:36:17.npz",
    DATA_DIRECTORY + "2022-01-18-17:38:21.npz",
    DATA_DIRECTORY + "2022-01-18-17:41:20.npz",
    DATA_DIRECTORY + "2022-01-18-17:43:23.npz",
    DATA_DIRECTORY + "2022-01-18-17:45:42.npz",
    DATA_DIRECTORY + "2022-01-18-17:47:45.npz",
]

targeted_window_sizes = np.zeros(len(FILES))
fit_parameters = np.zeros((len(FILES), 5))
fit_parameters_std = np.zeros((len(FILES), 5))

for i, file in enumerate(FILES):
    # noinspection PyTypeChecker
    file_contents: NpzFile = np.load(file)
    # Retrieve the data and metadata.
    metadata = {key: file_contents[key] for key in file_contents.files if key != 'data'}
    data = file_contents['data']

    shift_line_C = DelayLines.CA if metadata['shift_A'] else DelayLines.CB
    fixed_line_C = DelayLines.CB if metadata['shift_A'] else DelayLines.CA

    fixed_delay = fixed_line_C.calculate_delays(metadata['fixed_delay_C'])
    delay = shift_line_C.calculate_delays(data[0, :]) - fixed_delay

    counts1 = data[2, :]
    counts2 = data[3, :]
    coincidences = data[4, :]

    targeted_window_sizes[i] = targeted_window_size = metadata['window_size']

    p0 = (np.min(coincidences), np.max(coincidences), 1, 0, (targeted_window_size - 11) * 2)
    popt, pcov = curve_fit(WindowShiftEffect._distribution, delay, coincidences, p0=p0, maxfev=2000)
    fit_parameters[i] = popt
    fit_parameters_std[i] = np.sqrt(np.diag(pcov))

# Take absolute values of window size / sigma.
fit_parameters[:, 2] = np.abs(fit_parameters[:, 2])
fit_parameters[:, 4] = np.abs(fit_parameters[:, 4])
# Enlarge the STD of the window size/tau_0, too small to see otherwise.
fit_parameters_std[:, 3] *= 10
fit_parameters_std[:, 4] *= 50

window_sizes = fit_parameters[:, 4]
fit_window_sizes = np.arange(np.min(window_sizes), np.max(window_sizes), 0.1)

labels = [
    "$N_d$",
    "$N$",
    "$\\sigma$",
    "$\\tau_0$ [ns]",
    "$\\tau_w$ [ns]",
]
for i, label in enumerate(labels):
    logger.info(f"Mean for {label}: {fit_parameters[:, i].mean()}")
    logger.info(f"Mean (A) for {label}: {fit_parameters[::2, i].mean()}")
    logger.info(f"Mean (B) for {label}: {fit_parameters[1::2, i].mean()}")
    plt.errorbar(window_sizes[::2], fit_parameters[::2, i],
                 xerr=fit_parameters_std[::2, 4], yerr=fit_parameters_std[::2, i],
                 fmt='o', label='Shifting line A')
    plt.errorbar(window_sizes[::2], fit_parameters[1::2, i],
                 xerr=fit_parameters_std[1::2, 4], yerr=fit_parameters_std[1::2, i],
                 fmt='o', label='Shifting line B')
    plt.xlabel("Window size ($\\tau_w$) [ns]")
    plt.ylabel(label)
    plt.legend()

    file_label = label.replace('$', '')
    file_label = file_label.replace(' ', '_')
    file_label = file_label.replace('\\', '')
    plt.savefig(f"figures/{file_label}.pdf")

    plt.show()

function = lambda x, a, b: a * x + b
popt, pcov = curve_fit(function, window_sizes, fit_parameters[:, 0])
pstd = np.sqrt(np.diag(pcov))

logger.info(f"Parameters for linear fit on N_d: {popt}")
logger.info(f"STD for linear fit on N_d: {pstd}")
plt.errorbar(window_sizes[::2], fit_parameters[::2, 0],
             xerr=fit_parameters_std[::2, 4], yerr=fit_parameters_std[::2, 0],
             fmt='o', label='Shifting line A')
plt.errorbar(window_sizes[1::2], fit_parameters[1::2, 0],
             xerr=fit_parameters_std[1::2, 4], yerr=fit_parameters_std[1::2, 0],
             fmt='o', label='Shifting line B')
plt.plot(fit_window_sizes, function(fit_window_sizes, *popt), label='Fit')
plt.xlabel("Effective window size ($\\tau_w$) [ns]")
plt.ylabel("$N_d$")
plt.legend()
plt.savefig("figures/fit_N_d.pdf")
plt.show()

SNR = fit_parameters[:, 1] / fit_parameters[:, 0]
function = lambda x, a, b: a / x + b
popt, pcov = curve_fit(function, window_sizes, SNR)
pstd = np.sqrt(np.diag(pcov))

logger.info(f"Parameters for inverse fit on SNR: {popt}")
logger.info(f"STD for inverse fit on SNR: {pstd}")
plt.errorbar(window_sizes[::2], SNR[::2],
             xerr=fit_parameters_std[::2, 4], yerr=np.sqrt(
        (fit_parameters_std[::2, 0] / fit_parameters[::2, 1]) ** 2 + fit_parameters[::2, 1] / (
                2 * fit_parameters_std[::2, 0] ** 2)),
             fmt='o', label='Shifting line A')
plt.errorbar(window_sizes[1::2], SNR[1::2],
             xerr=fit_parameters_std[1::2, 4],
             fmt='o', label='Shifting line B')
plt.plot(fit_window_sizes, function(fit_window_sizes, *popt), label='Fit')
plt.xlabel("Effective window size ($\\tau_w$) [ns]")
plt.ylabel("SNR ($ N / N_d $)")
plt.legend()
plt.savefig("figures/fit_SNR.pdf")
plt.show()

function = lambda x, a, b: a * x + b
popt, pcov = curve_fit(function, targeted_window_sizes, fit_parameters[:, 4])
pstd = np.sqrt(np.diag(pcov))

logger.info(f"Parameters for linear fit on window size: {popt}")
logger.info(f"STD for linear fit on window size: {pstd}")
plt.errorbar(targeted_window_sizes[::2], fit_parameters[::2, 4],
             yerr=fit_parameters_std[::2, 4],
             fmt='o', label='Shifting line A')
plt.errorbar(targeted_window_sizes[1::2], fit_parameters[1::2, 4],
             yerr=fit_parameters_std[1::2, 4],
             fmt='o', label='Shifting line B')
plt.plot(targeted_window_sizes, function(targeted_window_sizes, *popt), label='Fit')
plt.xlabel("Targeted window size ($\\tau_t$) [ns]")
plt.ylabel("Effective window size ($\\tau_w$) [ns]")
plt.legend()
plt.savefig("figures/fit_window_size.pdf")
plt.show()
