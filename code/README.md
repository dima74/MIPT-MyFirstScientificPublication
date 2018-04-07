# Классификация символов

## `/1_data_discrete`
* папка `as_numpy` — получаю от Андрея, содержит дискретное описание изображения в numpy формате
* папка `as_png` — создаётся после запуска `convert_to_directory_with_png_files.py`, содержит файлы изображений в формате PNG
* файл `data.npy` — создаётся после запуска `convert_to_single_numpy_file`, содержит словарь
 
        {
            'I': (None, 28, 28),
            'y': (None, 1),
        }

## `/2_skeleton_creator`
* файл `skeletons.npy` — создаётся после запуска `run.sh`, содержит массив скелетов

## `/3_features_generator`
* файл `features.npy` — создаётся после запуска `features_generator.py`, содержит словарь

        {
            'F': [{
                'nodes_features': <number_vertexes, number_features>, 
                'adjacency_list': <array of arrays>,
            }]
        }