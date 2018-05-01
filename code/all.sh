#!/bin/sh -e
set -x

cd `dirname $0`
./clear_all_results.sh

cd `dirname $0`/1_data_discrete
python ./convert_to_directory_with_png_files.py
python ./convert_to_single_pickle_file.py

cd `dirname $0`/2_skeleton_creator
./run.sh

cd `dirname $0`/3_features_generator
python ./features_generator.py

cd `dirname $0`/4_merge_data_and_features
python ./merge_data_and_features.py