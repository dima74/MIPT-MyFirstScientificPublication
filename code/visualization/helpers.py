def graphs():
    import pickle
    with open('../4_merge_data_and_features/data_and_features.pickle', 'rb') as input:
        data = pickle.load(input)
    F = data['F']
    return F