import numpy as np


def project_values_array_list_to_indexes_array(
        original_indexes,
        values_array_list,
        indexes_array,
        default=0):

    arr = []
    for values_array in values_array_list:
        arr += [project_values_array_to_indexes_array(original_indexes,
                                                      values_array,
                                                      indexes_array,
                                                      default=default)]
    return np.array(arr)


def project_values_array_to_indexes_array(original_indexes,
                                          values_array,
                                          indexes_array,
                                          default=0):
    arr = []
    for idx, values in enumerate(values_array):
        arr += [project_values_array_to_indexes(original_indexes,
                                                values,
                                                indexes_array[idx],
                                                default=default)]

    return np.array(arr)


def project_values_array_to_indexes(original_indexes,
                                    dataset_values,
                                    indexes,
                                    default=0):

    dataset_values = np.array(dataset_values)
    indexes = np.array(indexes)
    base = np.ones((len(dataset_values), len(original_indexes))) * default

    base[:, indexes] = dataset_values

    return base


def project_to_indexes(original_indexes, values, indexes, default=0):

    original_indexes = np.array(original_indexes)
    values = np.array(values)
    indexes = np.array(indexes)
    base = np.ones(original_indexes.shape) * default

    base[indexes] = values

    return base


if __name__ == "__main__":

    indexes = [4, 5, 9, 12]
    values = [0, 1, 0, 1]
    original = np.arange(15)

    projected = project_to_indexes(original, values, indexes)
    print(projected)

    arr_values = [[0, 0, 1, 1], [1, 1, 0, 1], [0, 1, 1, 0]]

    projected_arr = project_values_array_to_indexes(original,
                                                    arr_values, indexes)

    print(projected_arr)
