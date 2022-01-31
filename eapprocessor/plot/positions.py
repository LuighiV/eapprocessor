import matplotlib.pylab as plt


def plot_electrodes_axons(recgen):

    electrodes_positions = recgen.channel_positions[:].T
    neurons_positions = recgen.template_locations[:].T
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(projection='3d')

    # Plot electrodes
    ax.scatter(electrodes_positions[1],
               electrodes_positions[2],
               zs=electrodes_positions[0],
               zdir='z',
               marker='o',
               label="Electrode positions")

    ax.scatter(neurons_positions[1],
               neurons_positions[2],
               zs=neurons_positions[0],
               zdir='z',
               marker='^',
               label="Neuron soma positions")

    ax.legend(loc="best")
    ax.set_xlabel("Distance in x (um)")
    ax.set_ylabel("Distance in y (um)")
    ax.set_zlabel("Depth in z (um)")
    plt.show()

    return ax, fig
