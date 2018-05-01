from helpers import graphs
vertexes_degrees = []
for graph in graphs():
    adjacency_list = graph['adjacency_list']
    for adjacency_vertexes in adjacency_list:
        vertexes_degrees.append(len(adjacency_vertexes))

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from collections import Counter
counter = Counter(vertexes_degrees)
del counter[0]
del counter[4]
plt.figure(figsize=(10, 7))
plt.bar(counter.keys(), counter.values())
plt.title('Гистограмма степеней вершин медиального представления')
plt.xlabel('степень вершины')
plt.gca().xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
plt.show()