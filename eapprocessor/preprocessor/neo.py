#!/bin/python3
import numpy as np


def apply_neo_to_array(values, w=1):
    newarray = np.array(values)
    for idx in range(len(values))[w:-w]:
        newarray[idx] = values[idx]**2 - values[idx + w] * values[idx - w]
    return newarray


if __name__ == "__main__":

    import matplotlib.pylab as plt
    array = np.array([0, 3, 4, 3, 6, 7, 8, 10])
    neoarray = apply_neo_to_array(values=array)
    print(array)
    print(neoarray)

    plt.plot(array)
    plt.plot(neoarray)
    plt.show()
