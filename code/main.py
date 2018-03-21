import matplotlib
from tqdm import tqdm
matplotlib.use('TkAgg')

import numpy as np
import scipy.stats as sps
import matplotlib.pyplot as plt
import pandas as pd
import itertools
import collections
import pickle
import math

np.set_printoptions(linewidth=10 ** 7)
pd.set_option('display.width', None)
plt.rcParams['figure.figsize'] = (10, 7)

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


def convert_skeleton(skeleton):
    """
    :return: (nodes, edges)
        nodes: [(x, y, degree, radial)]
        edges: [(node1_index, node2_index)]
    """

    nodes = []
    edges = []
    coordinates_to_nodes = {}
    def convert_node(node):
        x, y, degree, radial = node
        if (x, y) in coordinates_to_nodes:
            return coordinates_to_nodes[(x, y)]
        else:
            node_index = len(nodes)
            nodes.append((x, y, radial, degree))
            coordinates_to_nodes[(x, y)] = node_index
            return node_index

    for i in range(0, len(skeleton), 8):
        node0 = convert_node(skeleton[i + 4 * 0:i + 4 * 1])
        node1 = convert_node(skeleton[i + 4 * 1:i + 4 * 2])
        edges.append([node0, node1])
    # return np.array(nodes), np.array(edges)
    return nodes, edges


def skeleton_to_discrete(skeleton):
    """
    :return: array
        array.shape == (SIZE, SIZE)
        array[i][j] = максимальный радиус окружности, с центром в точке (i * step, j * step),
            где step подбирается так, чтобы символ находился по центру и занимал 80% по каждой из осей
    """
    SIZE = 28
    PADDING_PERCENTAGE = 0.2
    nodes, edges = convert_skeleton(skeleton)

    def create_grid(coordinate_index):
        coordinate_min = min(node[coordinate_index] for node in nodes)
        coordinate_max = max(node[coordinate_index] for node in nodes)
        coordinate_delta = coordinate_max - coordinate_min
        coordinate_min -= coordinate_delta * PADDING_PERCENTAGE
        coordinate_max += coordinate_delta * PADDING_PERCENTAGE
        return np.linspace(coordinate_min, coordinate_max, SIZE)
    x_grid = create_grid(0)
    y_grid = create_grid(1)

    def find_max_radius(x, y):
        max_radius = 0
        for node_index0, node_index1 in edges:
            node0 = nodes[node_index0]
            node1 = nodes[node_index1]
            # TODO заменить перебор a на максимум из a \in {0, 1, <аналитеческое значение a, дающее ноль у производной>}
            for a in np.linspace(0, 1, 5):
                # x0, y0, radial0, _ = node0 * a + node1 * (1 - a)
                x0 = node0[0] * a + node1[0] * (1 - a)
                y0 = node0[1] * a + node1[1] * (1 - a)
                radial0 = node0[2] * a + node1[2] * (1 - a)

                distance = math.sqrt((x - x0) ** 2 + (y - y0) ** 2)
                current_radius = radial0 - distance
                assert current_radius is not None
                max_radius = max(max_radius, current_radius)
        return max_radius

    result = np.empty((SIZE, SIZE))
    for i, x in enumerate(x_grid):
        for j, y in enumerate(y_grid):
            result[i][j] = find_max_radius(x, y)
    return result

X_train, y_train, X_train_skeleton = read_data('data/train_info')
# X_test, y_test, X_test_skeleton = read_data('data/test_info')

# with open('single-image.pickle', 'rb') as input:
#     data = pickle.load(input)
#     x, x_skeleton = data['x'], data['x_skeleton']

N = 100
X_new = []
for i in tqdm(range(N)):
    x_new = skeleton_to_discrete(X_train_skeleton[i])
    X_new.append(x_new)
    # plt.figure()
    # im = plt.imshow(image, cmap='gray')
    # plt.colorbar(im, orientation='horizontal')
    # plt.show()
X_new = np.array(X_new)

with open('data_matrixes/train.pickle', 'wb') as output:
    data = {
        'X_discrete_new': X_new,
        'X_discrete_old': X_train[:N],
        'X_skeleton': X_train_skeleton[:N],
        'y': y_train[:N]
    }
    pickle.dump(data, output, protocol=pickle.HIGHEST_PROTOCOL)
