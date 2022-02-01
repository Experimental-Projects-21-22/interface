import numpy as np


def nfft(wavelengths: np.ndarray, intensities: np.ndarray) -> np.ndarray:
    """
    Performs a discrete nfft.
    """
    reciprocal_wavelengths = 1 / wavelengths
    N = len(wavelengths)

    p = (reciprocal_wavelengths - np.min(reciprocal_wavelengths)) / (
            np.max(reciprocal_wavelengths) - np.min(reciprocal_wavelengths))
    k = np.arange(N)

    X = np.dot(intensities, np.exp(-2j * np.pi * p * k[:, None]))[: N // 2]
    X[0] = 0

    return X
