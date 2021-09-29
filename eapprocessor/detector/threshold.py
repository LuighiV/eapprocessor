#!/bin/python3
# from functools import partial
# from joblib import Parallel, delayed
# from eapprocessor.multi import NUM_CORES, MULTI_ENABLED
import numpy as np


def getIndexesOverListOfThresholdMaximum(array, number=100, absolute=False):

    if absolute:
        array = np.absolute(np.array(array))
    step = float(max(array) / number)
    steps = np.array(range(number)) * step
    indexes, count = getIndexesOverListOfThreshold(array, steps,
                                                   absolute=absolute)
    return indexes, count, steps


def getIndexesOverListOfThreshold(array, thresholds, absolute=False):

    array = np.array(array)
    if absolute:
        array = np.absolute(array)
    arr = np.reshape(array, (1, len(array)))
    th = np.reshape(np.array(thresholds), (len(thresholds), 1))
    arr_expanded = np.ones(th.shape) @ arr
    th_expanded = th @ np.ones(arr.shape)

    indexes = (arr_expanded >= th_expanded) * np.ones(arr_expanded.shape)
    count = np.sum(indexes, axis=1)
    del arr_expanded
    del th_expanded

    return indexes, count


def getSamplesOverThreshold(threshold, array, absolute=False):

    array = np.array(array)
    if absolute:
        array = np.absolute(array)
    indexes = np.ones(len(array)) * \
        (isOverThreshold(array, threshold=threshold))
    values = array[np.arange(len(array))[indexes > 0]]
    return indexes, values


def isOverThreshold(value, threshold):

    return value >= threshold


if __name__ == "__main__":

    array = [12, 0, 15, 4, 6, 19, 6, 7]

    indexes, values = getSamplesOverThreshold(array=array, threshold=15)
    # print(indexes)
    # print(values)

    indexes, values = getIndexesOverListOfThreshold(array=array,
                                                    thresholds=[12, 15, 19])

    print(indexes)
    print(values)
