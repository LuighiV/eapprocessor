import matplotlib.pylab as plt


def plot_electrodes_axons(recgen):

    electrodes_positions = recgen.channel_positions[:].T
    neurons_positions = recgen.template_locations[:].T
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(projection='3d')

    # Plot electrodes
    ax.scatter(electrodes_positions[1],
               electrodes_positions[2],
               zs=electrodes_positions[0],
               zdir='z',
               marker='o',
               label="Electrodes")

    ax.scatter(neurons_positions[1],
               neurons_positions[2],
               zs=neurons_positions[0],
               zdir='z',
               marker='^',
               label="Soma neurons")

    ax.legend(loc="best")
    plt.show()
