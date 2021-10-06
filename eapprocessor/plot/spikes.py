import matplotlib.pylab as plt
import numpy as np


def plot_spikes_from_neo(neogen):

    spiketrains = neogen["recordings"].spiketrains
    cell_type_list = [spiketrain.annotations["cell_type"] for spiketrain
                      in spiketrains]
    spiketrains_list = [np.array(spiketrain[:]) for spiketrain in spiketrains]
    labels = [str(cell_type) for cell_type in cell_type_list]
    plot_spikes_array(spike_list=spiketrains_list, labels=labels)


def plot_spikes_array(spike_list, labels=[]):

    if len(labels) == 0:
        labels = range(len(spike_list))

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(1, 1, 1)

    for idx, spike in enumerate(spike_list):

        ax.plot(spike, idx * np.ones(spike.shape), '+',
                label=f"Spiketrain {labels[idx]}")

    ax.set_title("Spike trains")
    ax.set_xlabel("Timestamps")
    ax.set_ylabel("Spiketrain index")
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

    return
