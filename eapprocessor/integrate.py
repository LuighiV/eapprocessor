#!/bin/python3
from typing import Tuple, Union
import numpy as np
import numpy.typing as npt

# from functools import partial
# from joblib import Parallel, delayed
# from eapprocessor.multi import NUM_CORES, MULTI_ENABLED

from eapprocessor.mearec.api import load_recordings
from eapprocessor.hwsimulator.adc \
    import convert_array, convert_lcadc, normalize
from eapprocessor.preprocessor.neo import apply_neo_to_array
from eapprocessor.detector.threshold \
    import getIndexesOverListOfThresholdMaximum


def convert_adc_recordings(
        dataset: npt.NDArray[np.float64],
        voltage_ref: float,
        resolution: int) -> npt.NDArray[np.float64]:
    """Convert array of recordings to digital values.

    :param dataset: array of recordings, shape length 2 [channel[recordings]]
    :type dataset: npt.NDArray[np.float64]
    :param voltage_ref: reference to convert recordings
    :type voltage_ref: float
    :param resolution: resolution for conversion
    :type resolution: int
    :return: Array of converted values
    :rtype: npt.NDArray[np.float64]
    """

    arrays = dataset[:, :].T

    converted = [
        convert_array(array,
                      voltage_ref=voltage_ref,
                      resolution=resolution,
                      bipolar=True) for array in arrays]

    saveconverted = np.array(converted)
    return saveconverted


def convert_lcadc_recordings(
        dataset: npt.NDArray[np.float64],
        voltage_ref: float,
        resolution: int) -> Tuple[npt.NDArray[np.object_],
                                  npt.NDArray[np.object_]]:
    """Convert array of recordings with LCADC technique

    :param dataset: array of recordings converted via LCADC,
        shape length 2 [channel[recordings]]
    :type dataset: npt.NDArray[np.float64]
    :param voltage_ref: reference to convert recordings
    :type voltage_ref: float
    :param resolution: resolution for conversion
    :type resolution: int
    :return: Array of converted values and indexes
    :rtype: Tuple[npt.NDArray[np.object_],
                                      npt.NDArray[np.object_]]
    """

    arrays = dataset[:, :].T

    converted = []
    indexes = []
    for array in arrays:
        index, convert = convert_lcadc(array, voltage_ref=voltage_ref,
                                       resolution=resolution,
                                       bipolar=True)
        converted += [convert]
        indexes += [index]

    print(f'Lenght of converted { len(converted) }')
    print(f'Lenght of indexes { len(indexes) }')
    saveindexes = np.array(indexes, dtype=object)
    saveconverted = np.array(converted, dtype=object)
    return saveindexes, saveconverted


def normalize_arrays(arrays: Union[npt.NDArray[np.float64],
                                   npt.NDArray[np.object_]],
                     resolution: int) -> npt.NDArray[np.float64]:
    """Normalize array of array of converted values

    :param arrays: Array of array of converted values, dimension length 2
        [channel[converted]]
    :type arrays: npt.NDArray[np.float64]
    :param resolution: resolution with those were converted
    :type resolution: int
    :return: array of array of normalized values [channel[normalized]]
    :rtype: npt.NDArray[np.float64]
    """

    normalized = [
        normalize(
            array,
            resolution=resolution,
            bipolar=True) for array in arrays]
    return np.array(normalized)


def apply_neo_to_dataset(dataset, w=1):

    print("Applying neo to dataset with w=", w)
    preprocessed = [
        apply_neo_to_array(array, w=w) for array in dataset]

    saveconverted = np.array(preprocessed)
    return saveconverted


def evaluate_threshold_maximum(dataset, number=100, absolute=False):

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


def evaluate_threshold_maximum_array(arrDataset, number=100, absolute=False):

    listidx = []
    counts = []
    ths = []
    total = len(arrDataset)
    i = 1
    for dataset in arrDataset:
        indexes, count, th = evaluate_threshold_maximum(dataset, number=number,
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

    recordings = np.array([])
    if recgen.recordings is not None:
        recordings = recgen.recordings[:, :].T

    print("Converting with normal ADC")
    adc = convert_adc_recordings(
        recordings,
        voltage_ref=1000,
        resolution=12)

    print("Normalizing...")
    normalized = normalize_arrays(adc, resolution=12)

    # print("Converting with LCADC")
    # indexes, lcadc = convertLCADCRecordings(recgen.recordings,
    #                                         voltage_ref=1000,
    #                                         resolution=12)

    print("Applying NEO preprocessor")
    w = [1, 2, 4, 8, 16]
    neoadc = [apply_neo_to_dataset(normalized, cw) for cw in w]

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
