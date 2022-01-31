#!/bin/python3
import numpy as np
from typing import Union, List, Tuple, Iterable, Callable


def normalize(array: Union[List[float], np.ndarray],
              resolution: int, bipolar: bool = False) -> np.ndarray:
    """Normalize values in array.

    :param array: array input
    :type array: Union[List[float], np.ndarray]
    :param resolution: resolution to max values
    :type resolution: int
    :param bipolar: type of adc
    :type bipolar: bool
    :return: normalized array
    :rtype: np.ndarray
    """

    max_values = 2**resolution
    if bipolar:
        normalized = 2 * np.array(array) / max_values - 1
    else:
        normalized = np.array(array) / max_values

    return normalized


def convert_lcadc(array: Union[List[float],
                               np.ndarray],
                  voltage_ref: float,
                  resolution: int,
                  bipolar: bool = False,
                  verbose: bool = False,
                  operator: Callable[[float], int] = int) -> Tuple[Iterable,
                                                                   Iterable]:
    """Convert array to numeric values with LCADC model

    :param array: array of float values
    :type array: Union[List[float], np.ndarray]
    :param voltage_ref: reference for converter
    :type voltage_ref: float
    :param resolution: resolution for converter
    :type resolution: int
    :param bipolar: type of converter
    :type bipolar: bool
    :return: array of converted values
    :rtype: Tuple[List[int], List[float]]
    """
    newarray = []
    indexes = []
    max_windows = 2**resolution
    if bipolar:
        step = float(2 * voltage_ref / max_windows)
    else:
        step = float(voltage_ref / max_windows)

    latest_ref = 0
    for idx, item in enumerate(array):
        if(verbose):
            print(f"value:{item}, latest ref: {latest_ref}, step:{step}")
        if(idx == 0 or (np.abs(item - latest_ref) >= step)):

            if(idx == 0):
                newarray += [
                    quantize(
                        item -
                        latest_ref,
                        voltage_ref=voltage_ref,
                        resolution=resolution,
                        bipolar=bipolar,
                        operator=operator)]
            else:
                value = quantize(
                    item -
                    latest_ref,
                    voltage_ref=2 * voltage_ref,
                    resolution=resolution,
                    bipolar=False,
                    operator=operator)
                if(verbose):
                    print(f"Append value:{value}")
                newarray += [
                    newarray[-1] + value
                ]

            indexes += [idx]
            latest_ref = dac(newarray[-1], voltage_ref=voltage_ref,
                             resolution=resolution, bipolar=bipolar)
            # print(latest_ref)

    return np.array(indexes), np.array(newarray)


def convert_array(array: Union[List[float], np.ndarray],
                  voltage_ref: float,
                  resolution: int,
                  bipolar: bool = False,
                  operator: Callable[[float], int] = int) -> np.ndarray:
    """Convert array to numeric values with classic SAR model

    :param array: array of float values
    :type array: Union[List[float], np.ndarray]
    :param voltage_ref: reference for converter
    :type voltage_ref: float
    :param resolution: resolution for converter
    :type resolution: int
    :param bipolar: type of converter
    :type bipolar: bool
    :return: array of converted values
    :rtype: Tuple[List[int], List[float]]
    """
    return np.array([quantize(x,
                              voltage_ref=voltage_ref,
                              resolution=resolution,
                              bipolar=bipolar,
                              operator=operator) for x in array])


def dac(value: Union[List[int], np.ndarray, int],
        voltage_ref: float,
        resolution: int,
        bipolar: bool = False) -> float:
    """Convert to analog value from digital

    :param value: Numeric value to be converted to float
    :type value: int
    :param voltage_ref: Reference for converter
    :type voltage_ref: float
    :param resolution: Resolution for converter
    :type resolution: int
    :param bipolar: Type of converter
    :type bipolar: bool
    :return: Floating value
    :rtype: float
    """

    if isinstance(value, (list, np.ndarray)):
        return np.array([dac(element, voltage_ref, resolution, bipolar)
                         for element in value])

    max_values = 2**resolution
    if bipolar:
        step = float(2 * voltage_ref / max_values)
        analog = float((value * step) - voltage_ref)
    else:
        step = float(voltage_ref / max_values)
        analog = float(value * step)

    return analog


def quantize(value: float,
             voltage_ref: float,
             resolution: int,
             bipolar: bool = False,
             operator: Callable[[float], int] = int) -> int:
    """Quantize value from analog to digital.

    :param value: Floating value to be converted
    :type value: float
    :param voltage_ref: Reference for quantization
    :type voltage_ref: float
    :param resolution: Resolution for quantization
    :type resolution: int
    :param bipolar: Type of quantization
    :type bipolar: bool
    :return: Numeric value corresponding to floating value
    :rtype: int
    """

    max_values = 2**resolution
    if bipolar:
        step = float(2 * voltage_ref / max_values)
        quantized = operator((value + voltage_ref) / step)
    else:
        step = float(voltage_ref / max_values)
        quantized = operator(value / step)
    return quantized


if __name__ == "__main__":

    import matplotlib.pylab as plt
    time = np.linspace(0, 1, 1000)
    signal = np.sin(2 * np.pi * time)
    quantized = convert_array(signal, 1, 4, bipolar=True)
    indexes, lcadc = convert_lcadc(signal, 1, 4, bipolar=True)

    normalized = normalize(quantized, 4, bipolar=True)

    print(indexes)
    print(lcadc)

    plt.plot(time, signal)
    plt.plot(time, quantized)
    plt.plot(time, normalized)
    plt.plot(time[indexes], lcadc)
    plt.show()
