import numpy as np
import time
import matplotlib
import matplotlib.pyplot as plt
from seabreeze.spectrometers import Spectrometer

matplotlib.use("TkAgg")

RANDOM = False
INTEGRATION_TIME = 5000  # microseconds

# Determine values for first loop
if not RANDOM:
    spec = Spectrometer.from_first_available()
    spec.integration_time_micros(INTEGRATION_TIME)
    wavelenghts = spec.wavelengths()
    intensity = spec.intensities()
else:
    wavelengths = np.linspace(0, 50, 1000)
    intensity = np.sin(2 * np.pi * wavelengths)

FFT = np.fft.fft(intensity)
freqs = np.fft.fftfreq(len(wavelengths), np.mean(np.diff(wavelengths)))
positive_mask = freqs >= 0

# Run the GUI loop
plt.ion()

# Create the subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Draw plots for first loop
line1 = ax1.scatter(freqs[positive_mask], np.abs(FFT[positive_mask]))
line2 = ax2.scatter(freqs[positive_mask], np.angle(FFT[positive_mask]))

# Set tiles
fig.suptitle("Fourier transform of the measured spectrum", fontsize=20)
ax1.set_title("Magnitude of the fourier transform")
ax1.set_xlabel("Reciprocal wavelength (m$^{-1}$)")
ax1.set_ylabel("|FT|")
ax1.set_xlim(-0.05 * np.max(freqs), 1.05 * np.max(freqs))

ax2.set_title("Phase of the fourier transform")
ax2.set_xlabel("Reciprocal wavelength (m$^{-1}$)")
ax2.set_ylabel("phase(FT) (rad)")
ax2.set_xlim(-0.05 * np.max(freqs), 1.05 * np.max(freqs))
ax2.set_yticks([-np.pi, -0.5 * np.pi, 0, 0.5 * np.pi, np.pi])
ax2.set_yticklabels(['$-\pi$', '$-\pi$/2', '0', '$\pi$/2', '$\pi$', ])

plt.tight_layout()
print(np.max(freqs))
# Loop
while 1==1:
    # Measure new values
    if not RANDOM:
        intensity = spec.intensities()
    else:
        intensity = np.random.rand(len(wavelengths))
    FFT = np.fft.fft(intensity)

    # Update plot
    line1.set_offsets(np.c_[wavelengths[positive_mask], np.abs(FFT[positive_mask])])
    line2.set_offsets(np.c_[wavelengths[positive_mask], np.angle(FFT[positive_mask])])

    # drawing updated values
    fig.canvas.draw()
    fig.canvas.flush_events()
