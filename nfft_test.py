import numpy as np
from matplotlib import pyplot as plt

wavelengths = np.arange(350, 500, 1)
reciprocal_wavelengths = 1 / wavelengths
N = len(wavelengths)

p = (reciprocal_wavelengths - np.min(reciprocal_wavelengths)) / (
        np.max(reciprocal_wavelengths) - np.min(reciprocal_wavelengths))
k = np.arange(N)

for dL in np.linspace(5000, 10000, 5):
    intensities = np.square(np.cos(2 * np.pi * dL * reciprocal_wavelengths))

    X_k = np.dot(intensities, np.exp(-2j * np.pi * p * k[:, None]))[: N // 2]
    X_k[0] = 0

    plt.plot(k[: N // 2], np.abs(X_k))
plt.show()
