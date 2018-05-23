from helpers import *
import matplotlib.pyplot as plt

def draw_hist(feature_name, plot_title, additional_actions):
    print('\t', feature_name)
    feature_index = F_names.index(feature_name)
    feature_values = []
    for graph in F:
        nodes_features = graph['nodes_features']
        feature_values += nodes_features[:, feature_index].tolist()
    feature_values = [value for value in feature_values if value is not None]

    plt.figure()
    plt.hist(feature_values, bins=100)
    # plt.title('Гистограмма признака {}'.format(feature_name))
    plt.xlabel(plot_title)
    plt.tight_layout()
    if additional_actions is not None:
        additional_actions()
    plt.savefig('images/histogram_feature_{}.eps'.format(feature_name))

def radial_additional_actions():
    plt.gca().set_xlim(right=15)

features = [
    ('radial', 'радиальная функция', radial_additional_actions),
    ('min_angle_between_adjacent_edges', 'минимальный угол между рёбрами вершины', None),
    ('distances_to_one_degree_node', 'расстояние до 1-вершины', None),
    ('angles_sum_on_path_one_degree_node', 'сумма углов на пути к 1-вершине', None),
]
for feature in features:
    draw_hist(*feature)

# 'number_cycles',
# 'cycle_area',
# 'straight_line_length',
# 'straight_line_angle_between_horizontal'