from generated.data_loader import load_data_discrete
X, y = load_data_discrete(size=1000)

import matplotlib
import matplotlib.pyplot as plt
for i, x in enumerate(X):
    plt.imsave('as_png/{}.png'.format(i), x, cmap=matplotlib.cm.gray)