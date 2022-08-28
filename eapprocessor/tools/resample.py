from scipy import interpolate
from scipy import signal
import numpy as np


def resample(x, y, X_new, kind):
    f = interpolate.interp1d(x, y, kind=kind)
    return f(X_new)


def decimate(x, y, factor):
    y_new = signal.decimate(y, factor)
    x_new = np.linspace(x[0], x[-1], int(len(x) / factor), endpoint=False)
    return x_new, y_new
