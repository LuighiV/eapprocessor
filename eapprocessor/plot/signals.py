import matplotlib.pylab as plt
import numpy as np


def plot_level_reference(ax, level):

    ax.axhline(y=level, color='grey', linestyle="--")


def plot_signals(neogen,
                 crange=None,
                 t_start=None,
                 t_stop=None,
                 channels=None,
                 include_spiketrains=True,
                 intensities=None,
                 range_spikes=None,
                 neo_idx=None,
                 include_threshold=False,
                 include_detected_spikes=False,
                 th_recordings=None,
                 th_normalized=None,
                 th_neo=None,
                 th_n=0
                 ):

    recordings = neogen["recordings"].recordings[:].T
    spiketrains = neogen["recordings"].spiketrains
    normalized = neogen["normalized"]
    neo = neogen["neo"]
    w = neogen["w"]
    timestamps = np.array(neogen["recordings"].timestamps)

    if channels is None:
        channels = range(len(recordings))

    if crange is None:
        if t_stop is None:
            t_stop = timestamps[-1]
        if t_start is None:
            t_start = timestamps[0]

        crange = (timestamps >= t_start) * (timestamps <= t_stop)

    if neo_idx is None:
        neo_idx = range(len(neo))

    neo = neo[neo_idx]

    for channel in channels:

        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(3, 1, 1)
        ax.plot(
            timestamps[crange],
            recordings[channel][crange],
            label="Recordings")
        if include_threshold:
            if channel in th_recordings["channels"]:
                ch_idx = th_recordings["channels"].index(channel)
                th_indexes = th_recordings["indexes"][ch_idx][th_n][crange]

                ax.plot(
                    timestamps[crange][th_indexes > 0],
                    recordings[channel][crange][th_indexes > 0],
                    '.'
                )

                plot_level_reference(
                    ax, th_recordings["thresholds"][ch_idx][th_n])

                if include_detected_spikes:

                    th_indexes = th_recordings[
                        "indexes_spikes"][ch_idx][th_n][crange]
                    ax.plot(
                        timestamps[crange][th_indexes > 0],
                        recordings[channel][crange][th_indexes > 0],
                        'x'
                    )

        if include_spiketrains:
            plot_spiketrains(ax=ax, spiketrains=spiketrains,
                             level=np.max(recordings[channel][crange]),
                             lowerlimit=timestamps[crange][0],
                             upperlimit=timestamps[crange][-1],
                             intensities=intensities,
                             range_spikes=range_spikes)
        ax.legend(loc='best')

        ax = fig.add_subplot(3, 1, 2)
        ax.plot(
            timestamps[crange],
            normalized[channel][crange],
            label="Normalized")
        if include_threshold:
            if channel in th_normalized["channels"]:
                ch_idx = th_normalized["channels"].index(channel)
                th_indexes = th_normalized["indexes"][ch_idx][th_n][crange]

                ax.plot(
                    timestamps[crange][th_indexes > 0],
                    normalized[channel][crange][th_indexes > 0],
                    '.'
                )

                plot_level_reference(
                    ax, th_normalized["thresholds"][ch_idx][th_n])

                if include_detected_spikes:

                    th_indexes = th_normalized[
                        "indexes_spikes"][ch_idx][th_n][crange]
                    ax.plot(
                        timestamps[crange][th_indexes > 0],
                        normalized[channel][crange][th_indexes > 0],
                        'x'
                    )

        ax.legend(loc='best')

        if include_spiketrains:
            plot_spiketrains(ax=ax, spiketrains=spiketrains,
                             level=np.max(normalized[channel][crange]),
                             lowerlimit=timestamps[crange][0],
                             upperlimit=timestamps[crange][-1],
                             intensities=intensities,
                             range_spikes=range_spikes)

        ax = fig.add_subplot(3, 1, 3)
        for idx, _ in enumerate(neo):
            ax.plot(timestamps[crange], neo[idx][channel][crange],
                    label=f"w={w[idx]}")

            if include_threshold:
                if channel in th_neo["channels"]:
                    ch_idx = th_neo["channels"].index(channel)
                    th_indexes = th_neo["indexes"][idx][ch_idx][th_n][crange]

                    ax.plot(
                        timestamps[crange][th_indexes > 0],
                        neo[idx][channel][crange][th_indexes > 0],
                        '.'
                    )

                    plot_level_reference(
                        ax, th_neo["thresholds"][idx][ch_idx][th_n])

                    if include_detected_spikes:

                        th_indexes = th_neo[
                            "indexes_spikes"][idx][ch_idx][th_n][crange]
                        ax.plot(
                            timestamps[crange][th_indexes > 0],
                            neo[idx][channel][crange][th_indexes > 0],
                            'x'
                        )

        if include_spiketrains:
            plot_spiketrains(ax=ax, spiketrains=spiketrains,
                             level=np.max(neo[-1][channel][crange]),
                             lowerlimit=timestamps[crange][0],
                             upperlimit=timestamps[crange][-1],
                             intensities=intensities,
                             range_spikes=range_spikes)
        ax.legend(loc='best')


