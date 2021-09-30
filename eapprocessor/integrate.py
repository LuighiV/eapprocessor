#!/bin/python3
import numpy as np

# from functools import partial
# from joblib import Parallel, delayed
# from eapprocessor.multi import NUM_CORES, MULTI_ENABLED

from eapprocessor.mearec.api import load_recordings
from eapprocessor.hwsimulator.adc import convertArray, convertLCADC, normalize
from eapprocessor.preprocessor.neo import applyNEOToArray
from eapprocessor.detector.threshold \
    import getIndexesOverListOfThresholdMaximum


def convertADCRecordings(dataset, voltage_ref, resolution):

    arrays = dataset[:, :].T

    converted = [
        convertArray(array,
                     voltage_ref=voltage_ref,
                     resolution=resolution,
                     bipolar=True) for array in arrays]

    saveconverted = np.array(converted)
    return saveconverted


def convertLCADCRecordings(dataset, voltage_ref, resolution):

    arrays = dataset[:, :].T

    converted = []
    indexes = []
    for array in arrays:
        index, convert = convertLCADC(array, voltage_ref=voltage_ref,
                                      resolution=resolution,
                                      bipolar=True)
        converted += [convert]
        indexes += [index]

    print(f'Lenght of converted { len(converted) }')
    print(f'Lenght of indexes { len(indexes) }')
    saveindexes = np.array(indexes, dtype=object)
    saveconverted = np.array(converted, dtype=object)
    return saveindexes, saveconverted


def normalizeArrays(arrays, resolution):

    normalized = [
        normalize(
            array,
            resolution=resolution,
            bipolar=True) for array in arrays]
    return np.array(normalized)


def applyNEOToDataset(dataset, w=1):

    preprocessed = [
        applyNEOToArray(array, w=w) for array in dataset]

    saveconverted = np.array(preprocessed)
    return saveconverted


def evaluateThresHoldMaximum(dataset, number=100, absolute=False):

    listidx = []
    counts = []
    ths = []
    total = len(dataset)
    i = 1
    print("Start processing dataset...")
    # if MULTI_ENABLED:
    #     res = Parallel(n_jobs=NUM_CORES)(
    #         delayed(getIndexesOverListOfThresholdMaximum)(array) for array in
    #         dataset)
    #     listidx = [ind[0] for ind in res]
    #     counts = [ind[1] for ind in res]

    # else:
    for array in dataset:
        indexes, count, th = getIndexesOverListOfThresholdMaximum(
            array, number=number, absolute=absolute)
        listidx += [indexes]
        counts += [count]
        ths += [th]
        print(f"Processed threshold {i}/{total} in dataset")
        i += 1

    return listidx, counts, ths


def evaluateThresHoldMaximumArray(arrDataset, number=100, absolute=False):

    listidx = []
    counts = []
    ths = []
    total = len(arrDataset)
    i = 1
    for dataset in arrDataset:
        indexes, count, th = evaluateThresHoldMaximum(dataset, number=number,
                                                      absolute=absolute)
        listidx += [indexes]
        counts += [count]
        ths += [th]
        print(f"Processed dataset {i}/{total} in array of dataset")
        i += 1

    return listidx, counts, ths


if __name__ == "__main__":

    print("Acquiring latest recordings")
    recgen = load_recordings()

    recordings = recgen.recordings[:, :].T
    print("Converting with normal ADC")
    adc = convertADCRecordings(
        recgen.recordings,
        voltage_ref=1000,
        resolution=12)

    print("Normalizing...")
    normalized = normalizeArrays(adc, resolution=12)

    # print("Converting with LCADC")
    # indexes, lcadc = convertLCADCRecordings(recgen.recordings,
    #                                         voltage_ref=1000,
    #                                         resolution=12)

    print("Applying NEO preprocessor")
    w = [1, 2, 4, 8, 16]
    neoadc = [applyNEOToDataset(normalized, cw) for cw in w]

    time = recgen.timestamps[:]
    spiketrains = recgen.spiketrains

    # Plotting
    import matplotlib.pylab as plt

    fig = plt.figure()
    axes = fig.subplots(nrows=3, ncols=1)

    # for idx in range(len(axes)):
    #     axes[idx].plot(time, normalized[idx], label="ADC normalized")
    #     axes[idx].plot(time, neoadc[idx], label="NEO")

    #     level = max(normalized[idx])
    #     for spikes in spiketrains:
    #         axes[idx].plot(spikes, level * np.ones(len(spikes)), '+',
    #                        color='red')

    #     axes[idx].legend()

    axes[0].plot(time, recordings[0], label="Original signal", color='blue')
    axes[1].plot(time, normalized[0], label="ADC normalized", color='green')
    axes[2].plot(time, neoadc[0][0], label="NEO", color='orange')

    axes[0].legend()
    axes[1].legend()
    axes[2].legend()

    fig2 = plt.figure()
    axes2 = fig2.subplots(nrows=len(w), ncols=1)

    for idx in range(len(axes2)):
        axes2[idx].plot(
            time,
            neoadc[idx][0],
            label=f'With w={w[idx]}')
        axes2[idx].legend()

    plt.show()
