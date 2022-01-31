from scipy.fft import fft as sci_fft, fftfreq
import numpy as np


def fft(array, fs, only_positive=True, absolute=True):

    T = 1.0 / fs
    N = len(array)
    yf = sci_fft(array)
    xf = fftfreq(N, T)

    if (absolute):
        yf = np.abs(yf)

    if (only_positive):
        xf = xf[0:N // 2]
        yf = 2.0 / N * (yf[0:N // 2])

    return xf, yf
