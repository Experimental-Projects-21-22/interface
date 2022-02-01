import matplotlib
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
from seabreeze.spectrometers import Spectrometer

from utils.nfft import nfft

matplotlib.use("TkAgg")
grid = gridspec.GridSpec(2, 2)

INTEGRATION_TIME = 5000  # microseconds
N = 2048

# Data arrays
wavelengths = np.ones(N)
intensities = np.zeros(N)

# Determine values for first loop
spectrometer = Spectrometer.from_first_available()
spectrometer.integration_time_micros(INTEGRATION_TIME)

# Run the GUI loop
plt.ion()

# Create the subplots
fig = plt.figure(figsize=(10, 8))
ax1 = fig.add_subplot(grid[0, 0])
ax2 = fig.add_subplot(grid[0, 1])
ax3 = fig.add_subplot(grid[1, :])

# Draw plots for first loop
line1 = ax1.scatter(np.arange(N // 2), np.zeros(N // 2), s=3)
line2 = ax2.scatter(np.arange(N // 2), np.zeros(N // 2), s=3)
line3 = ax3.scatter(wavelengths, intensities, s=3)

# Set tiles
fig.suptitle("Details of the measured spectrum", fontsize=20)
ax1.set_title("Magnitude of the fourier transform")
# ax1.set_xlabel("Reciprocal wavelength (m$^{-1}$)")
# ax1.set_ylabel("|FT| (db)")
# ax1.set_xlim(-0.05 * np.max(freqs), 1.05 * np.max(freqs))

ax2.set_title("Phase of the fourier transform")
# ax2.set_xlabel("Reciprocal wavelength (m$^{-1}$)")
# ax2.set_ylabel("phase(FT) (rad)")
# ax2.set_xlim(-0.05 * np.max(freqs), 1.05 * np.max(freqs))
ax2.set_yticks([-np.pi, -0.5 * np.pi, 0, 0.5 * np.pi, np.pi])
ax2.set_yticklabels(['$-\pi$', '$-\pi$/2', '0', '$\pi$/2', '$\pi$', ])

ax3.set_title("Measured intensity compared to base file")
ax3.set_xlabel("Wavelength (nm)")
ax3.set_ylabel("Intensity")

plt.tight_layout()
plt.show()

while True:
    intensities = spectrometer.intensities()
    wavelengths = spectrometer.wavelengths()

    # Fixes a broken pixel?
    intensities[1] = 0

    transform = nfft(wavelengths, intensities)

    line1.set_offsets(np.c_[np.arange(N // 2), np.abs(transform)])
    line2.set_offsets(np.c_[np.arange(N // 2), np.angle(transform)])
    line3.set_offsets(np.c_[wavelengths, intensities])

    ax1.set_ylim(0, np.max(np.abs(transform)))
    ax3.set_ylim(0, np.max(np.abs(transform)))

    ax3.set_ylim(0, np.max(np.abs(intensities)))
    ax3.set_xlim(np.min(wavelengths), np.max(wavelengths))

    # drawing updated values
    fig.canvas.draw()
    fig.canvas.flush_events()
