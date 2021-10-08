from pathlib import Path
import h5py
import MEArec as mr


def save_converted_values(adcgen, filename=None, is_lcadc=False):

    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(filename, 'w') as f:
        saveConvertedValuesToFile(adcgen, f, is_lcadc=is_lcadc)


def saveConvertedValuesToFile(adcgen, f, is_lcadc=False):

    mr.save_dict_to_hdf5(adcgen["adcinfo"], f, 'adcinfo/')
    if is_lcadc:
        idx_array = []
        for idx, adc in enumerate(adcgen["lcadc"]):
            if len(adc) > 0:
                f.create_dataset('lcadc/' + str(idx),
                                 data=adc)
            if len(adcgen["indexes"][idx]) > 0:
                f.create_dataset('indexes/' + str(idx),
                                 data=adcgen["indexes"][idx])
            if len(adcgen["normalized"][idx]) > 0:
                f.create_dataset('normalized/' + str(idx),
                                 data=adcgen["normalized"][idx])
            idx_array += [idx]

        if len(idx_array) > 0:
            f.create_dataset("channels", data=idx_array)

    else:
        if len(adcgen["adc"]) > 0:
            f.create_dataset('adc', data=adcgen["adc"])
        if len(adcgen["normalized"]) > 0:
            f.create_dataset('normalized', data=adcgen["normalized"])

    if adcgen["recordings"]:
        recgen = adcgen["recordings"]
        mr.save_recording_to_file(recgen, f, path="recordings/")


def save_neo_values(neogen, filename=None, is_lcadc=False):
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(filename, 'w') as f:
        saveNEOValuesToFile(neogen, f, is_lcadc=is_lcadc)


def saveNEOValuesToFile(neogen, f, is_lcadc=False):

    if len(neogen["w"]) > 0:
        f.create_dataset('w', data=neogen["w"])

    if is_lcadc:
        for w_idx, w_item in enumerate(neogen["neo"]):
            for idx, item in enumerate(w_item):
                f.create_dataset('neo/' + str(w_idx) + '/' + str(idx),
                                 data=item)

    else:
        if len(neogen["neo"]) > 0:
            f.create_dataset('neo', data=neogen["neo"])

    saveConvertedValuesToFile(neogen, f, is_lcadc=is_lcadc)


def saveArray(array, filename=None, path='array'):
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(filename, 'w') as f:
        f.create_dataset(path, data=array)


def save_indexes_and_counts(dic, filename=None, path=''):

    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(filename, 'w') as f:
        createIndexAndCountDataset(
            dic, f, path)


def saveThresholdValues(thgen, filename=None):
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(filename, 'w') as f:
        saveThresholdValuesToFile(thgen, f)


def saveThresholdValuesToFile(thgen, f):

    if len(thgen["threshold"]) > 0:

        threshold = thgen["threshold"]
        if len(threshold["recordings"]) > 0:
            createIndexAndCountDataset(
                threshold["recordings"], f, "threshold/recordings")

        if len(threshold["normalized"]) > 0:
            createIndexAndCountDataset(
                threshold["normalized"], f, "threshold/normalized")

        if len(threshold["neo"]) > 0:
            for wdx in range(len(threshold["neo"])):
                createIndexAndCountDataset(
                    threshold["neo"], f, f"threshold/neo/{wdx}")

    saveNEOValuesToFile(thgen, f)


def createIndexAndCountDataset(data, f, path=""):

    mr.save_dict_to_hdf5(data, f, path)
    # if len(data["thresholds"]) > 0:
    #     f.create_dataset(
    #         path + 'thresholds',
    #         data=data["thresholds"])

    # if data["count_thresholds"]:
    #     f[path + "count_thresholds"] = data["count_thresholds"]

    # if len(data["indexes"]) > 0:
    #     f.create_dataset(
    #         path + 'indexes',
    #         data=data["indexes"])

    # if len(data["counts"]) > 0:
    #     f.create_dataset(
    #         path + 'counts',
    #         data=data["counts"])
