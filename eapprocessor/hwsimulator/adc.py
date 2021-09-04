#!/bin/python3
import numpy as np


def normalize(array, resolution, bipolar=False):

    max_values = 2**resolution
    if bipolar:
        normalized = 2 * np.array(array) / max_values - 1
    else:
        normalized = np.array(array) / max_values

    return normalized


def convertLCADC(array, voltage_ref, resolution, bipolar=False):
    newarray = []
    indexes = []
    max_windows = 2**resolution
    if bipolar:
        step = float(2 * voltage_ref / max_windows)
    else:
        step = float(voltage_ref / max_windows)

    latest_ref = 0
    for idx in range(len(array)):
        if(idx == 0 or (np.abs(array[idx] - latest_ref) >= step)):
            newarray += [quantize(array[idx], voltage_ref=voltage_ref,
                                  resolution=resolution, bipolar=bipolar)]
            indexes += [idx]
            latest_ref = dac(newarray[-1], voltage_ref=voltage_ref,
                             resolution=resolution, bipolar=bipolar)
            # print(latest_ref)

    return indexes, newarray


def convertArray(array, voltage_ref, resolution, bipolar=False):
    return np.array([quantize(x,
                              voltage_ref=voltage_ref,
                              resolution=resolution,
                              bipolar=bipolar) for x in array])


def dac(value, voltage_ref, resolution, bipolar=False):

    max_values = 2**resolution
    if bipolar:
        step = float(2 * voltage_ref / max_values)
        analog = float((value * step) - voltage_ref)
    else:
        step = float(voltage_ref / max_values)
        analog = float(value * step)

    return analog


def quantize(value, voltage_ref, resolution, bipolar=False):

    max_values = 2**resolution
    if bipolar:
        step = float(2 * voltage_ref / max_values)
        quantized = int((value + voltage_ref) / step)
    else:
        step = float(voltage_ref / max_values)
        quantized = int(value / step)
    return quantized


if __name__ == "__main__":

    import matplotlib.pylab as plt
    time = np.linspace(0, 1, 1000)
    signal = np.sin(2 * np.pi * time)
    quantized = convertArray(signal, 1, 4, bipolar=True)
    indexes, lcadc = convertLCADC(signal, 1, 4, bipolar=True)

    normalized = normalize(quantized, 4, bipolar=True)

    print(indexes)
    print(lcadc)

    plt.plot(time, signal)
    plt.plot(time, quantized)
    plt.plot(time, normalized)
    plt.plot(time[indexes], lcadc)
    plt.show()
