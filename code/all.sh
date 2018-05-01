#!/bin/sh -e
set -x
ROOT="$( cd "$(dirname "$0")" ; pwd -P )"

cd $ROOT
./clear_all_results.sh

cd $ROOT/1_data_discrete
python ./convert_to_directory_with_png_files.py
python ./convert_to_single_pickle_file.py

cd $ROOT/2_skeleton_creator
./run.sh

cd $ROOT/3_features_generator
python ./features_generator.py

cd $ROOT/4_merge_data_and_features
python ./merge_data_and_features.py