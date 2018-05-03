from helpers import *
vertexes_degrees = []
for graph in graphs():
    adjacency_list = graph['adjacency_list']
    for adjacency_vertexes in adjacency_list:
        vertexes_degrees.append(len(adjacency_vertexes))

from collections import Counter
counter = Counter(vertexes_degrees)
del counter[0]
del counter[4]

import matplotlib.pyplot as plt
plt.figure()
plt.bar(counter.keys(), counter.values())
# plt.title('Гистограмма степеней вершин графа')
plt.xlabel('степень вершины')
plt.gca().xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
plt.tight_layout()
plt.savefig('images/histogram_vertexes_degrees.eps')