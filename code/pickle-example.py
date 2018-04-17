def write_example():
    import pickle
    data = {'key': 'value'}  # any data
    with open('path/to/file.pickle', 'wb') as output:
        pickle.dump(data, output)

def read_example():
    import pickle
    with open('path/to/file.pickle', 'rb') as input:
        data = pickle.load(input)
        # use data