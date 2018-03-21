import os
import shutil

for directory in ['testing', 'training']:
    directory_all = directory + '_all'
    if not os.path.exists(directory_all):
        os.makedirs(directory_all)

    for digit in range(0, 10):
        digit_directory = '{}/{}'.format(directory, digit)
        for filename in os.listdir(digit_directory):
            source_file = '{}/{}'.format(digit_directory, filename)
            shutil.copy(source_file, directory_all)
