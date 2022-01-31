import numpy as np
from eapprocessor.tools.slices import get_all_slices_from_indexes


def estimate_sample_spikes(spikes, timestamps, compacted=True):

    spikes = np.array(spikes).reshape(len(spikes), 1)
    timestamps = np.array(timestamps).reshape(1, len(timestamps))

    spikes_mat = spikes @ np.ones(timestamps.shape)
    timestamps_mat = np.ones(spikes.shape) @ timestamps

    diff_mat = spikes_mat - timestamps_mat
    abs_diff = np.abs(diff_mat)

    # Get the minimum values for each value in spikes
    min_arr = np.amin(abs_diff, axis=1).reshape(len(spikes), 1)
    min_mat = min_arr @ np.ones(timestamps.shape)

    # This will have to values when difference is 0.5
    indexes = (min_mat == abs_diff) * np.ones(abs_diff.shape)

    # Keeping only the maximum indexes for them
    # PD: perhaps ther is a better way to get the maxium index, but this was
    # that I ended up using, if you have another, please consider contribute
    ran = np.arange(timestamps.shape[1]).reshape(timestamps.shape)
    ind_arr = np.ones(spikes.shape) @ ran
    # print(ind_arr)
    ind_values = indexes * ind_arr
    max_index = np.amax(ind_values, axis=1).reshape(len(spikes), 1)
    max_mat = max_index @ np.ones(timestamps.shape)
    indexes = (max_mat == np.abs(ind_arr)) * np.ones(abs_diff.shape)

    errors = indexes * diff_mat

    if compacted:
        indexes = np.sum(indexes, axis=0)
        errors = np.sum(errors, axis=0)
    return indexes, errors


def combine_spiketrains(indexes_list, normalize=True):

    indexes = np.sum(np.array(indexes_list), axis=0)

    if normalize:
        indexes_total = (indexes > 0) * np.ones(indexes.shape)
    else:
        indexes_total = indexes

    return indexes_total


def comparison_detection_spiketrain(reference, test, window=None):

    reference = np.array(reference)
    test = np.array(test)

    # This section induce unexpected results, you must ensure the sizes
    # are equal
    # if len(reference) > len(test):
    #    reference = reference[:len(test)]

    # if len(test) > len(reference):
    #    test = test[:len(reference)]

    if window is None:
        truepositive = reference * test
        variations = test - reference
        falsepositive = np.ones(reference.shape) * (variations == 1)
        falsenegative = np.ones(reference.shape) * (variations == -1)
        truenegative = np.ones(reference.shape) * ((reference + test) == 0)
    else:
        original_range = np.arange(len(reference))
        actual_indexes = original_range[reference > 0]
        slices, labels = get_all_slices_from_indexes(actual_indexes,
                                                     window,
                                                     (0, len(reference) - 1))

        tp_arr = np.array(
            [np.sum(test[np.arange(sl[0], sl[1] + 1)])
             for sl in slices[labels > 0]])
        truepositive = np.sum(tp_arr > 0)
        fp_arr = np.array(
            [np.sum(test[np.arange(sl[0], sl[1] + 1)])
             for sl in slices[labels == 0]])
        falsepositive = np.sum(fp_arr > 0)
        falsenegative = len(slices[labels > 0]) - truepositive
        truenegative = len(slices[labels == 0]) - falsepositive

    return {
        "truepositive": np.sum(truepositive),
        "falsepositive": np.sum(falsepositive),
        "falsenegative": np.sum(falsenegative),
        "truenegative": np.sum(truenegative)
    }


def get_false_negatives(reference, test):
    variations = test - reference
    return np.ones(reference.shape) * (variations == -1)


def get_false_negatives_times(reference, test, timestamps):

    positions = get_false_negatives(reference=reference, test=test)
    indexes = np.arange(len(positions))[positions > 0]
    return timestamps[indexes]


def comparison_detection_spiketrain_array(arrayreference, test, window=None):

    return np.array([comparison_detection_spiketrain(reference=reference,
                                                     test=test,
                                                     window=window)
                     for reference in arrayreference], dtype=object)


def comparison_detection_array_spiketrain(reference, arraytest, window=None):

    return np.array([comparison_detection_spiketrain(reference=reference,
                                                     test=test,
                                                     window=window)
                     for test in arraytest], dtype=object)


