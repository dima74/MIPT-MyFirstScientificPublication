from generated.data_loader import load_data_discrete
X, y = load_data_discrete(path='generated', size=1000)

import pickle
data = {
    "I": X,
    "y": y,
}
with open('data.pickle', 'wb') as output:
    pickle.dump(data, output)