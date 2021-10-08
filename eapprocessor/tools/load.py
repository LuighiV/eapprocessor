# /bin/python3

from pathlib import Path
import h5py
import MEArec as mr
import numpy as np


def find_recording_files(
        folder,
        resolution=None,
        noise_level=None,
        fs=None,
        reverse=True):

    pattern = build_pattern(resolution=resolution,
                            noise_level=noise_level,
                            fs=fs)
    print(f"Search for pattern: {pattern}")
    recording_files = [f for f in folder.rglob(pattern) if
                       f.name.endswith(('.h5', '.hdf5'))]
    recording_files.sort(reverse=reverse)
    return recording_files


def load_converted_values(
        filename=None,
        resolution=None,
        noise_level=None,
        fs=None,
        verbose=True,
        check_suffix=True,
        is_lcadc=False):

    filename = Path(filename).resolve()
    adc_dict = {}
    if filename.is_dir():

        recording_files = find_recording_files(filename,
                                               resolution=resolution,
                                               noise_level=noise_level,
                                               fs=fs)
        if len(recording_files) == 0:
            raise AttributeError(filename, ' contains no adc values!')

        filename = recording_files[0]
        if verbose:
            print(f'Loading file {filename}')

    if (filename.suffix in ['.h5', '.hdf5']) or (not check_suffix):
        f = h5py.File(str(filename), 'r')

        adc_dict = load_converted_values_from_file(f, is_lcadc=is_lcadc)

    else:
        raise Exception("Converted values must be an hdf5 file (.h5 or .hdf5)")

    return adc_dict


def load_converted_values_from_file(f, path='', is_lcadc=False):

    adc_dict = {}

    adc_dict["adcinfo"] = mr.load_dict_from_hdf5(f, path + 'adcinfo/')

    if is_lcadc:
        if f.get(path + 'channels') is not None:
            adc_dict["channels"] = f.get(path + 'channels')

            channels = np.array(adc_dict["channels"])
            lcadc = []
            indexes = []
            normalized = []
            for channel in channels:
                if f.get(path + 'lcadc/' + str(channel)) is not None:
                    lcadc += [f.get(path + 'lcadc/' + str(channel))]
                if f.get(path + 'indexes/' + str(channel)) is not None:
                    indexes += [f.get(path + 'indexes/' + str(channel))]
                if f.get(path + 'normalized/' + str(channel)) is not None:
                    normalized += [f.get(path + 'normalized/' + str(channel))]

            adc_dict["lcadc"] = lcadc
            adc_dict["indexes"] = indexes
            adc_dict["normalized"] = normalized
        else:
            assert AttributeError("When using LCADC you must provide the "
                                  "channels information")

    else:
        if f.get(path + 'adc') is not None:
            adc_dict["adc"] = f.get(path + 'adc')

        if f.get(path + 'normalized') is not None:
            adc_dict["normalized"] = f.get(path + 'normalized')

    rec_dict, info = mr.load_recordings_from_file(f, path=path + 'recordings/')
    recgen = mr.RecordingGenerator(rec_dict=rec_dict, info=info)
    adc_dict["recordings"] = recgen

    return adc_dict


def load_neo(filename=None,
             resolution=None,
             noise_level=None,
             fs=None,
             verbose=True,
             check_suffix=True):

    filename = Path(filename).resolve()
    neo_dict = {}
    if filename.is_dir():

        recording_files = find_recording_files(filename,
                                               resolution=resolution,
                                               fs=fs,
                                               noise_level=noise_level)
        if len(recording_files) == 0:
            raise AttributeError(filename, ' contains no neo values!')

        filename = recording_files[0]
        if verbose:
            print(f'Loading file {filename}')

    if (filename.suffix in ['.h5', '.hdf5']) or (not check_suffix):
        file = h5py.File(str(filename), 'r')

        neo_dict = load_neo_from_file(file)

    else:
        raise Exception("NEO values must be an hdf5 file (.h5 or .hdf5)")

    return neo_dict, filename


