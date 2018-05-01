import pickle

result = {}

with open('../3_features_generator/features.pickle', 'rb') as input:
    features = pickle.load(input)
    result['F'] = features['F']

with open('../1_data_discrete/data.pickle', 'rb') as input:
    data = pickle.load(input)
    result['I'] = data['I']
    result['y'] = data['y']

with open('data_and_features.pickle', 'wb') as output:
    pickle.dump(result, output)