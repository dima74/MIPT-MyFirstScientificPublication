from helpers import *
numbers_vertexes = []
for graph in graphs():
    adjacency_list = graph['adjacency_list']
    numbers_vertexes.append(len(adjacency_list))

import matplotlib.pyplot as plt
plt.figure()
plt.hist(numbers_vertexes, bins=50)
# plt.title('Гистограмма числа вершин графа медиального графа')
plt.xlabel('число вершин')
plt.savefig('images/histogram_number_vertexes.eps')