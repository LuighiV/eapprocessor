#!/bin/python3
import numpy as np


def apply_neo_to_array(values, w=1):
    print("Apply to recording with w=", w)
    newarray = np.array(values)
    # for idx in range(len(values))[w:-w]:
    #     newarray[idx] = values[idx]**2 - values[idx + w] * values[idx - w]
    # return newarray

    operation = (newarray**2 -
                 np.roll(newarray, w) * np.roll(newarray, -w))

    mask = (np.arange(len(newarray)) >= w) * (np.arange(len(newarray))
                                              < len(newarray) - w)

    return operation * mask + newarray * (~mask)


if __name__ == "__main__":

    import matplotlib.pylab as plt
    array = np.array([0, 3, 4, 3, 6, 7, 8, 10])
    neoarray = apply_neo_to_array(values=array)
    print(array)
    print(neoarray)

    plt.plot(array)
    plt.plot(neoarray)
    plt.show()
