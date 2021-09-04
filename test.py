import MEArec as mr
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Qt5Agg')
recgen = mr.load_recordings(
    '/home/luighi/.config/mearec/1.7.2/recordings/' +
    'recordings_10cells_Neuronexus-32_10.0_10uV_27-08-2021_19-57.h5')

# fig, ax = plt.subplots()
fig2, ax2 = plt.subplots()
# mr.plot_recordings(recgen=recgen, ax=ax)
# mr.plot_waveforms(recgen=recgen, ax=ax2)
# mr.plot_rasters(recgen.spiketrains, ax=ax2)
mr.plot_pca_map(recgen, ax=ax2, max_elec=2)

# fig.show()
fig2.show()
