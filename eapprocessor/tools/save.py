from pathlib import Path
import h5py
import MEArec as mr


def save_converted_values(adcgen, filename=None, is_lcadc=False):

    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(filename, 'w') as f:
        save_converted_values_to_file(adcgen, f, is_lcadc=is_lcadc)


def save_converted_values_to_file(adcgen, f, is_lcadc=False):

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
        save_neo_values_to_file(neogen, f, is_lcadc=is_lcadc)


def save_neo_values_to_file(neogen, f, is_lcadc=False):

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

    save_converted_values_to_file(neogen, f, is_lcadc=is_lcadc)


def save_array(array, filename=None, path='array'):
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(filename, 'w') as f:
        f.create_dataset(path, data=array)


def save_indexes_and_counts(dic, filename=None, is_lcadc=False, path='',
                            is_neo=False, w=None):

    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(filename, 'w') as f:
        create_index_and_count_dataset(
            dic, f, path=path, is_lcadc=is_lcadc, is_neo=is_neo, w=w)


def save_threshold_values(thgen, filename=None):
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(filename, 'w') as f:
        save_threshold_values_to_file(thgen, f)


def save_threshold_values_to_file(thgen, f):

    if len(thgen["threshold"]) > 0:

        threshold = thgen["threshold"]
        if len(threshold["recordings"]) > 0:
            create_index_and_count_dataset(
                threshold["recordings"], f, "threshold/recordings")

        if len(threshold["normalized"]) > 0:
            create_index_and_count_dataset(
                threshold["normalized"], f, "threshold/normalized")

        if len(threshold["neo"]) > 0:
            for wdx in range(len(threshold["neo"])):
                create_index_and_count_dataset(
                    threshold["neo"], f, f"threshold/neo/{wdx}")

    save_neo_values_to_file(thgen, f)


def save_evaluation_per_channel(array, f, channels, path="",
                                is_neo=False, w=None):

    if is_neo:
        for w_idx, _ in enumerate(w):
            for channel_idx, _ in enumerate(channels):
                f.create_dataset(
                    path + str(w_idx) + '/' + str(channel_idx),
                    data=array[w_idx][channel_idx])
    else:
        for channel_idx, _ in enumerate(channels):
            f.create_dataset(
                path + str(channel_idx),
                data=array[channel_idx])


def create_index_and_count_dataset(data, f, path="",
                                   is_lcadc=False,
                                   is_neo=False,
                                   w=None):

    if is_lcadc:

        if "source_file" in data.keys():
            f[path + 'source_file'] = data["source_file"]

        if len(data["channels"]) > 0:
            f.create_dataset(
                path + 'channels',
                data=data["channels"])
        else:
            raise AttributeError("Dataset must have channel info")

        if data["count_thresholds"]:
            f[path + "count_thresholds"] = data["count_thresholds"]

        keys_arrays = ["thresholds", "counts", "counts_spikes"]

        for key in keys_arrays:
            if len(data[key]) > 0:
                f.create_dataset(path + key, data=data[key])

        keys = ["indexes", "indexes_spikes"]

        for key in keys:
            if len(data[key]) > 0:
                save_evaluation_per_channel(data[key], f,
                                            data["channels"],
                                            path=path + f"{key}/",
                                            is_neo=is_neo,
                                            w=w)
    else:
        mr.save_dict_to_hdf5(data, f, path)