def plot_spiketrains(ax,
                     spiketrains,
                     level,
                     lowerlimit=None,
                     upperlimit=None,
                     intensities=None,
                     range_spikes=None):

    spiketrains = np.array(spiketrains, dtype=object)
    if range_spikes is not None:
        spiketrains = spiketrains[range_spikes]

    if intensities is None:
        intensities = np.ones(len(spiketrains))
    elif range_spikes is not None:
        intensities = intensities[range_spikes]

    for idx in range(len(spiketrains)):
        spiketrain = spiketrains[idx]
        intensity = intensities[idx]
        if upperlimit is not None:
            spiketrain = spiketrain[spiketrain < upperlimit]

        if lowerlimit is not None:
            spiketrain = spiketrain[spiketrain > lowerlimit]

        ax.plot(spiketrain, level * np.ones(len(spiketrain)), '+',
                color='red', alpha=intensity)


def plot_transient_neo(neogen,
                       crange=None,
                       t_start=None,
                       t_stop=None,
                       channels=None,
                       labels=None,
                       marker=None,
                       w_indexes=None,
                       axes=None):

    recgen = neogen["recordings"]
    adcinfo = neogen["adcinfo"]
    recordings = recgen.recordings[:].T
    neo = neogen["neo"]
    w = np.array(neogen["w"])

    if w_indexes is not None:
        w = w[w_indexes]

    timestamps = np.array(recgen.timestamps)

    noise_level = recgen.info["recordings"]["noise_level"]
    fs = recgen.info["recordings"]["fs"]

    if channels is None:
        channels = np.arange(len(recordings))

    if crange is None:

        if t_stop is None:
            t_stop = timestamps[-1]
        if t_start is None:
            t_start = timestamps[0]

        crange = (timestamps >= t_start) * (timestamps <= t_stop)

    if marker is None:
        marker = '-'

    for idx, channel in enumerate(channels):

        if axes is None:
            _, ax = plt.subplots(len(w), 1, figsize=(12, 12))
        else:
            if isinstance(axes, (list, np.ndarray)):
                ax = axes[idx]
            else:
                ax = axes

        if labels is None:
            label = (f"Noise level={noise_level}, fs={fs}, "
                     f"resolution={adcinfo['resolution']}")
        else:
            if isinstance(labels, list):
                label = labels[idx]
            else:
                label = labels

        for w_i, w_value in enumerate(w):

            if isinstance(ax, (list, np.ndarray)):
                cax = ax[w_i]
            else:
                cax = ax

            cax.plot(
                timestamps[crange],
                neo[w_i][channel][crange],
                marker,
                label=label + f", w={w_value}")
            cax.set_xlabel("Time (s)")
            cax.set_ylabel("Amplitude")
            cax.legend(loc="best")
            if w_i == 0:
                cax.set_title(f"NEO values for channel {channel}")


