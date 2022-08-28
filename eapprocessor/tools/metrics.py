import numpy as np


def calculate_snr(yf):
    peak_index = np.argmax(yf)
    noise = np.delete(yf, np.array([0, peak_index]), None)
    pw_signal = yf[peak_index]**2
    pw_noise = np.sum(np.power(noise, 2))
    return 10 * np.log10(pw_signal / pw_noise)


def calculate_enob(snr):
    return (snr - 1.76) / 6.02
