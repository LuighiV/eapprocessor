#!/bin/python
import time
from pathlib import Path
import numpy as np
from eapprocessor.tools.save import save_converted_values, save_neo_values, \
    save_indexes_and_counts
from eapprocessor.integrate import convert_adc_recordings, \
    convert_lcadc_recordings, \
    normalize_arrays, \
    apply_neo_to_dataset, evaluate_threshold_maximum, \
    evaluate_threshold_maximum_array
from eapprocessor.mearec.api import load_recordings
from eapprocessor.tools.load import load_converted_values, load_neo, \
    load_count_evaluation, load_indexes

from eapprocessor.evaluator.spikes import \
    comparison_detection_array_spiketrain_array


DEFAULT_OUTPUT = "./output"
default_dir = Path(DEFAULT_OUTPUT)

FOLDER_ADC = "adc"
FOLDER_LCADC = "lcadc"
FOLDER_PREPROCESSOR = "preprocessor"
FOLDER_PREPROCESSOR_LCADC = "preprocessor_lcadc"
FOLDER_EVALUATOR = "evaluator"


def get_converted_adc(recfile=None,
                      voltage_ref=1000,
                      resolution=12,
                      noise_level=None,
                      fs=None,
                      verbose=True,
                      is_lcadc=False):

    recfile = Path(recfile)
    recgen = load_recordings(datafolder=recfile,
                             noise_level=noise_level,
                             fs=fs,
                             verbose=verbose)

    adcgen = {}
    if is_lcadc:

        indexes, lcadc = convert_lcadc_recordings(
            recgen.recordings,
            voltage_ref=voltage_ref,
            resolution=resolution)
        normalized = normalize_arrays(lcadc, resolution=resolution)
        adcgen["lcadc"] = lcadc
        adcgen["indexes"] = indexes
        adcgen["normalized"] = normalized
    else:
        adc = convert_adc_recordings(
            recgen.recordings,
            voltage_ref=voltage_ref,
            resolution=resolution)

        normalized = normalize_arrays(adc, resolution=resolution)
        adcgen["adc"] = adc
        adcgen["normalized"] = normalized

    adcgen["adcinfo"] = {
        "voltage_ref": voltage_ref,
        "resolution": resolution
    }
    adcgen["recordings"] = recgen

    noise_level = recgen.info["recordings"]["noise_level"]
    fs = recgen.info["recordings"]["fs"]

    if recfile is not None:
        parent_dir = recfile.parent
    else:
        parent_dir = default_dir

    if is_lcadc:
        output_folder = FOLDER_LCADC
    else:
        output_folder = FOLDER_ADC

    filename = str(
        parent_dir /
        output_folder /
        f'samples_{resolution}_{np.round(noise_level, 2)}uV_'
        f'{int(fs)}Hz.h5')
    save_converted_values(adcgen, filename, is_lcadc=is_lcadc)

    return adcgen


def get_neo(
        adcfile=None,
        w=[1],
        resolution=None,
        noise_level=None,
        fs=None,
        verbose=None,
        is_lcadc=False):

    adcgen = load_converted_values(adcfile,
                                   resolution=resolution,
                                   noise_level=noise_level,
                                   fs=fs,
                                   verbose=verbose,
                                   is_lcadc=is_lcadc)

    neogen = adcgen
    neogen["w"] = w
    neogen["neo"] = [
        apply_neo_to_dataset(
            adcgen["normalized"],
            cw) for cw in w]

    resolution = adcgen["adcinfo"]["resolution"]
    noise_level = adcgen["recordings"].info["recordings"]["noise_level"]
    fs = adcgen["recordings"].info["recordings"]["fs"]

    if adcfile is not None:
        adcfile = Path(adcfile).resolve()
        parent_dir = adcfile.parent
    else:
        parent_dir = default_dir

    if is_lcadc:
        output_folder = FOLDER_PREPROCESSOR_LCADC
    else:
        output_folder = FOLDER_PREPROCESSOR

    filename = str(
        parent_dir /
        output_folder /
        f'preprocessed_neo_{resolution}_'
        f'{np.round(noise_level, 2)}uV_'
        f'{int(fs)}Hz_'
        f'{time.strftime("%Y-%m-%d_%H-%M")}.h5')

    save_neo_values(neogen, filename, is_lcadc)
    return neogen


