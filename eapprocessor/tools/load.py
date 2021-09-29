# /bin/python3

from pathlib import Path
import h5py
import MEArec as mr
import numpy as np


def findRecordingFiles(folder, resolution=None, noise_level=None,
                       reverse=True):

    pattern = ""
    if resolution is not None:
        pattern = f'_{int(resolution)}_'
    if noise_level is not None:
        pattern = pattern.rstrip("_") + f'_{np.round(noise_level, 2)}uV_'
    print(pattern)

    if pattern != "":
        recording_files = [f for f in folder.rglob(f"*{pattern}*") if
                           f.name.endswith(('.h5', '.hdf5'))]
    else:
        recording_files = [f for f in folder.rglob("*") if
                           f.name.endswith(('.h5', '.hdf5'))]
    recording_files.sort(reverse=reverse)
    return recording_files


def loadConvertedValues(
        filename=None,
        resolution=None,
        noise_level=None,
        verbose=True,
        check_suffix=True):

    filename = Path(filename).resolve()
    adc_dict = {}
    if filename.is_dir():

        recording_files = findRecordingFiles(filename, resolution=resolution,
                                             noise_level=noise_level)
        if len(recording_files) == 0:
            raise AttributeError(filename, ' contains no adc values!')

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


def loadNEO(filename=None,
            resolution=None,
            noise_level=None,
            verbose=True, check_suffix=True):

    filename = Path(filename).resolve()
    neo_dict = {}
    if filename.is_dir():

        recording_files = findRecordingFiles(filename, resolution=resolution,
                                             noise_level=noise_level)
        if len(recording_files) == 0:
            raise AttributeError(filename, ' contains no neo values!')

        filename = recording_files[0]
        if verbose:
            print(f'Loading file {filename}')

    if (filename.suffix in ['.h5', '.hdf5']) or (not check_suffix):
        f = h5py.File(str(filename), 'r')

        neo_dict = loadNEOFromFile(f)

    else:
        raise Exception("NEO values must be an hdf5 file (.h5 or .hdf5)")

    return neo_dict, filename


def loadNEOFromFile(f, path=''):

    neo_dict = loadConvertedValuesFromFile(f, path=path)

    if f.get(path + 'w') is not None:
        neo_dict["w"] = f.get(path + 'w')

    if f.get(path + 'neo') is not None:
        neo_dict["neo"] = f.get(path + 'neo')

    return neo_dict


def buildPattern(resolution=None, noise_level=None, nthresholds=None):

    pattern = ""

    if nthresholds is not None:
        pattern = f'_{nthresholds}th'

    if resolution is not None:
        pattern += f'_{resolution}'
    else:
        if pattern != "":
            pattern += "*"

    if noise_level is not None:
        pattern = f'_{np.round(noise_level, 2)}uV'

    if pattern != "":
        pattern = pattern.rstrip("*")
        return f'*{pattern}*'
    else:
        return "*"


def findRelatedFiles(folder, sourcefile, verbose=True, resolution=None,
                     noise_level=None, nthresholds=None):

    folder = Path(folder).resolve()
    if folder.is_dir():
        pattern = buildPattern(resolution=resolution,
                               noise_level=noise_level,
                               nthresholds=nthresholds)
        print(pattern)
        recording_files = [f for f in folder.rglob(pattern) if
                           f.name.endswith(('.h5', '.hdf5'))]
        recording_files.sort(reverse=True)
        if len(recording_files) == 0:
            raise AttributeError(folder, ' contains no neo values!')

        related_recordings = []
        for recording in recording_files:
            f = h5py.File(str(recording), 'r')
            if f.get("source_file") is not None:
                filename = f["source_file"].astype("|O")
                filename = filename[()].decode()
                # print(filename)

                if filename == str(sourcefile):
                    related_recordings += [recording]

        print(f'Filename found {len(related_recordings)} files with source '
              f'{sourcefile}')
        return related_recordings
    else:
        raise AttributeError(folder, ' is not a folder!')


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


def getEvaluationFiles(folder, sourcefile=None, verbose=True):

    if sourcefile is None:
        record = getFile(folder, 'threshold_recordings', verbose=verbose)
        normal = getFile(folder, 'threshold_normalized', verbose=verbose)
        neo = getFile(folder, 'threshold_neo', verbose=verbose)
    else:
        related_files = findRelatedFiles(folder=folder,
                                         sourcefile=sourcefile)
        record = [f for f in related_files if
                  f.name.startswith("threshold_recordings")][0]

        normal = [f for f in related_files if
                  f.name.startswith("threshold_normalized")][0]

        neo = [f for f in related_files if
               f.name.startswith("threshold_neo")][0]

    files_dict = {
        "recordings_file": record,
        "normalized_file": normal,
        "neo_file": neo
    }

    return files_dict


def loadCountEvaluation(folder=None,
                        sourcefile=None,
                        recordings_file=None,
                        normalized_file=None,
                        neo_file=None,
                        include_channels=True,
                        verbose=True):

    if folder is not None:
        files_dict = getEvaluationFiles(folder,
                                        sourcefile=sourcefile,
                                        verbose=verbose)
        if recordings_file is None:
            recordings_file = files_dict["recordings_file"]

        if normalized_file is None:
            normalized_file = files_dict["normalized_file"]

        if neo_file is None:
            neo_file = files_dict["neo_file"]

    count_dict = {}

    if include_channels:
        count_dict["channels"] = loadChannels(recordings_file)
    count_dict["recordings"] = loadCount(recordings_file)
    count_dict["normalized"] = loadCount(normalized_file)
    count_dict["neo"] = loadCount(neo_file)

    return count_dict


def loadEvaluation(filename):

    f = h5py.File(str(filename), 'r')

    return loadEvaluationFromFile(f, path="/")


def loadEvaluationFromFile(f, path=''):

    return mr.load_dict_from_hdf5(f, path=path)


def loadParameter(filename, parameter, path=""):

    f = h5py.File(str(filename), 'r')

    return loadParameterFromFile(f, parameter=parameter, path=path)


def loadParameterFromFile(f, parameter, path=""):

    values = None
    if f.get(path + parameter) is not None:
        values = f.get(path + parameter)

    return values


def loadCount(filename, path=''):

    return loadParameter(filename=filename,
                         parameter="counts",
                         path=path)


def loadChannels(filename, path=''):

    return loadParameter(filename=filename,
                         parameter="channels",
                         path=path)

def loadIndexes(filename, path=''):

    return loadParameter(filename=filename,
                         parameter="indexes",
                         path=path)
