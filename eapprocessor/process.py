#!/bin/python
import time
from pathlib import Path
import numpy as np
from eapprocessor.tools.save import saveConvertedValues, saveNEOValues, \
    saveIndexesAndCounts
from eapprocessor.integrate import convertADCRecordings, normalizeArrays, \
    applyNEOToDataset, evaluateThresHoldMaximum, \
    evaluateThresHoldMaximumArray
from eapprocessor.mearec.api import load_recordings
from eapprocessor.tools.load import loadConvertedValues, loadNEO, \
    loadCountEvaluation, loadIndexes

from eapprocessor.evaluator.spikes import \
    comparisonDetectionArraySpiketrainArray


DEFAULT_OUTPUT = "./output"
default_dir = Path(DEFAULT_OUTPUT)

FOLDER_ADC = "adc"
FOLDER_PREPROCESSOR = "preprocessor"
FOLDER_EVALUATOR = "evaluator"


def getConvertedADC(recfile=None, voltage_ref=1000, resolution=12,
                    noise_level=None, verbose=True):

    recfile = Path(recfile)
    recgen = load_recordings(datafolder=recfile, noise_level=noise_level,
                             verbose=verbose)

    adc = convertADCRecordings(
        recgen.recordings,
        voltage_ref=voltage_ref,
        resolution=resolution)

    normalized = normalizeArrays(adc, resolution=resolution)
    adcgen = {}
    adcgen["adc"] = adc
    adcgen["normalized"] = normalized
    adcgen["adcinfo"] = {
        "voltage_ref": voltage_ref,
        "resolution": resolution
    }
    adcgen["recordings"] = recgen

    noise_level = recgen.info["recordings"]["noise_level"]

    if recfile is not None:
        parent_dir = recfile.parent
    else:
        parent_dir = default_dir

    filename = str(
        parent_dir /
        FOLDER_ADC /
        f'samples_{resolution}_{np.round(noise_level, 2)}uV_.h5')
    saveConvertedValues(adcgen, filename)

    return adcgen


def getNEO(
        adcfile=None,
        w=[1],
        resolution=None,
        noise_level=None,
        verbose=None):

    adcgen = loadConvertedValues(adcfile, resolution=resolution,
                                 noise_level=noise_level, verbose=verbose)

    neogen = adcgen
    neogen["w"] = w
    neogen["neo"] = [
        applyNEOToDataset(
            np.array(
                adcgen["normalized"]),
            cw) for cw in w]

    resolution = adcgen["adcinfo"]["resolution"]
    noise_level = adcgen["recordings"].info["recordings"]["noise_level"]

    if adcfile is not None:
        adcfile = Path(adcfile).resolve()
        parent_dir = adcfile.parent
    else:
        parent_dir = default_dir

    filename = str(
        parent_dir /
        FOLDER_PREPROCESSOR /
        f'preprocessed_neo_{resolution}_'
        f'{np.round(noise_level, 2)}uV_{time.strftime("%Y-%m-%d_%H-%M")}.h5')

    saveNEOValues(neogen, filename)
    return neogen


