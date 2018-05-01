"""
Формат файла:
        {
            'y': (None, 1),
            'I': (None, 64, 64),
            'F': [{
                'nodes_features': (number_vertexes, number_features),
                'adjacency_list': Бarray of arrays>,
            }]
        }
"""

import pickle
with open('data_and_features.pickle', 'rb') as input:
    data = pickle.load(input)
    y = data['y']  # правильные ответы (номера символов)
    I = data['I']  # исходные растровые изображения
    print(y.shape, I.shape)

    F = data['F']  # список графов признаков

    # небольшое описание формата F и небольшой пример
    """
    каждый граф --- dict с ключами 'nodes_features' и 'adjacency_list'
    nodes_features --- матрица признаков размерности (число вершин, число признаков)
    adjacency_list --- список смежности графа
        adjacency_list[i] = список вершин, смежных с i
    """

    example_graph = F[0]
    nodes_features = example_graph['nodes_features']
    adjacency_list = example_graph['adjacency_list']
    print(type(nodes_features), nodes_features.shape)
    print(type(adjacency_list), len(adjacency_list))