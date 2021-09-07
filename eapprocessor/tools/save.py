from pathlib import Path
import h5py
import MEArec as mr


def saveConvertedValues(adcgen, filename=None):

    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(filename, 'w') as f:
        saveConvertedValuesToFile(adcgen, f)


def saveConvertedValuesToFile(adcgen, f):

    mr.save_dict_to_hdf5(adcgen["adcinfo"], f, 'adcinfo/')
    if len(adcgen["adc"]) > 0:
        f.create_dataset('adc', data=adcgen["adc"])
    if len(adcgen["normalized"]) > 0:
        f.create_dataset('normalized', data=adcgen["normalized"])
    if adcgen["recordings"]:
        recgen = adcgen["recordings"]
        mr.save_recording_to_file(recgen, f, path="recordings/")


def saveNEOValues(neogen, filename=None):
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(filename, 'w') as f:
        saveNEOValuesToFile(neogen, f)


def saveNEOValuesToFile(neogen, f):

    if len(neogen["w"]) > 0:
        f.create_dataset('w', data=neogen["w"])

    if len(neogen["neo"]) > 0:
        f.create_dataset('neo', data=neogen["neo"])

    saveConvertedValuesToFile(neogen, f)


def saveArray(array, filename=None, path='array'):
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(filename, 'w') as f:
        f.create_dataset(path, data=array)


def saveIndexesAndCounts(dic, filename=None, path=''):

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

    if len(data["indexes"]) > 0:
        f.create_dataset(
            path + 'indexes',
            data=data["indexes"])

    if len(data["counts"]) > 0:
        f.create_dataset(
            path + 'counts',
            data=data["counts"])