def plot_transient_converted(adcgen,
                             crange=None,
                             t_start=None,
                             t_stop=None,
                             channels=None,
                             labels=None,
                             marker=None,
                             axes=None):

    recgen = adcgen["recordings"]
    adcinfo = adcgen["adcinfo"]
    recordings = recgen.recordings[:].T
    samples = adcgen["adc"]

    timestamps = np.array(recgen.timestamps)

    noise_level = recgen.info["recordings"]["noise_level"]
    fs = recgen.info["recordings"]["fs"]

    if channels is None:
        channels = np.arange(len(recordings))

    if crange is None:

        if t_stop is None:
            t_stop = timestamps[-1]
        if t_start is None:
            t_start = timestamps[0]

        crange = (timestamps >= t_start) * (timestamps <= t_stop)

    if marker is None:
        marker = '-'

    for idx, channel in enumerate(channels):

        if axes is None:
            fig = plt.figure(figsize=(12, 6))
            ax = fig.add_subplot(1, 1, 1)
        else:
            if isinstance(axes, list):
                ax = axes[idx]
            else:
                ax = axes

        if labels is None:
            label = (f"Noise level={noise_level}, fs={fs}, "
                     f"resolution={adcinfo['resolution']}")
        else:
            if isinstance(labels, list):
                label = labels[idx]
            else:
                label = labels

        ax.plot(
            timestamps[crange],
            samples[channel][crange],
            marker,
            label=label)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.set_title(f"Converted values for channel {channel}")
        ax.legend(loc="best")


def plot_transient_recordings(recgen,
                              crange=None,
                              t_start=None,
                              t_stop=None,
                              channels=None,
                              labels=None,
                              marker=None,
                              axes=None):

    recordings = recgen.recordings[:].T

    timestamps = np.array(recgen.timestamps)

    noise_level = recgen.info["recordings"]["noise_level"]
    fs = recgen.info["recordings"]["fs"]

    if channels is None:
        channels = np.arange(len(recordings))

    if crange is None:

        if t_stop is None:
            t_stop = timestamps[-1]
        if t_start is None:
            t_start = timestamps[0]

        crange = (timestamps >= t_start) * (timestamps <= t_stop)

    if marker is None:
        marker = '-'

    for idx, channel in enumerate(channels):

        if axes is None:
            fig = plt.figure(figsize=(12, 6))
            ax = fig.add_subplot(1, 1, 1)
        else:
            if isinstance(axes, list):
                ax = axes[idx]
            else:
                ax = axes

        if labels is None:
            label = f"Noise level={noise_level}, fs={fs}"
        else:
            if isinstance(labels, list):
                label = labels[idx]
            else:
                label = labels

        ax.plot(
            timestamps[crange],
            recordings[channel][crange],
            marker,
            label=label)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude (uV)")
        ax.set_title(f"Recordings for channel {channel}")
        ax.legend(loc="best")


def plot_recordings_list(recgen_list,
                         crange=None,
                         t_start=None,
                         t_stop=None,
                         channels=None,
                         group_by_channel=True,
                         marker=None,
                         labels=None,
                         axes=None):

    if axes is None:
        if group_by_channel:
            axes = []
            for _ in channels:
                fig = plt.figure(figsize=(12, 6))
                axes += [fig.add_subplot(1, 1, 1)]
        else:
            fig = plt.figure(figsize=(12, 6))
            axes = fig.add_subplot(1, 1, 1)

    for recgen in recgen_list:

        plot_transient_recordings(recgen=recgen,
                                  crange=crange,
                                  t_start=t_start,
                                  t_stop=t_stop,
                                  channels=channels,
                                  labels=labels,
                                  marker=marker,
                                  axes=axes)
