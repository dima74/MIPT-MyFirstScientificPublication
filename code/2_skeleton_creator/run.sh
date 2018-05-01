#!/bin/sh -e
set -x

# подготовка
cd `dirname $0`
touch code/directory_with_links_to_images_fake_empty_file_so_that_rm_dont_give_error  # TODO improve this
rm -f code/directory_with_links_to_images*
rm -rf directory_with_links_to_images
mkdir directory_with_links_to_images

cd directory_with_links_to_images
#ln -s ../../1_data_discrete/as_png/* .  # TODO extract path to directory with images to variable
find ../../1_data_discrete/as_png -exec ln -s "{}" . \;
cd ..

ln -s ../directory_with_links_to_images code/

# запуск кода скелетонизации
cd code
python make_bones.py 7 0 directory_with_links_to_images

# преобразование скелетов в numpy файл
cd ..
rm -rf skeletons.npy
python convert_results_to_numpy_format.py