import numpy as np


def calcDistancesFromRecordings(recgen):

    neurons_positions = recgen.template_locations
    electrodes_positions = recgen.channel_positions

    return calcDistances(
        electrodes_positions=electrodes_positions,
        neurons_positions=neurons_positions,
    )


def calcDistances(electrodes_positions, neurons_positions):

    neurons_positions = np.array(neurons_positions)
    electrodes_positions = np.array(electrodes_positions)

    distances = []
    for pos in neurons_positions:

        diff = electrodes_positions - \
            np.ones((electrodes_positions.shape[0], 1)) @ \
            pos.reshape(1, electrodes_positions.shape[1])

        distances += [np.sqrt(np.sum(np.square(diff), axis=1))]

    return np.array(distances).T


def getOrderByChannels(distances):

    return np.argsort(distances, axis=1)


def convertDistancesToIntensity(distances, max_value=1, min_value=0.1):

    approxIntensity = distances**(-2)

    minimum = np.min(approxIntensity)
    maximum = np.max(approxIntensity)

    m = (max_value - min_value) / (maximum - minimum)

    amplitude = (approxIntensity - np.ones(approxIntensity.shape)
                 * minimum) * m + min_value

    return amplitude


if __name__ == "__main__":

    neuron = np.array([[0, 1, 1], [1, 1, 2]])
    electrodes = np.array([[1, 1, 1], [2, 2, 2], [0, 0, 0]])
    print(neuron.shape)
    print(electrodes.shape)

    distances = calcDistances(electrodes, neuron)
    print(distances)

    orders = getOrderByChannels(distances)
    print(orders)

    amplitude = convertDistancesToIntensity(distances)
    print(amplitude)
