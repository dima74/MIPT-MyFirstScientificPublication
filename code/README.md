# Классификация символов

## `/1_data_discrete`
* папка `generated` — получаю от Андрея, содержит дискретное описание изображения в numpy формате
* папка `as_png` — создаётся после запуска `convert_to_directory_with_png_files.py`, содержит файлы изображений в формате PNG
* файл `data.pickle` — создаётся после запуска `convert_to_single_numpy_file`, содержит словарь
 
        {
            'I': (None, 64, 64),
            'y': (None, 1),
        }

Код для чтения:

    import pickle
    with open('1_data_discrete/data.pickle', 'rb') as input:
        data = pickle.load(input)
    I, y = data['I'], data['y']

## `/2_skeleton_creator`
* файл `skeletons.npy` — создаётся после запуска `run.sh`, содержит массив скелетов (каждый скелет --- массив вещественных чисел)

## `/3_features_generator`
После запуска `features_generator.py` создаются
* файл `features.pickle` — содержит словарь

        {
            'F': [{
                'nodes_features': (number_vertexes, number_features), 
                'adjacency_list': <array of arrays>,
            }]
        }

* файл `data_for_visualization.pickle` — содержит информацию о циклах и прямых линиях для графов

## `/4_merge_data_and_features`
* файл `data_and_features.pickle` — создаётся после запуска `merge_data_and_features.py`, содержит словарь

        {
            'y': (None, 1),
            'I': (None, 64, 64),
            'F': [{
                'nodes_features': (number_vertexes, number_features), 
                'adjacency_list': Бarray of arrays>,
            }]
        }