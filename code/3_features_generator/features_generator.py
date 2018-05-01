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

# def read_data(filename):
#     """
#     :return: (X, y, X_skeleton)
#         X.shape == (N, 28*28)
#         y.shape == (N)
#         X_skeleton.shape == (N, 8 * number_edges)
#             X_skeleton == [edge1, edge2, ...]
#             edge == node1, node2
#             node == x, y, degree, radial
#     """
#     with open(filename, 'rb') as input:
#         data = pickle.load(input)
#         X, y, X_skeleton = data['data'], data['labels'], data['skel_features']
#         return X, y, X_skeleton

# for debug only, pretty print skeleton
def pps(skeleton):
    result = []
    for i in range(0, len(skeleton), 8):
        node0 = skeleton[i + 4 * 0:i + 4 * 1]
        node1 = skeleton[i + 4 * 1:i + 4 * 2]
        result.append((node0, node1))
    return result


# q = 0
def convert_skeleton(skeleton):
    # global q
    # print(q)
    # q += 1
    """
    :return: (nodes, edges)
        nodes: [(x, y, degree, radial)]
        adjacency_list: массив массивов (adjacency_list[i] --- список вершин, смежных с i)
    """

    nodes = []
    # description == (x, y, degree, radial)
    descriptions_to_nodes = {}
    def convert_node(node):
        """ получает вершину в виде (x, y, degree, radial), сохраняет её в список вершин и возвращает индекс этой ввершины """
        x, y, degree, radial = node
        # node_description = tuple(node)
        node_description = (x, y)
        if node_description in descriptions_to_nodes:
            return descriptions_to_nodes[node_description]
        else:
            node_index = len(nodes)
            nodes.append(node)
            descriptions_to_nodes[node_description] = node_index
            return node_index

    edges = []
    for i in range(0, len(skeleton), 8):
        node0 = convert_node(skeleton[i + 4 * 0:i + 4 * 1])
        node1 = convert_node(skeleton[i + 4 * 1:i + 4 * 2])
        if node0 != node1:
            edges.append((node0, node1))

    adjacency_list = [[] for _ in range(len(nodes))]
    for node0, node1 in edges:
        adjacency_list[node0].append(node1)
        adjacency_list[node1].append(node0)

    # некоторая отладка для изучения того, почему записанноая степень вершины отличается от актуально
    # можно удалить это
    for node_index, node in enumerate(nodes):
        if node[2] != len(adjacency_list[node_index]):
            # print()
            # print(node_index, node, adjacency_list[node_index])
            # for node_neighbour in adjacency_list[node_index]:
            #     print(node_neighbour, nodes[node_neighbour])
            # вернуть идентификацию вершин только по координатам
            # import sys
            # sys.path.insert(0, '/home/dima/6science/MyFirstScientificPublication/code')
            from visualization.visualization import draw_skeleton
            # draw_skeleton(nodes, adjacency_list)
        # assert node[2] == len(adjacency_list[node_index])

    return nodes, adjacency_list

# наличие вершины степени три
# 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
# есть три:     3689abdeghmnpqABEFHPRTY
# нету:         01257cijlorsuvwyzCDGIJLMNOSUVWZ
# есть четыре:  4fktxKQX


# наличие циклов
# 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
# есть:  04689abdgopqBDOPQR
# нету:  12357cefhijklmnrstuvwxyzACEFGHIJKLMNSTUVWXYZ

# площадь цикла
# 04689abdgopqBDOPQR
# большая:    0oDOQ
# маленькая:  4689abdgpqBPR




