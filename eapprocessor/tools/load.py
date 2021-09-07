# /bin/python3

from pathlib import Path
import h5py
import MEArec as mr
from distutils.version import StrictVersion


def loadConvertedValues(filename=None, verbose=True, check_suffix=True):

    filename = Path(filename).resolve()
    adc_dict = {}
    if filename.is_dir():
        recording_files = [f for f in filename.rglob("*") if
                           f.name.endswith(('.h5', '.hdf5'))]
        recording_files.sort(reverse=True)
        if len(recording_files) == 0:
            raise AttributeError(filename, ' contains no adc values!')
        else:
            filename = recording_files[0]
            if verbose:
                print(f'Loading file {filename}')

    if (filename.suffix in ['.h5', '.hdf5']) or (not check_suffix):
        f = h5py.File(str(filename), 'r')

        adc_dict = loadConvertedValuesFromFile(f)

    else:
        raise Exception("Converted values must be an hdf5 file (.h5 or .hdf5)")

    return adc_dict


def loadConvertedValuesFromFile(f, path=''):

    adc_dict = {}

    adc_dict["adcinfo"] = mr.load_dict_from_hdf5(f, path + 'adcinfo/')

    if f.get(path + 'adc') is not None:
        adc_dict["adc"] = f.get(path + 'adc')

    if f.get(path + 'normalized') is not None:
        adc_dict["normalized"] = f.get(path + 'normalized')

    rec_dict, info = mr.load_recordings_from_file(f, path=path + 'recordings/')
    recgen = mr.RecordingGenerator(rec_dict=rec_dict, info=info)
    adc_dict["recordings"] = recgen

    return adc_dict


def loadNEO(filename=None, verbose=True, check_suffix=True):

    filename = Path(filename).resolve()
    adc_dict = {}
    if filename.is_dir():
        recording_files = [f for f in filename.rglob("*") if
                           f.name.endswith(('.h5', '.hdf5'))]
        recording_files.sort(reverse=True)
        if len(recording_files) == 0:
            raise AttributeError(filename, ' contains no neo values!')
        else:
            filename = recording_files[0]
            if verbose:
                print(f'Loading file {filename}')

    if (filename.suffix in ['.h5', '.hdf5']) or (not check_suffix):
        f = h5py.File(str(filename), 'r')

        adc_dict = loadNEOFromFile(f)

    else:
        raise Exception("NEO values must be an hdf5 file (.h5 or .hdf5)")

    return adc_dict


def loadNEOFromFile(f, path=''):

    neo_dict = loadConvertedValuesFromFile(f, path=path)

    if f.get(path + 'w') is not None:
        neo_dict["w"] = f.get(path + 'w')

    if f.get(path + 'neo') is not None:
        neo_dict["neo"] = f.get(path + 'neo')

    return neo_dict


def getFile(folder, starts, verbose=True):

    folder = Path(folder).resolve()
    filename = None
    if folder.is_dir():
        recording_files = [f for f in folder.rglob(starts + "*") if
                           f.name.endswith(('.h5', '.hdf5'))]
        recording_files.sort(reverse=True)
        if len(recording_files) == 0:
            raise AttributeError(folder, ' contains no neo values!')
        else:
            filename = recording_files[0]
            print(f'Filename found {filename}')

    return filename


def loadCountEvaluation(folder=None, verbose=True):

    record = getFile(folder, 'threshold_recordings', verbose=verbose)
    normal = getFile(folder, 'threshold_normalized', verbose=verbose)
    neo = getFile(folder, 'threshold_neo', verbose=verbose)

    count_dict = {}

    count_dict["recordings"] = loadCount(record)
    count_dict["normalized"] = loadCount(normal)
    count_dict["neo"] = loadCount(neo)

    return count_dict


def loadCount(filename, path=''):

    f = h5py.File(str(filename), 'r')

    return loadCountFromFile(f, path=path)


def loadCountFromFile(f, path=''):

    counts = []
    if f.get(path + 'counts') is not None:
        counts = f.get(path + 'counts')

    return counts
