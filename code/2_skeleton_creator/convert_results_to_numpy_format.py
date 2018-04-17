import numpy as np

path = 'code/'

with open(path + 'directory_with_links_to_images_bones0.txt') as input:
    lines = input.readlines()
    # skeletons --- массив скелетов (каждый скелет --- массив вещественных чисел)
    skeletons = [list(map(float, line.strip().split())) for line in lines]
with open(path + 'directory_with_links_to_images_files_paths.txt') as input:
    # lines --- список имён файлов для которых генерировались скелеты, в том же порядке в котором скелеты идут в массиве skeletons
    lines = input.readlines()
    indexes = [int(line[line.rfind('/') + 1:-len('.png\n')]) for line in lines if line]

# i-ая скелет массива skeletons должен иметь индекс indexes[i]
skeletons_reordered = [None] * len(skeletons)
for skeleton, index_right in zip(skeletons, indexes):
    skeletons_reordered[index_right] = skeleton

np.save('skeletons.npy', skeletons_reordered)

# import matplotlib
# matplotlib.use('TkAgg')
# import matplotlib.pyplot as plt
# plt.rcParams['figure.figsize'] = (10, 7)

# skeletons_result =
# number_skeletons = [len(skeleton) // 8 for skeleton in skeletons]
# plt.figure()
# plt.hist(number_skeletons)
# plt.show()