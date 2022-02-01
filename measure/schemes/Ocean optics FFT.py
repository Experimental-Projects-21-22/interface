import numpy as np
import time
import matplotlib
import matplotlib.pyplot as plt
from seabreeze.spectrometers import Spectrometer
from nfft import nfft
import matplotlib.gridspec as gridspec


def to_DB(FFT):
    return 20 * np.log10(np.abs(FFT))


def random_data(constant_intensity, dL):
    data = constant_intensity * (0.3 + 0.7 * (np.cos(2 * np.pi * dL / wavelengths) ** 2))
    # data += 5 * np.random.random(len(constant_intensity))
    return data


def create_inverse_mask(array):
    # VERY roughly creates a inversely spaced mask
    # CANNOT STRESS ENOUGH HOW ROUGH THIS IS
    # THIS WAS MADE AT 3AM
    inversed_array = np.flip(1/array)
    diff_array = np.diff(inversed_array)
    dx = diff_array[0]

    mask = np.zeros(len(array), dtype=bool)
    mask[0] = True
    n = 1
    for i, diff in enumerate(diff_array):
        if diff >= n * dx:
            mask[i] = True
            n += 1

    return mask


matplotlib.use("TkAgg")
gs = gridspec.GridSpec(2, 2)

RANDOM = False
INTEGRATION_TIME = 5000  # microseconds
STANDARD_FILE = '/Users/douweremmelts/PycharmProjects/interface_new/niet-GEBLOKT.txt'
BASE_INTENSITY = np.loadtxt(STANDARD_FILE, delimiter='\t')[:, 1][:-1]

# Determine values for first loop
if not RANDOM:
    spec = Spectrometer.from_first_available()
    spec.integration_time_micros(INTEGRATION_TIME)
    wavelenghts = spec.wavelengths()
    intensity = spec.intensities()
else:
    # wavelengths = np.loadtxt('/Users/douweremmelts/PycharmProjects/interface_new/niet-GEBLOKT.txt', delimiter='\t')[:,
    #               0][:-1]
    # niet_geblokt = np.loadtxt('/Users/douweremmelts/PycharmProjects/interface_new/niet-GEBLOKT.txt', delimiter='\t')[:,
    #                1][:-1]
    wavelengths = np.linspace(50, 100, 1000)
    # Delta_L = np.logspace(3, 4, 200)
    Delta_L = np.linspace(1, 8, 100)
    BASE_INTENSITY = np.ones(len(wavelengths))
    intensity = np.sin(2/np.max(wavelengths) * 1 * np.pi * wavelengths)


# wavelengths_inversely = 1/np.linspace(0, 1, len(wavelengths)+1)[1:]
# FFT = np.fft.fft(intensity)
FFT = nfft(wavelengths, intensity)
freqs = np.fft.fftfreq(len(wavelengths), np.mean(np.diff(wavelengths)))
positive_mask = freqs >= 0

# Run the GUI loop
plt.ion()

# Create the subplots
fig = plt.figure(figsize=(10, 8))
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[1, 0])
ax3 = fig.add_subplot(gs[:, 1])

# Draw plots for first loop
line1 = ax1.scatter(freqs[positive_mask], to_DB(FFT[positive_mask]), s=3)
line2 = ax2.scatter(freqs[positive_mask], np.angle(FFT[positive_mask]), s=3)
line3 = ax3.scatter(wavelengths, intensity / BASE_INTENSITY)

# Set tiles
fig.suptitle("Details of the measured spectrum", fontsize=20)
ax1.set_title("Magnitude of the fourier transform")
ax1.set_xlabel("Reciprocal wavelength (m$^{-1}$)")
ax1.set_ylabel("|FT| (db)")
ax1.set_xlim(-0.05 * np.max(freqs), 1.05 * np.max(freqs))

ax2.set_title("Phase of the fourier transform")
ax2.set_xlabel("Reciprocal wavelength (m$^{-1}$)")
ax2.set_ylabel("phase(FT) (rad)")
ax2.set_xlim(-0.05 * np.max(freqs), 1.05 * np.max(freqs))
ax2.set_yticks([-np.pi, -0.5 * np.pi, 0, 0.5 * np.pi, np.pi])
ax2.set_yticklabels(['$-\pi$', '$-\pi$/2', '0', '$\pi$/2', '$\pi$', ])

ax3.set_title("Measured intensity compared to base file")
ax3.set_xlabel("Wavelength (nm)")
ax3.set_ylabel("Relative intensity")

plt.tight_layout()
plt.show()
print(np.max(freqs))
# Loop

while 1==1:
    # Measure new values
    if not RANDOM:
        intensity = spec.intensities()
    else:
        # intensity = random_data(niet_geblokt, dL)
        intensity = np.sin(2/np.max(wavelengths) * dL * np.pi * wavelengths)

    FFT = np.fft.fft(intensity)
    # FFT = nfft(wavelengths_inversely, intensity, len(intensity))
    # Update plot
    dB = to_DB(FFT[positive_mask])
    rel = intensity/BASE_INTENSITY
    line1.set_offsets(np.c_[freqs[positive_mask], dB])
    line2.set_offsets(np.c_[freqs[positive_mask], np.angle(FFT[positive_mask])])
    line3.set_offsets(np.c_[wavelengths, rel])

    ax1.set_ylim(-0.05*np.min(dB), 1.05*np.max(dB))
    ax3.set_ylim(-0.05*np.min(rel), 1.05*np.max(rel))

    # drawing updated values
    fig.canvas.draw()
    fig.canvas.flush_events()

# plt.plot(1/wavelengths, intensity)
# plt.show()
