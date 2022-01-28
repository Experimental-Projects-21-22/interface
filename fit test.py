import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from utils.delays import DelayLines
from scipy.special import erf
from os import listdir


def fit_func(time_diff, amp, sigma, window, horizontal_offset, background):
    return background + amp * sigma * (erf((time_diff + window - 2 * horizontal_offset) / (2 * sigma))
                                       - erf((time_diff - window - 2 * horizontal_offset) / (2 * sigma)))


def lin_func(x, a, b):
    return a * x + b


path = '/Users/douweremmelts/PycharmProjects/interface_new/Data coinc'
parameter_names = ['Amplitude', 'sigma', 'window size', 'horizontal offset', 'background counts']

num_of_files = len(listdir(path))
values = {}
sigmas = {}
for i in parameter_names:
    values[i] = np.zeros(num_of_files)
    sigmas[i] = np.zeros(num_of_files)

theoretical_lengths = np.zeros(num_of_files)
for j, file in enumerate(listdir(path)):
    metadata = np.load(path + '/' + file)
    counts = metadata['data'][4]

    if metadata['shift_A']:
        shift_line_C = DelayLines.CA
        fixed_line_C = DelayLines.CB
    else:
        shift_line_C = DelayLines.CB
        fixed_line_C = DelayLines.CA

    delay = shift_line_C.calculate_delays(metadata['data'][0, :]) - fixed_line_C.calculate_delays(
        metadata['fixed_delay_C'])

    p0 = [np.max(counts), 1, 2, 0, 0]
    title = file + '\n'
    fig, ax = plt.subplots()
    try:
        popt, pcov = curve_fit(fit_func, delay, counts, p0=p0, maxfev=2000)
        errors = np.sqrt(np.diag(pcov))
        lin = np.linspace(delay[0], delay[-1], 100)
        ax.plot(lin, fit_func(lin, *popt))
        for i in range(5):
            values[parameter_names[i]][j] = popt[i]
            sigmas[parameter_names[i]][j] = errors[i]
            title += f'{parameter_names[i]} = {popt[i]:.3} ± {errors[i]:.1} '
            if i % 2 == 1:
                title += '\n'
    except RuntimeError:
        print(f'Error bij {file}')
    ax.scatter(delay, counts)
    ax.set_title(title)
    ax.set_xlabel('Delay (ns)')
    ax.set_ylabel('Coincidence counts')
    ax.grid(alpha=.4)
    fig.tight_layout()
    fig.savefig(f'/Users/douweremmelts/PycharmProjects/interface_new/utils/Plotjes/{file}.pdf')
    fig.show()

    theoretical_lengths[j] = metadata['window_size']

mask = ~((theoretical_lengths == 11) * (values['window size'] > 1))

# popt, pcov = curve_fit(lin_func, theoretical_lengths[mask], lengths[mask])
# lin = np.linspace(np.min(theoretical_lengths), np.max(theoretical_lengths), 100)
# print(popt, np.sqrt(np.diag(pcov)))
# plt.errorbar(theoretical_lengths, lengths, sigma_l, fmt='o')
# plt.plot(lin, lin_func(lin, *popt))
# plt.xlabel('Input window size')
# plt.ylabel('Fitted window size')
# plt.title('Input window size vs. fitted window size')
# plt.grid(alpha=.4)
# plt.show()

for i in parameter_names:
    plt.errorbar(theoretical_lengths, values[i], sigmas[i], fmt='o')
    plt.xlabel('Input window size (ns)')
    plt.ylabel(i)
    plt.title(f'Input window size vs {i}')
    plt.grid(alpha=.4)
    plt.show()
