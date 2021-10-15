#!/bin/python3
# from functools import partial
# from joblib import Parallel, delayed
# from eapprocessor.multi import NUM_CORES, MULTI_ENABLED
import numpy as np
import scipy.signal as scp


def get_indexes_over_threshold_list_maximum(
        array, number=100, absolute=False):

    if absolute:
        array = np.absolute(np.array(array))
    step = float(max(array) / number)
    steps = np.array(range(number)) * step
    indexes, count = get_indexes_over_threshold_list(array, steps,
                                                     absolute=absolute)
    indexes_spikes, count_spikes = get_spikes_over_threshold_list(
        array, steps, absolute=absolute)

    return indexes, count, indexes_spikes, count_spikes, steps


def get_indexes_over_threshold_list(array, thresholds, absolute=False):

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


def get_samples_over_threshold(array, threshold, absolute=False):

    array = np.array(array)
    if absolute:
        array = np.absolute(array)
    indexes = np.ones(len(array)) * \
        (is_over_threshold(array, threshold=threshold))
    values = array[np.arange(len(array))[indexes > 0]]
    return indexes, values


def is_over_threshold(value, threshold):

    return value >= threshold


def get_spikes_over_threshold_list(array, thresholds, absolute=False):

    indexes = np.array([get_spikes_over_threshold(array,
                                                  threshold=threshold,
                                                  absolute=absolute)
                        for threshold in thresholds])
    count = np.sum(indexes, axis=1)
    return indexes, count


def get_spikes_over_threshold(array, threshold, absolute=False):
    array = np.array(array)
    if absolute:
        array = np.absolute(array)
    peaks, _ = scp.find_peaks(array, height=threshold)
    indexes = np.zeros(array.shape)
    indexes[peaks] = 1
    return indexes


def get_local_maximum(array):
    array = np.array(array)
    if len(array.shape) > 1:
        local = scp.argrelmax(array, axis=1)
    else:
        local = scp.argrelmax(array)
    print(local)
    indexes = np.zeros(array.shape)
    indexes[local] = 1
    return indexes


if __name__ == "__main__":

    array = [12, 0, 15, 14, 6, 19, 6, 7]
    array = np.array(array)

    indexes, values = get_samples_over_threshold(array=array, threshold=13)
    print("Indexes over threshold", indexes)
    print("Values over threshold", values)

    indexes_spikes = get_spikes_over_threshold(array=array, threshold=13)
    print("Indexes as spikes", indexes_spikes)

    indexes_local = get_local_maximum(array * indexes)
    print("Indexes as local maximum", indexes_local)

    indexes, values = get_indexes_over_threshold_list(
        array=array, thresholds=[12, 15, 19])
    print(indexes)
    print(values)

    array_arr = np.ones(indexes.shape[0]).reshape(
        indexes.shape[0], 1) @ array.reshape(1, len(array))

    new_array = array_arr * indexes
    local_maximum = get_local_maximum(new_array)

    print(array_arr)
    print(new_array)
    print(local_maximum)

    from scipy.misc import electrocardiogram

    x = electrocardiogram()[2000:4000]

    indexes, values = get_samples_over_threshold(array=x, threshold=0)
    indexes_spikes = get_spikes_over_threshold(array=x, threshold=0)
    indexes_local = get_local_maximum(x * indexes)

    import matplotlib.pyplot as plt
    plt.plot(x)
    plt.plot(np.arange(len(x))[indexes > 0], x[indexes > 0], '.')
    plt.plot(np.arange(len(x))[indexes_spikes > 0], x[indexes_spikes > 0], 'o')
    plt.plot(np.arange(len(x))[indexes_local > 0], x[indexes_local > 0], 'x')

    thresholds = [0, 0.1, 0.2]
    indexes, _ = get_indexes_over_threshold_list(array=x,
                                                 thresholds=thresholds)
    indexes_spikes, _ = get_spikes_over_threshold_list(array=x,
                                                       thresholds=thresholds)

    fig = plt.figure()
    for idx, threshold in enumerate(thresholds):
        ax = fig.add_subplot(3, 1, idx + 1)
        plt.plot(x)
        plt.plot(np.arange(len(x))[indexes[idx] > 0],
                 x[indexes[idx] > 0], '.')
        plt.plot(np.arange(len(x))[indexes_spikes[idx] > 0],
                 x[indexes_spikes[idx] > 0], 'o')

    plt.show()
