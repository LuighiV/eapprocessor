#!/bin/python
from eapprocessor.tools.save import saveConvertedValues, saveNEOValues, \
    saveThresholdValues, saveIndexesAndCounts
from eapprocessor.integrate import convertADCRecordings, normalizeArrays, \
    applyNEOToDataset, evaluateThresHoldMaximum, \
    evaluateThresHoldMaximumArray
from eapprocessor.mearecapi.api import loadRecordings
from pathlib import Path
import time
import numpy as np
from eapprocessor.tools.load import loadConvertedValues, loadNEO, \
    loadCountEvaluation

DEFAULT_OUTPUT = "./output"
default_dir = Path(DEFAULT_OUTPUT)

FOLDER_ADC = "adc"
FOLDER_PREPROCESSOR = "preprocessor"
FOLDER_EVALUATOR = "evaluator"


def getConvertedADC(recfile=None, voltage_ref=1000, resolution=12):

    recgen = loadRecordings(recfile)

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

    filename = str(default_dir / FOLDER_ADC / f'samples_{resolution}.h5')
    saveConvertedValues(adcgen, filename)

    return adcgen


def getNEO(adcfile=None, w=[1]):

    adcgen = loadConvertedValues(adcfile)

    neogen = adcgen
    neogen["w"] = w
    neogen["neo"] = [
        applyNEOToDataset(
            np.array(
                adcgen["normalized"]),
            cw) for cw in w]

    filename = str(
        default_dir /
        FOLDER_PREPROCESSOR /
        f'preprocessed_neo_{time.strftime("%Y-%m-%d_%H-%M")}.h5')

    saveNEOValues(neogen, filename)
    return neogen


def getOverThreshold(neofile):
    neogen = loadNEO(neofile)

    recordings = np.array(neogen["recordings"].recordings[:, :].T)
    normalized = neogen["normalized"]
    neo = neogen["neo"]

    neogen["threshold"] = {}

    print("Processing recordings")
    listidx, counts = evaluateThresHoldMaximum(recordings, 10)
    threcordings = {"indexes": listidx, "counts": counts}

    filename = str(
        default_dir /
        FOLDER_EVALUATOR /
        f'threshold_recordings_{time.strftime("%Y-%m-%d_%H-%M")}.h5')

    saveIndexesAndCounts(threcordings, filename)
    del threcordings

    print("Processing normalized")
    listidx, counts = evaluateThresHoldMaximum(normalized, 10)
    thnorm = {"indexes": listidx, "counts": counts}

    filename = str(
        default_dir /
        FOLDER_EVALUATOR /
        f'threshold_normalized_{time.strftime("%Y-%m-%d_%H-%M")}.h5')

    saveIndexesAndCounts(thnorm, filename)
    del thnorm

    print("Processing neo array")
    listidx, counts = evaluateThresHoldMaximumArray(neo, 10)
    thneo = {"indexes": listidx, "counts": counts}

    filename = str(
        default_dir /
        FOLDER_EVALUATOR /
        f'threshold_neo_{time.strftime("%Y-%m-%d_%H-%M")}.h5')

    saveIndexesAndCounts(thneo, filename)
    return neogen


if __name__ == "__main__":

    # adgen = getConvertedADC()
    folder = default_dir / FOLDER_ADC
    # adcgen = loadConvertedValues(folder)
    # print(adcgen)

    # normalized = np.array(adcgen["normalized"])
    # neogen = getNEO(folder, w=[1, 2, 4, 16])

    neofolder = default_dir / FOLDER_PREPROCESSOR
    neogen = loadNEO(neofolder)
    print(neogen)

    # thgen = getOverThreshold(neofolder)
    # print(thgen)

    evalfolder = default_dir / FOLDER_EVALUATOR

    counts = loadCountEvaluation(evalfolder)
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
