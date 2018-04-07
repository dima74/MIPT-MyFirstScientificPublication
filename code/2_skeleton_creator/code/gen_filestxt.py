import os
import sys

path = sys.argv[1]

class_type = path.replace(os.sep, '').replace('.', '')
class_label = (0 if class_type == 'normal' else 1)

pictures = list(filter(lambda x : x.endswith(".png"), os.listdir(path)))
pictures = list(map(lambda x : '../' + path[2:] + '/' + x, pictures))

picture_names = list(map(lambda x : x[x.rfind('_') - 2 : x.rfind('_') - 1], pictures))
picture_names = list(filter(len, picture_names))

fout = open(class_type + "_files_paths.txt", "w")
print(*pictures, sep="\n", file=fout)
fout.close()

fout = open(class_type + "_words_names.txt", "w")
print(*picture_names, sep="\n", file=fout)
fout.close()
