#!/bin/python3
from functools import partial
from joblib import Parallel, delayed
from eapprocessor.multi import NUM_CORES, MULTI_ENABLED
import numpy as np


def getIndexesOverListOfThresholdMaximum(array):

    step = float(max(array) / 100)
    steps = np.array(range(100)) * step
    return getIndexesOverListOfThreshold(array, steps)


def getIndexesOverListOfThreshold(array, thresholds):
    indexes = []
    count = []

    if MULTI_ENABLED:
        proc_ = partial(getSamplesOverThreshold, array=array)
        res = Parallel(n_jobs=NUM_CORES)(delayed(proc_)(th) for th in
                                         thresholds)
        indexes = [ind[0] for ind in res]
        count = [ind[1] for ind in res]

    else:
        for idx in range(len(thresholds)):
            index, value = getSamplesOverThreshold(
                threshold=thresholds[idx],
                array=array)
            indexes += [index]
            count += [len(index)]

    return indexes, count


def getSamplesOverThreshold(threshold, array):
    indexes = []
    values = []
    for idx in range(len(array)):
        if isOverThreshold(array[idx], threshold=threshold):
            indexes += [idx]
            values += [array[idx]]
    return indexes, values


def isOverThreshold(value, threshold):

    return value >= threshold


if __name__ == "__main__":

    array = [12, 0, 15, 4, 6, 19, 6, 7]

    indexes, values = getSamplesOverThreshold(array=array, threshold=15)
    print(indexes)
    print(values)