def comparison_detection_array_spiketrain_array(arrayreference,
                                                arraytest,
                                                window=None):

    return np.array([comparison_detection_spiketrain_array(
        arrayreference=arrayreference, test=test, window=window)
        for test in arraytest])


def select_comparison(array_comparison,
                      range_reference=None, range_test=None):

    if range_test is not None:
        array_comparison = array_comparison[range_test]

    if range_reference is not None:
        array_comparison = array_comparison[:, range_reference]

    return array_comparison


def calc_accuracy(dic):

    tp = dic["truepositive"]
    fp = dic["falsepositive"]
    fn = dic["falsenegative"]

    return (tp) / (tp + fp + fn)


def convert_to_accuracy(array_comparison,
                        range_reference=None,
                        range_test=None):

    array_comparison = select_comparison(array_comparison=array_comparison,
                                         range_reference=range_reference,
                                         range_test=range_test)
    accuracy = []

    for test in array_comparison:

        if isinstance(test, dict):
            accuracy += [calc_accuracy(test)]

        else:
            accuracy_ref = []
            for reference in test:
                accuracy_ref += [calc_accuracy(reference)]

            accuracy += [accuracy_ref]

    return np.array(accuracy)


def convert_to_accuracy_list(array_comparison_list,
                             range_reference=None,
                             range_test=None):

    accuracy_list = []
    for array_comparison in array_comparison_list:

        if len(array_comparison.shape) > 2:

            accuracy_arr = [convert_to_accuracy_list(
                comparison,
                range_reference=range_reference,
                range_test=range_test)
                for comparison in array_comparison]

        else:
            accuracy_arr = convert_to_accuracy(array_comparison,
                                               range_reference=range_reference,
                                               range_test=range_test)

        accuracy_list += [accuracy_arr]

    return np.array(accuracy_list)


def convert_to_roc(array_comparison,
                   range_reference=None,
                   range_test=None):

    array_comparison = select_comparison(array_comparison=array_comparison,
                                         range_reference=range_reference,
                                         range_test=range_test)

    tpr_arr = []
    fpr_arr = []
    for test in array_comparison:

        if isinstance(test, dict):
            tp = test["truepositive"]
            fp = test["falsepositive"]
            tn = test["truenegative"]
            fn = test["falsenegative"]

            tpr_arr += [tp / (tp + fn)]
            fpr_arr += [fp / (fp + tn)]

        else:

            tpr_ref = []
            fpr_ref = []
            for reference in test:

                tp = reference["truepositive"]
                fp = reference["falsepositive"]
                tn = reference["truenegative"]
                fn = reference["falsenegative"]

                tpr_ref += [tp / (tp + fn)]
                fpr_ref += [fp / (fp + tn)]

            tpr_arr += [tpr_ref]
            fpr_arr += [fpr_ref]

    return np.array(tpr_arr), np.array(fpr_arr)


def convert_to_roc_list(array_comparison_list,
                        range_reference=None,
                        range_test=None):

    tpr_arr_list = []
    fpr_arr_list = []
    for array_comparison in array_comparison_list:

        if len(array_comparison.shape) > 2:

            results = [(convert_to_roc(comparison,
                                       range_reference=range_reference,
                                       range_test=range_test))
                       for comparison in array_comparison]

            tpr_arr = np.array([result[0] for result in results])
            fpr_arr = np.array([result[1] for result in results])

        else:
            tpr_arr, fpr_arr = convert_to_roc(array_comparison,
                                              range_reference=range_reference,
                                              range_test=range_test)

        tpr_arr_list += [tpr_arr]
        fpr_arr_list += [fpr_arr]

    return np.array(tpr_arr_list), np.array(fpr_arr_list)


if __name__ == "__main__":

    spikes = [2.6, 3.5, 4.5, 6.2]
    timestamps = [0, 1, 2, 3, 4, 5, 6, 7]

    indexes, errors = estimate_sample_spikes(
        spikes=spikes, timestamps=timestamps)
    print(indexes)
    print(errors)

    reference = [0, 1, 0, 1, 0, 1, 1, 0]
    result = comparison_detection_spiketrain(reference=reference, test=indexes)

    print(result)
