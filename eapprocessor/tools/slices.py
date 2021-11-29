import numpy as np


def get_slices_from_indexes(indexes_array, N_samples, limits):

    slices = []
    for test_index in indexes_array:
        lower_limit = max(test_index - int(N_samples / 2), limits[0])
        upper_limit = min(test_index + int(N_samples / 2), limits[1])

        slices.append([lower_limit, upper_limit])

    return slices


def get_slices_from_range(positive_slices, N_samples, limits):

    n_slices = []
    labels = []
    lower_limit = limits[0]

    for c_slice in positive_slices:
        upper_limit = c_slice[0] - 1

        slices = split_range((lower_limit, upper_limit), N_samples)
        c_labels = [0] * len(slices)

        n_slices.extend(slices)
        labels.extend(c_labels)

        n_slices.append(c_slice)
        labels.append(1)
        lower_limit = c_slice[1] + 1

    if positive_slices[-1][1] < limits[1]:
        slices = split_range((lower_limit, limits[1]), N_samples)
        c_labels = [0] * len(slices)

        n_slices.extend(slices)
        labels.extend(c_labels)

    assert len(n_slices) == len(labels)
    return np.array(n_slices), np.array(labels)


def split_range(limits, N_samples):
    lower_limit = limits[0]
    upper_limit = limits[1]

    n_slices = []
    estimate_number_slices = int(
        round((upper_limit - lower_limit) / N_samples))
    if estimate_number_slices > 0:
        actual_number_samples = int(
            round((upper_limit - lower_limit) / estimate_number_slices))
        for i in range(estimate_number_slices - 1):
            n_slices.append([
                lower_limit + i * actual_number_samples,
                lower_limit + (i + 1) * actual_number_samples - 1])
        n_slices.append([lower_limit + (estimate_number_slices - 1)
                         * actual_number_samples, upper_limit])

    else:
        n_slices.append([lower_limit, upper_limit])

    return n_slices


def get_all_slices_from_indexes(indexes_array, N_samples, limits):
    positive_slices = get_slices_from_indexes(indexes_array, N_samples, limits)

    return get_slices_from_range(positive_slices, N_samples, limits)
