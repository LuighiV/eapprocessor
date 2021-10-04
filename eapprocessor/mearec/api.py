#!/bin/python3
"""
:File: api.py
:Author: Luighi Viton
:Email: luighiavz@gmail.com
:Github: https://github.com/LuighiV
:Description: Module to interface with MEArec
"""

from pathlib import Path
from typing import Union, Dict
from distutils.version import StrictVersion
import time
import yaml
import MEArec as mr
import numpy as np

DEFAULT_DATA_INFO = "./data/mearec"
default_dir = Path(DEFAULT_DATA_INFO)

use_loader = bool(StrictVersion(yaml.__version__) >= StrictVersion('5.0.0'))


def get_config_info(datafolder: Union[str, Path] = None) -> Dict[str, str]:
    """Obtaing infor from file in datafolder.
    The file should be named mearec.conf

    :param datafolder: Folder where config file resides
    :type datafolder: Union[str, Path]
    :return:
        Returns a dictionary with the information about
            * cell_models_folder: folder with cell models
            * recordings_params: recording parameters
            * templates_params: template parameters
            * templates_folder: template folder
            * recordings_folder: recording folder

    :rtype: dict
    """

    if datafolder is None:
        datafolder = default_dir

        with (datafolder / 'mearec.conf').open() as file:
            if use_loader:
                default_info = yaml.load(file, Loader=yaml.FullLoader)
            else:
                default_info = yaml.load(file)
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


def generate_templates(
        config_folder: Union[str, Path] = None,
        cell_models_folder: Union[str, Path] = None,
        templates_folder: Union[str, Path] = None,
        templates_params_file: str = None,
        n_jobs: int = None,
        recompile: bool = None,
        parallel: bool = None,
        verbose: bool = None,
        fname: str = None) -> mr.TemplateGenerator:
    """Function to generate templates.

    :param config_folder: Folder where configuration resides
    :type config_folder: Union[str, Path]
    :param cell_models_folder: Folder of cell_models
    :type cell_models_folder: Union[str, Path]
    :param templates_folder: Folder for templates
    :type templates_folder: Union[str, Path]
    :param templates_params_file: File with templates parameters
    :type templates_params_file: str
    :param n_jobs: Number of jobs
    :type n_jobs: int
    :param recompile: If True, forces compilation
    :type recompile: bool
    :param parallel: If True, enable parallel execution
    :type parallel: bool
    :param verbose: If True, enable verbose output
    :type verbose: bool
    :param fname: Specify the output name
    :type fname: str
    :return: Object TemplateGenerator with template info
    :rtype: mr.TemplateGenerator

    :raises AttributeError: If templates_params_file or templates_folder
        is not defined either by their corresponding variables or by
        the config_folder
    """

    if config_folder is not None:
        config = get_config_info(datafolder=config_folder)

        if templates_params_file is None:
            templates_params_file = config['templates_params']

        if cell_models_folder is None:
            cell_models_folder = config['cell_models_folder']

        if templates_folder is None:
            templates_folder = config['templates_folder']

    if templates_params_file is None:
        raise AttributeError("templates_params_file should be not null")

    with open(templates_params_file, 'r', encoding='utf8') as file:
        if use_loader:
            params_dict = yaml.load(file, Loader=yaml.FullLoader)
        else:
            params_dict = yaml.load(file)
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

    if templates_folder is None:
        raise AttributeError("templates_folder should be not null")

    save_fname = str(Path(templates_folder) / rot / fname)

    mr.save_template_generator(templates, save_fname, verbose=True)
    return templates


