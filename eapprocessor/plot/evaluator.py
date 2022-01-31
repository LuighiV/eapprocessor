import matplotlib.pylab as plt

import numpy as np


def plot_counts_evaluator(counts, neogen, channels_idx=None):

    if "channels" in counts.keys():
        channels = np.array(counts["channels"])
    else:
        channels = np.arange(len(counts["recordings"]))

    if channels_idx is not None:
        channels = channels[channels_idx]

    figure_list = []
    for chidx in range(len(channels)):

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(counts["recordings"][chidx], label="recordings")
        ax.plot(counts["normalized"][chidx], label="normalized")

        for idx in range(len(counts["neo"])):
            ax.plot(counts["neo"][idx][chidx], label=f"w={neogen['w'][idx]}")

        noise_level = neogen["recordings"].info["recordings"]["noise_level"]
        ax.set_xlabel("Threshold/Amax")
        ax.set_ylabel("Samples over threshold")
        ax.set_title(f"Analysis with noise level={noise_level}, "
                     f"Channel={channels[chidx]}")
        ax.legend()
        ax.grid()

        figure_list.append(fig)

    return figure_list


def plot_accuracy_evaluator(truepositive, falsenegative, th_level=None):

    y_offset = np.zeros(len(truepositive))
    fig = plt.figure(figsize=(6, 4))

    bar_width = 0.5
    ax = fig.add_subplot(1, 1, 1)
    ax.bar(range(len(truepositive)), truepositive, bar_width,
           bottom=y_offset, color="blue", edgecolor="blue",
           label="True positive")
    y_offset += truepositive

    ax.bar(range(len(falsenegative)), falsenegative, bar_width,
           bottom=y_offset, color="white", edgecolor="blue", hatch='////',
           label="False negative")

    ax.set_xlabel("Spiketrain index")
    ax.set_ylabel("Number of spikes")
    if th_level is None:
        ax.set_title("Detection rate")
    else:
        ax.set_title(
            f"Detection rate at the relative threshold level={th_level}")

    ax.legend(loc="best")

    return fig


def plot_accuracy(reference, accuracy, label, ax=None):

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

    ax.plot(reference, accuracy, '.--', label=label)


def plot_accuracy_list(accuracy_list, labels,
                       reference=None,
                       spiketrains_labels=None,
                       append_title=None):

    if append_title is None:
        append_title = ""

    # Evaluate if list is for various spiketrains
    if len(accuracy_list[0].shape) == 2:
        n_spiketrains = accuracy_list[0].shape[1]

        for idx in range(n_spiketrains):
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            for idx_fpr, accuracy in enumerate(accuracy_list):

                if reference is None:
                    reference = np.arange(len(accuracy[:, idx]))

                plot_accuracy(reference,
                              accuracy[:, idx],
                              label=labels[idx_fpr],
                              ax=ax)
            ax.legend(loc="best")
            ax.set_xlabel("Threshold reference")
            ax.set_ylabel("Accuracy")
            ax.set_title(f"Accuracy for spiketrain {spiketrains_labels[idx]}"
                         f"{append_title}")
    else:

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        for idx_fpr, accuracy in enumerate(accuracy_list):

            if reference is None:
                reference = np.arange(len(accuracy[:]))
            plot_accuracy(reference,
                          accuracy[:],
                          label=labels[idx_fpr],
                          ax=ax)
        ax.legend(loc="best")
        ax.set_xlabel("Threshold reference")
        ax.set_ylabel("Accuracy")
        ax.set_title("Accuracy curve")


def plot_roc(fpr, tpr, label, ax=None):

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

    ax.plot(fpr, tpr, '.--', label=label)


def plot_roc_list(fpr_list, tpr_list, labels,
                  spiketrains_labels=None,
                  append_title=None):

    if append_title is None:
        append_title = ""

    figure_list =[]
    # Evaluate if list is for various spiketrains
    if len(fpr_list[0].shape) == 2:
        n_spiketrains = fpr_list[0].shape[1]

        for idx in range(n_spiketrains):
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            for idx_fpr in range(len(fpr_list)):

                plot_roc(fpr_list[idx_fpr][:, idx],
                         tpr_list[idx_fpr][:, idx],
                         label=labels[idx_fpr],
                         ax=ax)
            ax.legend(loc="best")
            ax.set_xlabel("FPR(1-specificity)")
            ax.set_ylabel("TPR(sensitivity)")
            ax.set_title(f"ROC for spiketrain {spiketrains_labels[idx]}"
                         f"{append_title}")
            figure_list.append(fig)
        return figure_list

    else:

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        for idx_fpr in range(len(fpr_list)):

            plot_roc(fpr_list[idx_fpr][:],
                     tpr_list[idx_fpr][:],
                     label=labels[idx_fpr],
                     ax=ax)
        ax.legend(loc="best")
        ax.set_xlabel("FPR(1-specificity)")
        ax.set_ylabel("TPR(sensitivity)")
        ax.set_title("ROC curve")

        return fig
