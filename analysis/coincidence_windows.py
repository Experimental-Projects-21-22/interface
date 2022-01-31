import numpy as np
from matplotlib import pyplot as plt
from numpy.lib.npyio import NpzFile
from scipy.optimize import curve_fit

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

targeted_window_sizes = np.zeros(len(files))
fit_parameters = np.zeros((len(files), 5))
fit_parameters_std = np.zeros((len(files), 5))

for i, file in enumerate(files):
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
    fit_parameters[i], pcov = curve_fit(WindowShiftEffect._distribution, delay, coincidences, p0=p0)
    fit_parameters_std[i] = np.sqrt(np.diag(pcov))

    plt.title(f"Targeted window size: {targeted_window_size} ns")
    plt.grid()
    plt.xlabel(f"Relative delay [ns]")
    plt.ylabel(f"Coincidences")
    plt.plot(delay, coincidences, '.')
    plt.plot(np.arange(np.min(delay), np.max(delay), 0.1),
             WindowShiftEffect._distribution(np.arange(np.min(delay), np.max(delay), 0.1), *fit_parameters[i]))
    plt.show()

# Enlarge the STD of the window size, too small to see otherwise.
fit_parameters_std[:, 4] *= 50

labels = [
    "$N_d$",
    "$N$",
    "$\\sigma$",
    "$\\tau_0$ [ns]",
]
for i in range(0, len(labels)):
    plt.errorbar(fit_parameters[::2, 4], fit_parameters[::2, i],
                 xerr=fit_parameters_std[::2, 4], yerr=fit_parameters_std[::2, 0],
                 fmt='o', label='Shifting line A')
    plt.errorbar(fit_parameters[1::2, 4], fit_parameters[1::2, i],
                 xerr=fit_parameters_std[1::2, 4], yerr=fit_parameters_std[1::2, 0],
                 fmt='o', label='Shifting line B')
    plt.xlabel("Window size [ns]")
    plt.ylabel(labels[i])
    plt.legend()
    plt.show()

plt.errorbar(targeted_window_sizes[::2], fit_parameters[::2, 4],
             yerr=fit_parameters_std[::2, 4],
             fmt='o', label='Shifting line A')
plt.errorbar(targeted_window_sizes[1::2], fit_parameters[1::2, 4],
             yerr=fit_parameters_std[1::2, 4],
             fmt='o', label='Shifting line B')
plt.xlabel("Targeted window size [ns]")
plt.ylabel("Effective window size ($\\tau_w$) [ns]")
plt.legend()
plt.show()
