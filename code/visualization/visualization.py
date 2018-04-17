import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import scipy.stats as sps
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import itertools
import collections
import math
np.set_printoptions(linewidth=10 ** 7)
pd.set_option('display.width', None)
plt.rcParams['figure.figsize'] = (10, 7)

"""
import sys
sys.path.insert(0, '/home/dima/6science/MyFirstScientificPublication/code/visualization')
import visualization.draw_skeleton
"""

s = 64
def draw_skeleton(nodes, adjacency_list):
    plt.figure()
    for node in nodes:
        x, y, degree, radial = node
        circle = plt.Circle((x, s - y), radial, color='cyan', ls='-', linewidth=2, fill=False)
        plt.scatter([x], [s - y], color='blue', s=5)
        plt.gca().add_patch(circle)
    plt.xlim((0, s))
    plt.ylim((0, s))
    plt.show()