def generate_features(skeleton):
    """
    :return: (nodes_features, edges)
        nodes_features: [(feature1, feature2, ...)]
            features:
                degree --- степень вершины, от 1 до 3
                radial --- значение радиальной функции в вершине
                number_cycles --- число циклов, в которых содержится вершина (по сути это бинарное свойство, так как два цикла только у цифры 8)
                circle_area --- площадь области, ограниченной циклом. среднее площадей, если циклов несколько
                min_angle --- значение минимального угла между рёбрами, выходящими из вершины
                ...

        edges: [(node1_index, node2_index)]
    """
    nodes, adjacency_list = convert_skeleton(skeleton)
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
        for neighbour in adjacency_list[node]:
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
    dfs(0, -1)

    # площадь цикла
    if cycle is None:
        cycle_area = 0
    else:
        x, y = nodes[0:2, cycle].T
        # https://stackoverflow.com/a/30408825/5812238
        cycle_area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    # поиск прямых линий
    ...

    def generate_features(node, node_features0):
        x, y, degree, radial = node_features0
        node_features = []
        node_features += [degree]
        node_features += [radial]

        # TODO посмотреть как же так получается что степени вершин не совпадают
        # assert degree == len(adjacency_list[node])
        degree = len(adjacency_list[node])
        assert 0 <= degree <= 4, 'неожиданная степень вершины: {}'.format(degree)

        # min_angle
        def get_vector_to_neighbour(neighbour):
            x_neighbour, y_neighbour, _, _ = nodes[neighbour]
            delta_x = x_neighbour - x
            delta_y = y_neighbour - y
            delta_length = math.sqrt(delta_x * delta_x + delta_y * delta_y)
            return (delta_x / delta_length, delta_y / delta_length)
        vectors_to_neighbours = [get_vector_to_neighbour(neighbour) for neighbour in (adjacency_list[node])]
        def angle_between_neighbours(neighbour1, neighbour2):
            x1, y1 = vectors_to_neighbours[neighbour1]
            x2, y2 = vectors_to_neighbours[neighbour2]
            dot_product = x1 * x2 + y1 * y2
            # https://stackoverflow.com/a/13849249/5812238
            return abs(math.acos(np.clip(dot_product, -1, +1)))
        if degree == 1:
            min_angle = 0
        elif degree == 2:
            min_angle = angle_between_neighbours(0, 1)
        elif degree == 3:
            min_angle = min(angle_between_neighbours(0, 1), angle_between_neighbours(1, 2), angle_between_neighbours(2, 0))
        elif degree == 4:
            # изображений с вершинами степени 4 не так много...
            min_angle = math.pi / 4
        elif degree == 0:
            min_angle = 0
        else:
            assert False
        node_features += [min_angle]

        # number_cycles & cycle_area
        if (cycle is not None) and (node in cycle):
            node_number_cycles = 1
            node_cycle_area = cycle_area
        else:
            node_number_cycles = 0
            node_cycle_area = 0
        node_features += [node_number_cycles]
        node_features += [node_cycle_area]

        # расстояние/минимальное расстояние до вершины степени 1
        # суммарный угол поворота на пути до ближайшей вершины степени 1
        # длина максимальной прямой линии, в которой содержится текущая вершина (прямая линия --- путь в графе, такой что каждый угол примерно 180)
        # наличие вершин степени 4 (полезно, применимо к только 2(?) символам, неосуществимо при текущем алгоритме ([хотя мб считать две очень близких вершины степени 3 как вершину степени 4))
        # число связных компонент
        return node_features

    nodes_features = [generate_features(node_index, node_features0) for node_index, node_features0 in enumerate(nodes)]
    nodes_features = np.array(nodes_features)
    return nodes_features, adjacency_list


skeletons = np.load('../2_skeleton_creator/skeletons.npy')
features = list(map(generate_features, tqdm(skeletons)))
result = {
    'F': [
        {
            'nodes_features': nodes_features,
            'adjacency_list': adjacency_list
        } for nodes_features, adjacency_list in features
    ]
}

with open('features.pickle', 'wb') as output:
    pickle.dump(result, output)

# with open('single-image.pickle', 'rb') as input:
#     data = pickle.load(input)
#     x, x_skeleton = data['x'], data['x_skeleton']
#
# x_new = generate_features(x_skeleton)
# print(x_new)