def load_neo_from_file(f, path=''):

    neo_dict = load_converted_values_from_file(f, path=path)

    if f.get(path + 'w') is not None:
        neo_dict["w"] = f.get(path + 'w')

    if f.get(path + 'neo') is not None:
        neo_dict["neo"] = f.get(path + 'neo')

    return neo_dict


def build_pattern(resolution=None,
                  noise_level=None,
                  fs=None,
                  nthresholds=None):

    pattern = ""

    if nthresholds is not None:
        pattern = f'_{nthresholds}th'

    if resolution is not None:
        pattern += f'_{resolution}'
    else:
        if pattern != "":
            pattern += "*"

    if noise_level is not None:
        pattern += f'_{np.round(noise_level, 2)}uV'
    else:
        if pattern != "":
            pattern = pattern.rstrip("*") + "*"

    if fs is not None:
        pattern += f'_{int(fs)}Hz'

    if pattern != "":
        pattern = pattern.rstrip("*")
        return f'*{pattern}*'
    else:
        return "*"


def find_related_files(folder,
                       sourcefile,
                       verbose=True,
                       resolution=None,
                       noise_level=None,
                       fs=None,
                       nthresholds=None):

    folder = Path(folder).resolve()
    if folder.is_dir():
        pattern = build_pattern(resolution=resolution,
                                noise_level=noise_level,
                                fs=fs,
                                nthresholds=nthresholds)
        print(f"Search for pattern: {pattern}")
        recording_files = [f for f in folder.rglob(pattern) if
                           f.name.endswith(('.h5', '.hdf5'))]
        recording_files.sort(reverse=True)
        if len(recording_files) == 0:
            raise AttributeError(folder, ' contains no neo values!')

        related_recordings = []
        for recording in recording_files:
            file = h5py.File(str(recording), 'r')
            if file.get("source_file") is not None:
                filename = file["source_file"].astype("|O")
                filename = filename[()].decode()
                # print(filename)

                if filename == str(sourcefile):
                    related_recordings += [recording]

        print(f'Filename found {len(related_recordings)} files with source '
              f'{sourcefile}')
        return related_recordings
    else:
        raise AttributeError(folder, ' is not a folder!')


def get_file(folder, starts, verbose=True):

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


def get_evaluation_files(folder, sourcefile=None, verbose=True):

    if sourcefile is None:
        record = get_file(folder, 'threshold_recordings', verbose=verbose)
        normal = get_file(folder, 'threshold_normalized', verbose=verbose)
        neo = get_file(folder, 'threshold_neo', verbose=verbose)
    else:
        related_files = find_related_files(folder=folder,
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


def load_count_evaluation(folder=None,
                          sourcefile=None,
                          recordings_file=None,
                          normalized_file=None,
                          neo_file=None,
                          include_channels=True,
                          verbose=True):

    if folder is not None:
        files_dict = get_evaluation_files(folder,
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
        count_dict["channels"] = load_channels(recordings_file)
    count_dict["recordings"] = load_count(recordings_file)
    count_dict["normalized"] = load_count(normalized_file)
    count_dict["neo"] = load_count(neo_file)

    return count_dict


def load_evaluation(filename):

    f = h5py.File(str(filename), 'r')

    return load_evaluation_from_file(f, path="/")


def load_evaluation_from_file(f, path=''):

    return mr.load_dict_from_hdf5(f, path=path)


def load_parameter(filename, parameter, path=""):

    f = h5py.File(str(filename), 'r')

    return load_parameter_from_file(f, parameter=parameter, path=path)


def load_parameter_from_file(f, parameter, path=""):

    values = None
    if f.get(path + parameter) is not None:
        values = f.get(path + parameter)

    return values


def load_count(filename, path=''):

    return load_parameter(filename=filename,
                          parameter="counts",
                          path=path)


def load_channels(filename, path=''):

    return load_parameter(filename=filename,
                          parameter="channels",
                          path=path)


def load_indexes(filename, path=''):

    return load_parameter(filename=filename,
                          parameter="indexes",
                          path=path)
