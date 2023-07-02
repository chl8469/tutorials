import numpy as np


def make_dataset(data, label, window_size=365, predsize = None):
    feature_list = []
    label_list = []

    if isinstance(predsize, int):
        for i in range(len(data) - (window_size + predsize)):
            feature_list.append(np.array(data.iloc[i:i+window_size]))
            label_list.append(np.array(label.iloc[i+window_size:i+window_size+predsize]))
    else:
        for i in range(len(data) - window_size):
            feature_list.append(np.array(data.iloc[i:i+window_size]))
            label_list.append(np.array(label.iloc[i+window_size]))

    return np.array(feature_list), np.array(label_list)