import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from utils.delays import DelayLines
from scipy.special import erf
from os import listdir
import matplotlib.patches as mpl_patches


def fit_func(time_diff, amp, sigma, window, horizontal_offset, background):
    return background + amp / 2 * (erf((time_diff + window - 2 * horizontal_offset) / (np.sqrt(2) * sigma))
                                   - erf((time_diff - window - 2 * horizontal_offset) / (np.sqrt(2) * sigma)))


def lin_func(x, a, b):
    return a * x + b


PATH = '/Users/douweremmelts/PycharmProjects/interface_new/Data coinc'
PARAMETER_NAMES = ['$A$', '$\sigma$', '$L$', '$\\tau_0$', '$N_0$']
UNITS = ['', ' ns', ' ns', ' ns', '']
PLOT_FITS = False
PLOT_PARAMETERS = True

num_of_files = len(listdir(PATH))
values = {}
sigmas = {}
for i in PARAMETER_NAMES:
    values[i] = np.zeros(num_of_files)
    sigmas[i] = np.zeros(num_of_files)

theoretical_lengths = np.zeros(num_of_files)
handles = [mpl_patches.Rectangle((0, 0), 1, 1, fc="white", ec="white",
                                 lw=0, alpha=0)] * len(PARAMETER_NAMES)

for j, file in enumerate(listdir(PATH)):
    metadata = np.load(PATH + '/' + file)
    counts = metadata['data'][4]
    success = False

    if metadata['shift_A']:
        shift_line_C = DelayLines.CA
        fixed_line_C = DelayLines.CB
    else:
        shift_line_C = DelayLines.CB
        fixed_line_C = DelayLines.CA

    delay = shift_line_C.calculate_delays(metadata['data'][0, :]) - fixed_line_C.calculate_delays(
        metadata['fixed_delay_C'])

    p0 = [np.max(counts), 1, 2, 0, 0]
    title = f"Coincidence counts vs relative delay\nwith input window length = {metadata['window_size']} ns\n"
    if PLOT_FITS:
        fig, ax = plt.subplots()
        lines = []
    try:
        popt, pcov = curve_fit(fit_func, delay, counts, p0=p0, maxfev=2000)
        errors = np.sqrt(np.diag(pcov))
        parameters = []
        for i in range(5):
            values[PARAMETER_NAMES[i]][j] = np.abs(popt[i])
            sigmas[PARAMETER_NAMES[i]][j] = errors[i]
            parameters.append(f'{PARAMETER_NAMES[i]} = {popt[i]:.3} ± {errors[i]:.1}{UNITS[i]}')
        if PLOT_FITS:
            lin = np.linspace(delay[0], delay[-1], 100)
            ax.plot(lin, fit_func(lin, *popt), label='Fit')
            legend1 = ax.legend(handles, parameters, handlelength=0, handletextpad=0)
            legend1.set_title("Fit parameters", prop={'weight': 'bold'})
            legend1._legend_box.align = "left"
        success = True
    except RuntimeError:
        print(f'Error bij {file}')
    if PLOT_FITS:
        ax.scatter(delay, counts, label='Coincidence counts')
        ax.set_title(title)
        ax.set_xlabel('Delay (ns)')
        ax.set_ylabel('Coincidence counts')
        ax.grid(alpha=.4)
        legend2 = ax.legend(loc='upper left')
        if success:
            ax.add_artist(legend1)
        fig.tight_layout()
        fig.savefig(f'/Users/douweremmelts/PycharmProjects/interface_new/utils/Plotjes/{file}.pdf')
        fig.show()

    theoretical_lengths[j] = metadata['window_size']

# mask = ~((theoretical_lengths == 11) * (values['$L$'] > 1))
mask = ~(theoretical_lengths == 11)

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
if PLOT_PARAMETERS:
    for j, i in enumerate(PARAMETER_NAMES):
        plt.errorbar(theoretical_lengths[mask], values[i][mask], sigmas[i][mask], fmt='o')
        plt.xlabel('Input window size (ns)')
        if UNITS[j] != '':
            unit = f' ({UNITS[j][1:]})'
        else:
            unit = ''
        plt.ylabel(f'{i}{unit}')
        plt.title(f'Input window size vs {i}')
        plt.grid(alpha=.4)
        plt.savefig(f'/Users/douweremmelts/PycharmProjects/interface_new/utils/Plotjes/{i}.pdf')
        plt.show()
