"""
Written by:
    Douwe Remmelts <remmeltsdouwe@gmail.com>
"""
from os import listdir

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from measure.schemes.window_shift_effect import WindowShiftEffect
from utils.delays import DelayLines


def sin_fit(x, f, phi, A, b, alpha):
    return A * np.exp(-alpha * x) * np.sin(2 * np.pi * f * x + phi) + b


fit_func = WindowShiftEffect._distribution
PATH = '/Users/douweremmelts/PycharmProjects/interface_new/Data coinc'
files = listdir(PATH)
try:
    files.remove('.DS_Store')
except ValueError:
    pass

target_window = np.zeros(len(files))
restd = np.zeros(len(files))
actual_window = np.zeros(len(files))
Nd_fit = np.zeros(len(files))
Nd_theory = np.zeros(len(files))

SIN_LABELS = ['f', 'phi', 'A', 'b', 'alpha']
parameters = np.zeros((len(files), len(SIN_LABELS)))
errors = np.zeros((len(files), len(SIN_LABELS)))

for i, file in enumerate(files):
    # if i > 1:
    #     break
    metadata = np.load(PATH + '/' + file)
    data = metadata['data']
    coincidences = data[4]
    targeted_window_size = metadata['window_size']

    shift_line_C = DelayLines.CA if metadata['shift_A'] else DelayLines.CB
    fixed_line_C = DelayLines.CB if metadata['shift_A'] else DelayLines.CA

    fixed_delay = fixed_line_C.calculate_delays(metadata['fixed_delay_C'])
    delay = shift_line_C.calculate_delays(data[0, :]) - fixed_delay

    p0 = (np.min(coincidences), np.max(coincidences), 1, 0, (targeted_window_size - 11) * 2)
    try:
        popt, pcov = curve_fit(fit_func, delay, coincidences, p0=p0, maxfev=2000)
        succes = True
    except RuntimeError:
        popt = np.empty(len(p0))
        popt[:] = np.nan
        pcov = np.empty((len(p0), len(p0)))
        pcov[:] = np.nan
        succes = False
    if popt[-1] > 20:
        popt = np.empty(len(p0))
        popt[:] = np.nan
        pcov = np.empty((len(p0), len(p0)))
        pcov[:] = np.nan
        succes = False

    lin = np.linspace(delay[0], delay[-1], 500)
    counts1 = data[2]
    counts2 = data[3]

    if succes:
        fig, count_axis = plt.subplots()

        # plt.title(f"Window Shift Effect ({'A' if metadata['shift_A'] else 'B'})\n"
        #           + f"{metadata['timestamp']}"
        #           )
        plt.title(f'Targeted window size: {targeted_window_size} ns')
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
        coincidence_axis.plot(lin, fit_func(lin, *popt), label='Fit', c='r')

        # Create proper legend
        handles, labels = count_axis.get_legend_handles_labels()
        handles += coincidence_axis.get_legend_handles_labels()[0]
        labels += coincidence_axis.get_legend_handles_labels()[1]

        a, b = labels.index('Fit'), labels.index('Coincidences')
        labels[a], labels[b] = labels[b], labels[a]
        handles[a], handles[b] = handles[b], handles[a]

        plt.legend(handles, labels)
        plt.tight_layout()
        # plt.savefig('Sinc_example.pdf')
        # plt.show()
        plt.clf()
        res = coincidences - fit_func(delay, *popt)

        p0 = [1 / 5, -np.pi / 2, np.max(res), np.mean(res), 0]

        mask_parameter = 2.25 * np.std(res)
        fit_mask = np.abs(res) <= mask_parameter

        popt_sin, pcov_sin = curve_fit(sin_fit, delay[fit_mask], res[fit_mask], p0=p0)
        errors_sin = np.sqrt(np.diag(pcov_sin))

        parameters[i] = popt_sin
        errors[i] = errors_sin

        print(f'For {file}:')
        for i, value in enumerate(popt_sin):
            print(f'{SIN_LABELS[i]} = {value} ± {errors_sin[i]}')

        plt.plot(delay, res, '-o')
        plt.plot(lin, sin_fit(lin, *popt_sin))
        plt.xlabel('Relative delay [ns]')
        plt.ylabel('Residue counts')
        plt.hlines(mask_parameter, delay[0], delay[-1])
        plt.hlines(-mask_parameter, delay[0], delay[-1])
        # plt.ylim(-1.1*np.abs(popt_sin[2]) + popt_sin[3], 1.1*np.abs(popt_sin[2]) + popt_sin[3])
        plt.grid(alpha=.4)
        plt.title('Residue of coincidence counts compared to the fit\n'
                  f'Targeted window size: {targeted_window_size} ns')
        plt.tight_layout()
        # plt.savefig('res_example.pdf')
        plt.show()

    else:
        parameters[i, :] = np.nan
        errors[i, :] = np.nan

    # target_window[i] = targeted_window_size
    # actual_window[i] = popt[-1]
    # restd[i] = np.std(res)
    # Nd_fit[i] = popt[0]
    # Nd_theory[i] = np.mean(counts1) * np.mean(counts2) * popt[-1] * 2e-9

print(np.nanmean(parameters, axis=0), np.nanmean(errors, axis=0) / np.sqrt(len(files)))
print(np.nanstd(parameters, axis=0))
