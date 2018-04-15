import numpy as np

def load_data_discrete(path, size=None):
    X = np.load(path + '/images.npy').astype(np.uint8)
    y = np.load(path + '/answers.npy')
    return np.unpackbits(X[:size], axis=2), y[:size]