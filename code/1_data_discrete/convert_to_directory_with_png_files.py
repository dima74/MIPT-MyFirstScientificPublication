from constants import N
from generated.data_loader import load_data_discrete
X, y = load_data_discrete(path='generated', size=N)

import shutil
import os
try:
    os.remove('data.pickle')
except OSError:
    pass
shutil.rmtree('as_png', ignore_errors=True)
os.mkdir('as_png')

import matplotlib
import matplotlib.pyplot as plt
for i, x in enumerate(X):
    plt.imsave('as_png/{}.png'.format(i), x, cmap=matplotlib.cm.gray)