def getOverThreshold(neofile,
                     resolution=None,
                     noise_level=None,
                     ch_indexes=None,
                     nthresholds=10,
                     verbose=None,
                     absolute_recordings=True,
                     absolute_adc=True,
                     absolute_neo=False):

    neogen, fneo = loadNEO(neofile, resolution=resolution,
                           noise_level=noise_level, verbose=verbose)

    recordings = np.array(neogen["recordings"].recordings[:, :].T)
    normalized = neogen["normalized"]
    neo = neogen["neo"]

    if ch_indexes is not None:
        recordings = recordings[ch_indexes]
        normalized = normalized[ch_indexes]
        neo = neo[:, ch_indexes]
    else:
        ch_indexes = np.arange(len(recordings))

    neogen["thresholds"] = nthresholds

    print("Processing recordings")
    listidx, counts, ths = evaluateThresHoldMaximum(
        recordings, nthresholds, absolute=absolute_recordings)
    threcordings = {"source_file": str(fneo),
                    "channels": ch_indexes,
                    "indexes": listidx,
                    "counts": counts,
                    "thresholds": ths,
                    "count_thresholds": nthresholds}

    resolution = neogen["adcinfo"]["resolution"]
    noise_level = neogen["recordings"].info["recordings"]["noise_level"]

    if neofile is not None:
        neofile = Path(neofile).resolve()
        parent_dir = neofile.parent
    else:
        parent_dir = default_dir

    fileid = f'{nthresholds}th_{resolution}_{np.round(noise_level, 2)}uV'
    if ch_indexes is not None:
        fileid = 'subset_' + fileid

    filename_rec = str(
        parent_dir /
        FOLDER_EVALUATOR /
        f'threshold_recordings_{fileid}_{time.strftime("%Y-%m-%d_%H-%M")}.h5')

    saveIndexesAndCounts(threcordings, filename_rec)
    del threcordings

    print("Processing normalized")
    listidx, counts, ths = evaluateThresHoldMaximum(normalized, nthresholds,
                                                    absolute=absolute_adc)
    thnorm = {"source_file": str(fneo),
              "channels": ch_indexes,
              "indexes": listidx,
              "counts": counts,
              "thresholds": ths,
              "count_thresholds": nthresholds}

    filename_norm = str(
        parent_dir /
        FOLDER_EVALUATOR /
        f'threshold_normalized_{fileid}_{time.strftime("%Y-%m-%d_%H-%M")}.h5')

    saveIndexesAndCounts(thnorm, filename_norm)
    del thnorm

    print("Processing neo array")
    listidx, counts, ths = evaluateThresHoldMaximumArray(neo, nthresholds,
                                                         absolute=absolute_neo)
    thneo = {"source_file": str(fneo),
             "channels": ch_indexes,
             "indexes": listidx,
             "counts": counts,
             "thresholds": ths,
             "count_thresholds": nthresholds}

    filename_neo = str(
        parent_dir /
        FOLDER_EVALUATOR /
        f'threshold_neo_{fileid}_{time.strftime("%Y-%m-%d_%H-%M")}.h5')

    saveIndexesAndCounts(thneo, filename_neo)

    return neogen


def getResultsEvaluationDatasetArray(dataset_files,
                                     indexes_list,
                                     channel_idx=0):

    results_list = []
    for dataset_file in dataset_files:

        evaluation_indexes = np.array(loadIndexes(dataset_file))

        if len(evaluation_indexes.shape) == 4:
            results = [
                comparisonDetectionArraySpiketrainArray(
                    indexes_list,
                    evaluation[channel_idx])
                for evaluation in evaluation_indexes]

        elif len(evaluation_indexes.shape) == 3:
            results = comparisonDetectionArraySpiketrainArray(
                indexes_list,
                evaluation_indexes[channel_idx])

        else:
            results = comparisonDetectionArraySpiketrainArray(
                indexes_list,
                evaluation_indexes)

        results_list += [np.array(results)]

    return results_list


if __name__ == "__main__":

    # adgen = getConvertedADC()
    folder = default_dir / FOLDER_ADC
    # adcgen = loadConvertedValues(folder)
    # print(adcgen)

    # normalized = np.array(adcgen["normalized"])
    # neogen = getNEO(folder, w=[1, 2, 4, 16])

    neofolder = default_dir / FOLDER_PREPROCESSOR
    neogen, fneo = loadNEO(neofolder)
    print(neogen)

    # thgen = getOverThreshold(neofolder)
    # print(thgen)

    evalfolder = default_dir / FOLDER_EVALUATOR

    counts, files = loadCountEvaluation(evalfolder)
    print(counts)

    import matplotlib.pylab as plt

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(counts["recordings"][0], label="recordings")
    ax.plot(counts["normalized"][0], label="normalized")

    for idx in range(len(counts["neo"])):
        ax.plot(counts["neo"][idx][0], label=f"w={neogen['w'][idx]}")

    ax.set_xlabel("Threshold/Amax")
    ax.set_ylabel("Samples over threshold")
    ax.legend()
    plt.show()
