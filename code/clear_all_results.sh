#!/bin/sh -e
set -x
cd `dirname $0`

rm -rf 1_data_discrete/as_png
rm -f 1_data_discrete/data.pickle
rm -f 2_skeleton_creator/skeletons.npy
rm -f 3_features_generator/features.pickle
rm -f 4_merge_data_and_features/data_and_features.pickle