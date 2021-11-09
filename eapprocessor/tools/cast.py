def convert_to_list(dictionary):

    return convert_to_list_recursively(dictionary)


def convert_to_list_recursively(dictionary):

    keys = sorted(dictionary.keys())

    list_items = []
    for key in keys:
        if isinstance(dictionary[key], dict):
            value = convert_to_list_recursively(dictionary[key])
        else:
            value = dictionary[key]
        list_items += [value]
    return list_items


if __name__ == "__main__":

    import numpy as np
    ran = range(3)

    dic = {}
    for i in ran:
        dic[str(i)] = {}
        for j in ran:
            dic[str(i)][str(j)] = np.arange(i + j)

    test_list = convert_to_list(dic)
    print(test_list)