def generate_recordings(
        config_folder: Union[str, Path] = None,
        recordings_params_file: Union[str, Path] = None,
        templates_folder: Union[str, Path] = None,
        recordings_folder: Union[str, Path] = None,
        verbose: bool = None,
        njobs: int = None,
        fname: Union[str, Path] = None,
        fs: int = None,
        noise_level: float = 10) -> mr.RecordingGenerator:
    """Function to generate recordings according with some custom parameters
    such as the sampling frequency or the noise_level

    :param config_folder: Folder where configuration file resides
    :type config_folder: Union[str, Path]
    :param recordings_params_file: File with recording parameters
    :type recordings_params_file: Union[str, Path]
    :param templates_folder: Folder where there are the template files
    :type templates_folder: Union[str, Path]
    :param recordings_folder: Folder to save in the recording files
    :type recordings_folder: Union[str, Path]
    :param verbose: If True, enable verbose output
    :type verbose: bool
    :param njobs: Number of jobs for parallel execution
    :type njobs: int
    :param fname: File name to save
    :type fname: Union[str, Path]
    :param fs: Sampling frequency in Hz
    :type fs: int
    :param noise_level: Noise level
    :type noise_level: float
    :return: RecordingGenerator object with information about the generated
        recordings
    :rtype: mr.RecordingGenerator

    :raises AttributeError: If recordings_params_file or recordings_folder
        is not defined either by their corresponding variables or by
        the config_folder
    """

    if config_folder is not None:
        config = get_config_info(datafolder=config_folder)

        if recordings_params_file is None:
            recordings_params_file = config['recordings_params']

        if templates_folder is None:
            templates_folder = config['templates_folder']

        if recordings_folder is None:
            recordings_folder = config['recordings_folder']

    if recordings_params_file is None:
        raise AttributeError("recordings_params_file should be not null")

    with open(recordings_params_file, 'r', encoding='utf8') as file:
        if use_loader:
            params_dict = yaml.load(file, Loader=yaml.FullLoader)
        else:
            params_dict = yaml.load(file)

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
                f'_{duration}_{np.round(noise_level, 2)}uV' \
                f'_{int(fs)}Hz_' \
                f'drift_{time.strftime("%Y-%m-%d_%H-%M")}.h5'
        else:
            fname = f'recordings_{n_neurons}cells_{electrode_name}' \
                f'_{duration}_{np.round(noise_level, 2)}uV' \
                f'_{int(fs)}Hz_' \
                f'{time.strftime("%Y-%m-%d_%H-%M")}.h5'
    n_neurons = info['recordings']['n_neurons']
    electrode_name = info['electrodes']['electrode_name']
    duration = info['recordings']['duration']
    noise_level = info['recordings']['noise_level']

    if recordings_folder is None:
        raise AttributeError("recordings_folder should be not null")

    save_fname = str(Path(recordings_folder) / fname)
    mr.save_recording_generator(recordings, save_fname, verbose=True)
    return recordings


def load_recordings(datafolder: Union[str, Path] = None,
                    verbose: bool = None,
                    noise_level: float = None,
                    fs: int = None) -> mr.RecordingGenerator:
    """ Load the recordings object from file in datafolder

    :param datafolder: Folder where there are recordings files
    :type datafolder: Union[str, Path]
    :param verbose: If True, verbose output
    :type verbose: bool
    :param noise_level: Specify the noise_level
    :type noise_level: float
    :param fs: Specify the sampling frequency in Hz
    :type fs: int
    :return: RecordingGenerator object with recordings info
    :rtype: mr.RecordingGenerator
    """

    if datafolder is None:
        config = get_config_info()
        recordings_folder = config['recordings_folder']
    else:
        recordings_folder = datafolder

    if noise_level is not None:
        recordings = Path(recordings_folder).resolve()
        pattern = f'_{np.round(noise_level, 2)}uV'

        if fs is not None:
            pattern += f'_{int(fs)}Hz'

        recording_files = [f for f in recordings.rglob(f"*{pattern}*") if
                           f.name.endswith(('.h5', '.hdf5'))]
        recording_files.sort(reverse=True)
        if len(recording_files) == 0:
            raise AttributeError(
                recordings,
                ' contains no recordings models with noise_level ',
                noise_level)

        recordings = recording_files[0]
        if verbose:
            print(f'Loading file {recordings}')
        recgen = mr.load_recordings(recordings, verbose=verbose)
    else:
        recgen = mr.load_recordings(recordings_folder, verbose=verbose)
    return recgen


if __name__ == "__main__":
    # tempgen = generate_templates(verbose=True, recompile=True)
    # print(tempgen)
    # recgen = generate_recordings(verbose=True)
    recgen = load_recordings(verbose=True)
    print(recgen)
