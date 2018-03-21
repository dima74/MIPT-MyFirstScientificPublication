import pickle

def read_data(filename):
    """
    :return: (X, y, X_skeleton)
        X.shape == (N, 28*28)
        y.shape == (N)
        X_skeleton.shape == (N, 8 * number_edges)
            X_skeleton == [edge1, edge2, ...]
            edge == node1, node2
            node == x, y, degree, radial
    """
    with open(filename, 'rb') as input:
        data = pickle.load(input)
        X, y, X_skeleton = data['data'], data['labels'], data['skel_features']
        return X, y, X_skeleton

X_test, y_test, X_test_skeleton = read_data('data/test_info')

with open('single-image.pickle', 'wb') as output:
    data = {
        'x': X_test[0],
        'x_skeleton': X_test_skeleton[0],
    }
    pickle.dump(data, output, protocol=pickle.HIGHEST_PROTOCOL)
