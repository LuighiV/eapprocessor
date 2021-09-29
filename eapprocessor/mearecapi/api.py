#!/bin/python3
from pathlib import Path
from distutils.version import StrictVersion
import time
import yaml
import MEArec as mr
import numpy as np

DEFAULT_DATA_INFO = "./data/mearec"
default_dir = Path(DEFAULT_DATA_INFO)

use_loader = bool(StrictVersion(yaml.__version__) >= StrictVersion('5.0.0'))


def getConfigInfo(datafolder=None):

    if datafolder is None:
        datafolder = default_dir

        with (datafolder / 'mearec.conf').open() as f:
            if use_loader:
                default_info = yaml.load(f, Loader=yaml.FullLoader)
            else:
                default_info = yaml.load(f)
    else:
        datafolder = Path(datafolder).resolve()
        parentfolder = datafolder.parent.parent
        default_info = {
            "cell_models_folder": str(
                datafolder /
                "cell_models" /
                "bbp"),
            "recordings_params": str(
                datafolder /
                "params" /
                "recordings_params.yaml"),
            "templates_params": str(
                datafolder /
                "params" /
                "templates_params.yaml"),
            "recordings_folder": str(
                parentfolder /
                "output" /
                "recordings"),
            "templates_folder": str(
                parentfolder /
                "output" /
                "templates")}

    return default_info


def generateTemplates(
        config_folder=None,
        cell_models_folder=None,
        templates_folder=None,
        templates_params_file=None,
        n_jobs=None,
        recompile=None,
        parallel=None,
        verbose=None,
        fname=None):

    if config_folder is not None:
        config = getConfigInfo(datafolder=config_folder)

        if templates_params_file is None:
            templates_params_file = config['templates_params']

        if cell_models_folder is None:
            cell_models_folder = config['cell_models_folder']

        if templates_folder is None:
            templates_folder = config['templates_folder']

    with open(templates_params_file, 'r', encoding='utf8') as pf:
        if use_loader:
            params_dict = yaml.load(pf, Loader=yaml.FullLoader)
        else:
            params_dict = yaml.load(pf)
            print(params_dict)

    print(templates_folder)
    print(cell_models_folder)
    templates = mr.gen_templates(
        cell_models_folder=cell_models_folder,
        params=params_dict,
        templates_tmp_folder=templates_folder,
        intraonly=False,
        n_jobs=n_jobs,
        recompile=recompile,
        parallel=parallel,
        verbose=verbose)

    print("Models generated")
    rot = params_dict['rot']
    n = params_dict['n']
    probe = params_dict['probe']
    if fname is None:
        if params_dict['drifting']:
            fname = f'templates_{n}_{probe}_drift_' + \
                f'{time.strftime("%d-%m-%Y_%H-%M")}.h5'
        else:
            fname = f'templates_{n}_{probe}_' + \
                f'{time.strftime("%d-%m-%Y_%H-%M")}.h5'

    save_fname = str(Path(templates_folder) / rot / fname)
    mr.save_template_generator(templates, save_fname, verbose=True)
    return templates


def generateRecordings(
        config_folder=None,
        recordings_params_file=None,
        templates_folder=None,
        recordings_folder=None,
        verbose=None,
        njobs=None,
        fname=None,
        fs=None,
        noise_level=10):

    if config_folder is not None:
        config = getConfigInfo(datafolder=config_folder)

        if recordings_params_file is None:
            recordings_params_file = config['recordings_params']

        if templates_folder is None:
            templates_folder = config['templates_folder']

        if recordings_folder is None:
            recordings_folder = config['recordings_folder']

    with open(recordings_params_file, 'r', encoding='utf8') as pf:
        if use_loader:
            params_dict = yaml.load(pf, Loader=yaml.FullLoader)
        else:
            params_dict = yaml.load(pf)

    print(params_dict)

    if noise_level is not None:
        params_dict["recordings"]["noise_level"] = noise_level

    if fs is not None:
        params_dict["recordings"]["fs"] = fs

    recordings = mr.gen_recordings(
        templates=templates_folder,
        params=params_dict,
        verbose=verbose,
        n_jobs=njobs)

    info = recordings.info

    n_neurons = info['recordings']['n_neurons']
    electrode_name = info['electrodes']['electrode_name']
    duration = info['recordings']['duration']
    noise_level = info['recordings']['noise_level']
    fs = info['recordings']['fs']

    if fname is None:
        if params_dict['recordings']['drifting']:
            fname = f'recordings_{n_neurons}cells_{electrode_name}' \
                f'_{duration}_{np.round(noise_level, 2)}uV_' \
                f'_{fs}Hz_' \
                f'drift_{time.strftime("%d-%m-%Y_%H-%M")}.h5'
        else:
            fname = f'recordings_{n_neurons}cells_{electrode_name}' \
                f'_{duration}_{np.round(noise_level, 2)}uV_' \
                f'_{fs}Hz_' \
                f'{time.strftime("%d-%m-%Y_%H-%M")}.h5'
    n_neurons = info['recordings']['n_neurons']
    electrode_name = info['electrodes']['electrode_name']
    duration = info['recordings']['duration']
    noise_level = info['recordings']['noise_level']

    save_fname = str(Path(recordings_folder) / fname)
    mr.save_recording_generator(recordings, save_fname, verbose=True)
    return recordings


def loadRecordings(datafolder=None, verbose=None, noise_level=None):

    if datafolder is None:
        config = getConfigInfo(datafolder=datafolder)
        recordings_folder = config['recordings_folder']
    else:
        recordings_folder = datafolder

    if noise_level is not None:
        recordings = Path(recordings_folder).resolve()
        pattern = f'_{np.round(noise_level, 2)}uV_'

        recording_files = [f for f in recordings.rglob(f"*{pattern}*") if
                           f.name.endswith(('.h5', '.hdf5'))]
        recording_files.sort(reverse=True)
        if len(recording_files) == 0:
            raise AttributeError(
                recordings,
                ' contains no recordings models with noise_level ',
                noise_level)
        else:
            recordings = recording_files[0]
            if verbose:
                print(f'Loading file {recordings}')
            recgen = mr.load_recordings(recordings, verbose=verbose)
    else:
        recgen = mr.load_recordings(recordings_folder, verbose=verbose)
    return recgen


if __name__ == "__main__":
    # tempgen = generateTemplates(verbose=True, recompile=True)
    # print(tempgen)
    # recgen = generateRecordings(verbose=True)
    recgen = loadRecordings(verbose=True)
    print(recgen)
