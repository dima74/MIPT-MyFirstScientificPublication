import numpy as np

def batch_loader(path, num_batches=100):
    for i in range(num_batches):
        X = np.load(path + '/images/{}.npy'.format(i)).astype(np.uint8)
        y = np.load(path + '/answers/{}.npy'.format(i))
        yield np.unpackbits(X, axis=2), y

def load_data_discrete(path, size):
    BATCH_SIZE = 10000
    if size is None:
        size = 100 * BATCH_SIZE

    X_batches = []
    y_batches = []
    generator = batch_loader(path)
    while len(X_batches) * BATCH_SIZE < size:
        X_batch, y_batch = next(generator)
        assert len(X_batch) == BATCH_SIZE and len(y_batch) == BATCH_SIZE
        X_batches.append(X_batch)
        y_batches.append(y_batch)

    X = np.row_stack(X_batches)
    y = np.hstack(y_batches)
    return X[:size], y[:size]