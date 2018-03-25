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
        adjacency_matrix: [(node1_index, node2_index)]
    """

    nodes = []
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

    adjacency_matrix = [[] for _ in range(len(nodes))]
    for i in range(0, len(skeleton), 8):
        node0 = convert_node(skeleton[i + 4 * 0:i + 4 * 1])
        node1 = convert_node(skeleton[i + 4 * 1:i + 4 * 2])
        adjacency_matrix[node0].append(node1)
        adjacency_matrix[node1].append(node0)
    return nodes, adjacency_matrix

# исследуемые символы
# abcdefghijklmnopqrstuvwxyz 0123456789

# символы с циклами
# abdgopq 04689

# символы без циклов
# cefhijklmnrstuvwxyz 12357

def skeleton_to_discrete(skeleton):
    """
    :return: (nodes_features, edges)
        nodes_features: [(feature1, feature2, ...)]
            features:
                degree --- степень вершины, от 1 до 3
                radial --- значение радиальной функции в вершине
                number_cycles --- число циклов, в которых содержится вершина (по сути это бинарное свойство, так как два цикла только у цифры 8)
                circle_area --- площадь области, ограниченной циклом. среднее площадей, если циклов несколько
                min_angle --- значение минимального угла между рёбрами, выходящими из вершины

        edges: [(node1_index, node2_index)]
    """
    nodes, adjacency_matrix = skeleton
    nodes = np.array(nodes)

    # поиск цикла (ищем только первый цикл, так как больше одного цикла почти не бывает (толко у цифры 8))
    cycle = None
    visited = np.zeros(len(nodes), dtype=np.bool)
    def dfs(node, previous_node):
        global cycle
        """
        :param node: текущая вершина dfs
        :param previous_node: предыдущая вершина dfs
        :return: (dfs_state, node)
            dfs_state:
                0 --- цикл не найден
                1 --- цикл найден, заполняем массив цикла
                2 --- цикл найден, массив цикла заполнен 
            node --- вершина на которой dfs нашёл цикл
        """
        if visited[node]:
            # нашли цикл
            cycle = [node]
            return 1, node
        visited[node] = True
        for neighbour in adjacency_matrix[node]:
            if neighbour != previous_node:
                dfs_state, cycle_node = dfs(neighbour, node)
                if dfs_state == 1:
                    if node == cycle_node:
                        return 2, None
                    else:
                        cycle.append(node)
                        return 1, cycle_node
                elif dfs_state == 2:
                    return 2, None
        return 0, None
    # площадь цикла
    if cycle is None:
        cycle_area = 0
    else:
        x, y = nodes[0:2, cycle].T
        # https://stackoverflow.com/a/30408825/5812238
        cycle_area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    def generate_features(node, node_features0):
        x, y, degree, radial = node_features0
        node_features = []
        node_features += [degree]
        node_features += [radial]

        # min_angle
        assert degree == len(adjacency_matrix[node])
        def get_vector_to_neighbour(neighbour):
            x_neighbour, y_neighbour, _, _ = nodes[neighbour]
            delta_x = x_neighbour - x
            delta_y = y_neighbour - y
            delta_length = math.sqrt(delta_x * delta_x + delta_y * delta_y)
            return (delta_x / delta_length, delta_y / delta_length)
        vectors_to_neighbours = [get_vector_to_neighbour(neighbour) for neighbour in (adjacency_matrix[node])]
        def angle_between_neighbours(neighbour1, neighbour2):
            x1, y1 = vectors_to_neighbours[neighbour1]
            x2, y2 = vectors_to_neighbours[neighbour2]
            dot_product = x1 * x2 + y1 * y2
            return abs(math.acos(dot_product))
        if degree == 1:
            min_angle = 0
        elif degree == 2:
            min_angle = angle_between_neighbours(0, 1)
        elif degree == 3:
            min_angle = min(angle_between_neighbours(0, 1), angle_between_neighbours(1, 2), angle_between_neighbours(2, 0))
        else:
            assert False
        node_features += [min_angle]

        # number_cycles & cycle_area
        number_cycles = 0
        total_cycles_area = 0
        if node in cycle:
            number_cycles += 1
            total_cycles_area += cycle_area
        node_features += [number_cycles]
        node_features += [0 if number_cycles == 0 else total_cycles_area / number_cycles]

        # расстояние/минимальное расстояние до вершины степени 1
        # суммарный угол поворота на пути до ближайшей вершины степени 1
        # длина максимальной прямой линии, в которой содержится текущая вершина (прямая линия --- путь в графе, такой что каждый угол примерно 180)


    nodes_features = list(map(generate_features, enumerate(nodes)))
    return nodes_features, adjacency_matrix

# X_train, y_train, X_train_skeleton = read_data('data/train_info')
# X_test, y_test, X_test_skeleton = read_data('data/test_info')

with open('single-image.pickle', 'rb') as input:
    data = pickle.load(input)
    x, x_skeleton = data['x'], data['x_skeleton']

x_new = skeleton_to_discrete(x_skeleton)
print(x_new)