def get_over_threshold(neofile,
                       resolution=None,
                       noise_level=None,
                       fs=None,
                       ch_indexes=None,
                       nthresholds=10,
                       verbose=None,
                       absolute_recordings=True,
                       absolute_adc=True,
                       absolute_neo=False):

    neogen, fneo = load_neo(neofile,
                            resolution=resolution,
                            noise_level=noise_level,
                            fs=fs,
                            verbose=verbose)

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
    listidx, counts, listidx_spikes, \
        counts_spikes, ths = evaluate_threshold_maximum(
            recordings, nthresholds, absolute=absolute_recordings)
    threcordings = {"source_file": str(fneo),
                    "channels": ch_indexes,
                    "indexes": listidx,
                    "counts": counts,
                    "indexes_spikes": listidx_spikes,
                    "counts_spikes": counts_spikes,
                    "thresholds": ths,
                    "count_thresholds": nthresholds}

    resolution = neogen["adcinfo"]["resolution"]
    noise_level = neogen["recordings"].info["recordings"]["noise_level"]
    fs = neogen["recordings"].info["recordings"]["fs"]

    if neofile is not None:
        neofile = Path(neofile).resolve()
        parent_dir = neofile.parent
    else:
        parent_dir = default_dir

    fileid = f'{nthresholds}th_{resolution}_'\
        f'{np.round(noise_level, 2)}uV_' \
        f'{int(fs)}Hz'

    if ch_indexes is not None:
        fileid = 'subset_' + fileid

    filename_rec = str(
        parent_dir /
        FOLDER_EVALUATOR /
        f'threshold_recordings_{fileid}_{time.strftime("%Y-%m-%d_%H-%M")}.h5')

    save_indexes_and_counts(threcordings, filename_rec)
    del threcordings

    print("Processing normalized")
    listidx, counts, listidx_spikes,\
        counts_spikes, ths = evaluate_threshold_maximum(normalized,
                                                        nthresholds,
                                                        absolute=absolute_adc)
    thnorm = {"source_file": str(fneo),
              "channels": ch_indexes,
              "indexes": listidx,
              "counts": counts,
              "indexes_spikes": listidx_spikes,
              "counts_spikes": counts_spikes,
              "thresholds": ths,
              "count_thresholds": nthresholds}

    filename_norm = str(
        parent_dir /
        FOLDER_EVALUATOR /
        f'threshold_normalized_{fileid}_{time.strftime("%Y-%m-%d_%H-%M")}.h5')

    save_indexes_and_counts(thnorm, filename_norm)
    del thnorm

    print("Processing neo array")
    listidx, counts, listidx_spikes, \
        counts_spikes, ths = evaluate_threshold_maximum_array(
            neo, nthresholds, absolute=absolute_neo)
    thneo = {"source_file": str(fneo),
             "channels": ch_indexes,
             "indexes": listidx,
             "counts": counts,
             "indexes_spikes": listidx_spikes,
             "counts_spikes": counts_spikes,
             "thresholds": ths,
             "count_thresholds": nthresholds}

    filename_neo = str(
        parent_dir /
        FOLDER_EVALUATOR /
        f'threshold_neo_{fileid}_{time.strftime("%Y-%m-%d_%H-%M")}.h5')

    save_indexes_and_counts(thneo, filename_neo)

    return neogen


def get_results_evaluation_dataset_array(dataset_files,
                                         indexes_list,
                                         channel_idx=0):

    results_list = []
    for dataset_file in dataset_files:

        evaluation_indexes = np.array(load_indexes(dataset_file))

        if len(evaluation_indexes.shape) == 4:
            results = [
                comparison_detection_array_spiketrain_array(
                    indexes_list,
                    evaluation[channel_idx])
                for evaluation in evaluation_indexes]

        elif len(evaluation_indexes.shape) == 3:
            results = comparison_detection_array_spiketrain_array(
                indexes_list,
                evaluation_indexes[channel_idx])

        else:
            results = comparison_detection_array_spiketrain_array(
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
    neogen, fneo = load_neo(neofolder)
    print(neogen)

    # thgen = getOverThreshold(neofolder)
    # print(thgen)

    evalfolder = default_dir / FOLDER_EVALUATOR

    counts, files = load_count_evaluation(evalfolder)
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
