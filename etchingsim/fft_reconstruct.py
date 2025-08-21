import numpy as np


def intermeidate_curve(x1, y1, x2, y2, weigth=0.5):
    freqs1, coeffs1, z_full_1 = fourier_curve_reconstruction(x1, y1)
    freqs2, coeffs2, z_full_2 = fourier_curve_reconstruction(x2, y2)
    z_middle = reconstruct_curve(
        weigth*coeffs1 + (1 - weigth)*coeffs2, weigth*freqs1 + (1 - weigth)*freqs2, num_points=400, top_k=None)
    return z_middle.real, z_middle.imag


def dft_at_frequencies(z, freqs):
    N = len(z)
    n = np.arange(N)
    coeffs = []
    for f in freqs:
        coeffs.append(np.sum(z * np.exp(-2j * np.pi * f * n / N)) / N)
    return np.array(coeffs)


def fourier_curve_reconstruction(x: np.array, y: np.array):
    if len(y) != len(x):
        raise ValueError("x and y must have the same length")
    # Convert to complex numbers
    z = x + 1j*y
    N = len(z)
    freqs = np.linspace(-50, 50, N)
    coeffs = dft_at_frequencies(z, freqs)
    # # Apply FFT
    # coeffs = np.fft.fft(z) / N  # normalize
    # freqs = np.fft.fftfreq(N, 1/N)
    # Print first 10 coefficients for debugging
    return freqs, coeffs, reconstruct_curve(coeffs, freqs)


def reconstruct_curve(coeffs, freqs, num_points=400, top_k=None):
    """
    Reconstructs curve from Fourier basis vectors.

    coeffs : array of Fourier coefficients
    freqs  : corresponding frequencies
    num_points : number of time samples to generate
    top_k  : use only top_k largest vectors (if None, use all)
    """
    t = np.linspace(0, 1, num_points, endpoint=False)
    z_rec = np.zeros(num_points, dtype=complex)

    if top_k is not None:
        # sort indices by amplitude
        indices = np.argsort(-np.abs(coeffs))[:top_k]
    else:
        indices = range(len(coeffs))

    for i in indices:
        z_rec += coeffs[i] * np.exp(2j*np.pi*freqs[i]*t)

    return z_rec
