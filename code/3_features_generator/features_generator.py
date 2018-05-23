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
from collections import Counter

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

    # некоторая отладка для изучения того, почему записанная степень вершины отличается от актуальной
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
            # from visualization.visualization import draw_skeleton
            # draw_skeleton(nodes, adjacency_list)
            pass
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
        edges: [(node1_index, node2_index)]
    """
    features_generator = FeaturesGenerator(skeleton)
    return features_generator.generate_features()


class FeaturesGenerator:
    debug_number_nodes = 0
    debug_number_nodes_in_straight_lines = 0
    debug_straight_lines_lengths = []
    debug_straight_lines_sizes = []
    debug_number_skeletons_without_nodes_with_degree_one = 0
    STRAIGHT_LINES_ANGLE_THRESHOLD = np.deg2rad(10)
    STRAIGHT_LINES_LENGTH_THRESHOLD = 10  # размер квадрата, в котором лежит скелет --- 64

    def __init__(self, skeleton):
        nodes, adjacency_list = convert_skeleton(skeleton)
        self.nodes = np.array(nodes)
        self.adjacency_list = adjacency_list

    def generate_features(self):
        self.find_cycles()
        self.calculate_one_degree_nodes_features()
        self.find_straight_lines()
        nodes_features = [self.generate_node_features(node_index, node_features0) for node_index, node_features0 in enumerate(self.nodes)]
        nodes_features = np.array(nodes_features)
        return nodes_features, self.adjacency_list

    ################################################
    # служебные функции

    def get_edge_length(self, node1, node2):
        x1, y1, _, _ = self.nodes[node1]
        x2, y2, _, _ = self.nodes[node2]
        delta_x = x1 - x2
        delta_y = y1 - y2
        return math.sqrt(delta_x * delta_x + delta_y * delta_y)

    def get_angle_between_edges(self, edge1, edge2):
        # угол между (u1, v1) и (u2, v2)
        u1, v1 = edge1
        u2, v2 = edge2
        def get_edge_vector(u, v):
            x_u, y_u, _, _ = self.nodes[u]
            x_v, y_v, _, _ = self.nodes[v]
            x_delta = x_u - x_v
            y_delta = y_u - y_v
            return x_delta, y_delta
        x1, y1 = get_edge_vector(u1, v1)
        x2, y2 = get_edge_vector(u2, v2)
        # https://stackoverflow.com/a/16544330/5812238
        dot_product = x1 * x2 + y1 * y2
        cross_product = x1 * y2 - y1 * x2
        return math.atan2(cross_product, dot_product)

    ################################################
    # методы для всего графа

    def calculate_one_degree_nodes_features(self):
        # кратчайшее расстояние для каждой вершины от неё до вершины степени один
        # (Дейкстра с начальными вершинами --- всеми вершинами степени 1)

        # и сумма углов поворота между рёбрами на пути от каждой вершины к ближайшей вершине степени один
        # (запоминаем путь в Дейкстре)

        from heapq import heappush, heappop
        queue = []  # [(distance, node, previous)]
        distances = [None] * len(self.nodes)
        previous_nodes = [None] * len(self.nodes)
        for node in range(len(self.nodes)):
            if len(self.adjacency_list[node]) == 1:
                heappush(queue, [0, node, -1])
        if len(queue) == 0:
            # нет вершин степени 1
            # TODO подумать что делать в таком случае
            self.distances_to_one_degree_node = [0] * len(self.nodes)
            self.angles_sum_on_path_one_degree_node = [0] * len(self.nodes)
            FeaturesGenerator.debug_number_skeletons_without_nodes_with_degree_one += 1
            return
        while len(queue) > 0:
            distance, node, previous_node = heappop(queue)
            if distances[node] is None:
                distances[node] = distance
                previous_nodes[node] = previous_node
                for neighbour in self.adjacency_list[node]:
                    if distances[neighbour] is None:
                        distance_new = distance + self.get_edge_length(node, neighbour)
                        heappush(queue, [distance_new, neighbour, node])
        self.distances_to_one_degree_node = distances

        angles_sum_on_path_one_degree_node = [None] * len(self.nodes)
        def update_angle(node):
            # возвращает пару (сумма_углов, предыдущая_вершина)
            previous_node = previous_nodes[node]
            # TODO проверить, что assert падает только на вершинах степени ноль
            # assert previous_node is not None
            angles_sum = angles_sum_on_path_one_degree_node[node]
            if angles_sum is None:
                if previous_node == -1 or previous_node is None:
                    # вершина степени один или ноль или ?
                    angles_sum = 0
                else:
                    previous_angles_sum, node1 = update_angle(previous_node)
                    node2 = previous_node
                    node3 = node
                    angle_between_last_edges = 0 if node1 == -1 else self.get_angle_between_edges((node1, node2), (node2, node3))
                    angles_sum = previous_angles_sum + angle_between_last_edges
            angles_sum_on_path_one_degree_node[node] = angles_sum
            return angles_sum, previous_node
        for node in range(len(self.nodes)):
            update_angle(node)
        self.angles_sum_on_path_one_degree_node = angles_sum_on_path_one_degree_node

        # TODO решить что делать если нет вершин степени один (заменять на нули имхо плохое решение)
        # for array in distances, angles_sum_on_path_one_degree_node:
        #     for i in range(len(array)):
        #         if array[i] is None:
        #             array[i] = 0

    def find_straight_lines(self):
        # прямая линия — путь в графе, такой что угол между каждой парой соседних рёбер отличается не более чем на 10° от 180°

        # TODO сколько прямых линий на самом деле непрямые?
        #      (например, 10 рёбер, между каждыми двумя угол поворота меньше 10, в итоге получаем «прямую линию» с углом поворота >90)
        #      может стоит не рассматривать такие линии, или вообще как-нибудь изменить алгоритм поиска прямых линий, чтобы это учитывалось

        # для каждой прямой линии нас будет интересовать её длина и угол относительно горизонтали
        self.node_straight_lines_features = [(0, 0) for _ in range(len(self.nodes))]

        # каждой вершине сопоставляем линию (массив вершин), которой вершина принадлежит
        nodes_line = [None] * len(self.nodes)
        # каждой вершине v сопоставляем пару смежных с ней вершин (u, w), таких что путь (u, v, w) является (частью) прямой линией
        nodes_line_part = [None] * len(self.nodes)

        for node in range(len(self.nodes)):
            if len(self.adjacency_list[node]) < 2:
                continue
            neighbours_pairs = [(self.get_angle_between_edges((neighbour1, node), (node, neighbour2)), neighbour1, neighbour2)
                                for neighbour1, neighbour2 in itertools.combinations(self.adjacency_list[node], 2)]
            neighbours_pairs.sort()
            # выбираем одну лучшею пару, так как считаем что через вершину степени три не может проходить две прямых линии
            angle, neighbour1, neighbour2 = neighbours_pairs[0]
            if abs(angle) < FeaturesGenerator.STRAIGHT_LINES_ANGLE_THRESHOLD:
                nodes_line_part[node] = (neighbour1, neighbour2)

        used_in_continue_line = np.full(len(self.nodes), False)
        def continue_line(node, previous_node, current_line):
            # продолжает прямую линию от previous_node к node и возвращает массив [node, ...]
            current_line.append(node)
            node_line_part = nodes_line_part[node]
            if node_line_part is None or nodes_line[node] is not None or used_in_continue_line[node]:
                return current_line
            used_in_continue_line[node] = True
            node1, node2 = node_line_part
            if node1 != previous_node and node2 != previous_node:
                return current_line
            next_node = node1 if node1 != previous_node else node2
            return continue_line(next_node, node, current_line)
        def get_line_length_and_angle_between_horizontal(line):
            length = 0
            # угол считается как взвешенная (по длине ребра) сумма углов рёбер
            angle_weighted = 0
            for node1, node2 in zip(line[:-1], line[1:]):
                current_length = self.get_edge_length(node1, node2)
                length += current_length
                x1, y1, _, _ = self.nodes[node1]
                x2, y2, _, _ = self.nodes[node2]
                current_angle_weighted = math.atan2(y2 - y1, x2 - x1)
                if current_angle_weighted < 0:
                    current_angle_weighted += math.pi
                angle_weighted += current_angle_weighted * current_length
            angle = angle_weighted / length
            return length, angle
        for node in range(len(self.nodes)):
            FeaturesGenerator.debug_number_nodes += 1
            if nodes_line[node] is None:
                node_line_part = nodes_line_part[node]
                if node_line_part is not None:
                    node1, node2 = node_line_part
                    used_in_continue_line[node] = True
                    line1 = continue_line(node1, node, [])
                    line2 = continue_line(node2, node, [])
                    node_line = [*line1[::-1], node, *line2]
                    node_line_length, node_line_angle = get_line_length_and_angle_between_horizontal(node_line)
                    if node_line_length < FeaturesGenerator.STRAIGHT_LINES_LENGTH_THRESHOLD:
                        # не рассматриваем слишком короткие линии
                        continue
                    for v in node_line:
                        FeaturesGenerator.debug_number_nodes_in_straight_lines += 1
                        nodes_line[v] = node_line
                        self.node_straight_lines_features[v] = (node_line_length, node_line_angle)
                    FeaturesGenerator.debug_straight_lines_lengths.append(node_line_length)
                    FeaturesGenerator.debug_straight_lines_sizes.append(len(node_line))
        self.nodes_line = nodes_line

    def find_cycles(self):
        # поиск цикла (ищем только первый цикл, так как больше одного цикла почти не бывает (толко у цифры 8))
        cycle = None
        visited = np.zeros(len(self.nodes), dtype=np.bool)
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
            for neighbour in self.adjacency_list[node]:
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
        self.cycle = cycle

        # площадь цикла
        if cycle is None:
            self.cycle_area = 0
        else:
            x, y = self.nodes[0:2, cycle].T
            # https://stackoverflow.com/a/30408825/5812238
            self.cycle_area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    ################################################
    # методы для одной вершины

    def generate_node_features(self, node, node_features0):
        """
        features:
            degree --- степень вершины, от 1 до 3
            radial --- значение радиальной функции в вершине
            min_angle --- значение минимального угла между рёбрами, выходящими из вершины
            number_cycles --- число циклов, в которых содержится вершина (по сути это бинарное свойство, так как два цикла только у цифры 8)
            circle_area --- площадь области, ограниченной циклом. среднее площадей, если циклов несколько
            distance_to_one_degree_node --- минимальное расстояние до вершины степени 1
        """
        x, y, degree, radial = node_features0
        # TODO посмотреть как же так получается что степени вершин не совпадают
        # assert degree == len(adjacency_list[node])
        degree = len(self.adjacency_list[node])
        assert 0 <= degree <= 4, 'неожиданная степень вершины: {}'.format(degree)

        node_features = []
        node_features += [degree]
        node_features += [radial]
        node_features += [self.get_min_angle_between_adjacent_edges(node, x, y, degree, radial)]
        node_features += self.get_cycles_features(node, x, y, degree, radial)
        node_features += self.get_one_degree_node_features(node, x, y, degree, radial)
        node_features += self.get_straight_lines_node_features(node, x, y, degree, radial)

        # TODO признак наличия вершин степени 4 (полезно, применимо к только 2(?) символам, неосуществимо при текущем алгоритме скелетонизации ([хотя мб считать две очень близких вершины степени 3 как вершину степени 4))
        # TODO число связных компонент
        return node_features

    def get_min_angle_between_adjacent_edges(self, node, x, y, degree, radial):
        def angle_between_neighbours(neighbour1, neighbour2):
            neighbour1 = self.adjacency_list[node][neighbour1]
            neighbour2 = self.adjacency_list[node][neighbour2]
            return abs(self.get_angle_between_edges((node, neighbour1), (node, neighbour2)))
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
        return min_angle

    def get_cycles_features(self, node, x, y, degree, radial):
        # number_cycles & cycle_area
        if (self.cycle is not None) and (node in self.cycle):
            node_number_cycles = 1
            node_cycle_area = self.cycle_area
        else:
            node_number_cycles = 0
            node_cycle_area = 0
        return [node_number_cycles, node_cycle_area]

    def get_one_degree_node_features(self, node, x, y, degree, radial):
        return [
            # минимальное расстояние до вершины степени 1
            self.distances_to_one_degree_node[node],
            # сумма углов поворота между рёбрами на пути к ближайшей вершине степени один
            self.angles_sum_on_path_one_degree_node[node]
        ]

    def get_straight_lines_node_features(self, node, x, y, degree, radial):
        # пара
        #   длина максимальной прямой линии, в которой содержится текущая вершина
        #   угол между максимальной прямой линией и горизонталью
        return self.node_straight_lines_features[node]


# for debug
# skeletons = np.load('single_skeleton.npy')
# features = list(map(generate_features, skeletons))

skeletons = np.load('../2_skeleton_creator/skeletons.npy')
features = list(map(generate_features, tqdm(skeletons)))
result = {
    'F': [
        {
            'nodes_features': nodes_features,
            'adjacency_list': adjacency_list
        } for nodes_features, adjacency_list in features
    ],
    'F_nodes_features_description': [
        'degree',
        'radial',
        'min_angle_between_adjacent_edges',
        'number_cycles',
        'cycle_area',
        'distances_to_one_degree_node',
        'angles_sum_on_path_one_degree_node',
        'straight_line_length',
        'straight_line_angle_between_horizontal'
    ]
}

with open('features.pickle', 'wb') as output:
    pickle.dump(result, output)

print('предупреждение: доля скелетов без вершин степени один равна', FeaturesGenerator.debug_number_skeletons_without_nodes_with_degree_one / len(skeletons))
print('доля вершин, входящих в какую-нибудь прямую линию', FeaturesGenerator.debug_number_nodes_in_straight_lines / FeaturesGenerator.debug_number_nodes)

# plt.figure()
# plt.hist(FeaturesGenerator.debug_straight_lines_sizes, bins=20)
# plt.title('Гистограмма числа вершин в прямых линиях')
# plt.show()

# plt.figure()
# plt.hist(FeaturesGenerator.debug_straight_lines_lengths, bins=20)
# plt.title('Гистограмма длин прямых линий')
# plt.show()