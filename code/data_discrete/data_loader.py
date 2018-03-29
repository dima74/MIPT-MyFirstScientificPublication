import numpy as np

def load_symbols(path, size = None):
    X = np.load(path + '/images.npy')
    X.dtype=np.uint8
    y = np.load(path + '/answers.npy')
    return np.unpackbits(X[:size], axis = 2), y
