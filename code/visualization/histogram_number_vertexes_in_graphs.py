from helpers import graphs
numbers_vertexes = []
for graph in graphs():
    adjacency_list = graph['adjacency_list']
    numbers_vertexes.append(len(adjacency_list))

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 7))
plt.hist(numbers_vertexes, bins=20)
plt.title('Гистограмма числа вершин графа медиального представления')
plt.xlabel('число вершин')
plt.show()