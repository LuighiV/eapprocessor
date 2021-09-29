import matplotlib.pylab as plt
import numpy as np


def plotSignals(neogen, crange=None, channels=None,
                plot_spiketrains=True, intensities=None,
                range_spikes=None):

    recordings = neogen["recordings"].recordings[:].T
    spiketrains = neogen["recordings"].spiketrains
    normalized = neogen["normalized"]
    neo = neogen["neo"]
    w = neogen["w"]
    timestamps = np.array(neogen["recordings"].timestamps)

    if channels is None:
        channels = range(len(recordings))

    if crange is None:
        crange = range(len(timestamps))

    for channel in channels:

        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(3, 1, 1)
        ax.plot(
            timestamps[crange],
            recordings[channel][crange],
            label="Recordings")
        if plot_spiketrains:
            plotSpikeTrains(ax=ax, spiketrains=spiketrains,
                            level=np.max(recordings[channel][crange]),
                            upperlimit=timestamps[crange][-1],
                            intensities=intensities,
                            range_spikes=range_spikes)
        ax.legend(loc='best')

        ax = fig.add_subplot(3, 1, 2)
        ax.plot(
            timestamps[crange],
            normalized[channel][crange],
            label="Normalized")

        ax.legend(loc='best')

        if plot_spiketrains:
            plotSpikeTrains(ax=ax, spiketrains=spiketrains,
                            level=np.max(normalized[channel][crange]),
                            upperlimit=timestamps[crange][-1],
                            intensities=intensities,
                            range_spikes=range_spikes)

        ax = fig.add_subplot(3, 1, 3)
        for idx in range(len(neo)):
            ax.plot(timestamps[crange], neo[idx][channel][crange],
                    label=f"w={w[idx]}")

        if plot_spiketrains:
            plotSpikeTrains(ax=ax, spiketrains=spiketrains,
                            level=np.max(neo[-1][channel][crange]),
                            upperlimit=timestamps[crange][-1],
                            intensities=intensities,
                            range_spikes=range_spikes)
        ax.legend(loc='best')


def plotSpikeTrains(ax, spiketrains, level, upperlimit=None, intensities=None,
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
            ax.plot(spiketrain, level * np.ones(len(spiketrain)), '+',
                    color='red', alpha=intensity)


def plotTransientRecordings(recgen, crange=None, channels=None):

    recordings = recgen.recordings[:].T

    timestamps = np.array(recgen.timestamps)

    noise_level = recgen.info["recordings"]["noise_level"]

    if channels is None:
        channels = range(len(recordings))

    if crange is None:
        crange = range(len(timestamps))

    for channel in channels:

        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(
            timestamps[crange],
            recordings[channel][crange],
            label=f"Noise level={noise_level}")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude (uV)")
        ax.set_title(f"Recordings for channel {channel}")
        ax.legend(loc="best")
