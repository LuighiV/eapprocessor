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


def getConfigInfo():
    with (default_dir / 'mearec.conf').open() as f:
        if use_loader:
            default_info = yaml.load(f, Loader=yaml.FullLoader)
        else:
            default_info = yaml.load(f)

    return default_info


def generateTemplates(
        n_jobs=None,
        recompile=None,
        parallel=None,
        verbose=None,
        fname=None):

    config = getConfigInfo()
    with open(config['templates_params'], 'r', encoding='utf8') as pf:
        if use_loader:
            params_dict = yaml.load(pf, Loader=yaml.FullLoader)
        else:
            params_dict = yaml.load(pf)
            print(params_dict)

    templates_folder = config['templates_folder']
    model_folder = config['cell_models_folder']
    print(templates_folder)
    print(model_folder)
    templates = mr.gen_templates(
        cell_models_folder=model_folder,
        params=params_dict,
        templates_tmp_folder=templates_folder,
        intraonly=False,
        n_jobs=n_jobs,
        recompile=recompile,
        parallel=parallel,
        verbose=verbose)

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
        verbose=None,
        njobs=None,
        fname=None):

    config = getConfigInfo()
    with open(config['recordings_params'], 'r', encoding='utf8') as pf:
        if use_loader:
            params_dict = yaml.load(pf, Loader=yaml.FullLoader)
        else:
            params_dict = yaml.load(pf)
            print(params_dict)

    templates_folder = config['templates_folder']
    recordings_folder = config['recordings_folder']
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

    if fname is None:
        if params_dict['recordings']['drifting']:
            fname = f'recordings_{n_neurons}cells_{electrode_name}' \
                    f'_{duration}_{np.round(noise_level, 2)}uV_' \
                    f'drift_{time.strftime("%d-%m-%Y_%H-%M")}.h5'
        else:
            fname = f'recordings_{n_neurons}cells_{electrode_name}' \
                f'_{duration}_{np.round(noise_level, 2)}uV_' \
                    f'{time.strftime("%d-%m-%Y_%H-%M")}.h5'
    n_neurons = info['recordings']['n_neurons']
    electrode_name = info['electrodes']['electrode_name']
    duration = info['recordings']['duration']
    noise_level = info['recordings']['noise_level']

    save_fname = str(Path(recordings_folder) / fname)
    mr.save_recording_generator(recordings, save_fname, verbose=True)
    return recordings


def loadRecordings(verbose=None):

    config = getConfigInfo()
    recordings_folder = config['recordings_folder']
    recgen = mr.load_recordings(recordings_folder, verbose=verbose)
    return recgen


if __name__ == "__main__":
    # tempgen = generateTemplates(verbose=True, recompile=True)
    # print(tempgen)
    # recgen = generateRecordings(verbose=True)
    recgen = loadRecordings(verbose=True)
    print(recgen)
