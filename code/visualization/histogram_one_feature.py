from helpers import *
import matplotlib.pyplot as plt

def draw_hist(feature_name, additional_actions):
    feature_index = F_names.index(feature_name)
    feature_values = []
    for graph in F:
        nodes_features = graph['nodes_features']
        feature_values += nodes_features[:, feature_index].tolist()

    plt.figure()
    plt.hist(feature_values, bins=50)
    # plt.title('Гистограмма признака {}'.format(feature_name))
    plt.xlabel('радиальная функция')
    plt.tight_layout()
    if additional_actions is not None:
        additional_actions()
    plt.savefig('images/histogram_feature_{}.eps'.format(feature_name))

def radial_additional_actions():
    plt.gca().set_xlim(right=15)

features = [
    ('radial', None),
    ('min_angle_between_adjacent_edges', None),
    ('distances_to_one_degree_node', None),
    ('angles_sum_on_path_one_degree_node', None),
]
for feature_name, feature_additional_actions in features:
    print('\t', feature_name)
    draw_hist(feature_name, feature_additional_actions)

# 'number_cycles',
# 'cycle_area',
# 'straight_line_length',
# 'straight_line_angle_between_horizontal'