import os
import sys
from termcolor import colored
import time

all_time = time.time()

pruning = int(sys.argv[1])
idx = int(sys.argv[2])


if os.system("cd ./PatternSpectrumConsole && make") == 0:
    print(colored("MAKE DONE", 'green'))
else:
    print(colored("MAKE FAILED", 'red'))
    sys.exit()

for filename in sys.argv[3:]:
    print(colored("-------------------------------------", "magenta"))
    print(colored("Processing {0}".format(filename), "blue"))

    if os.system("python3 gen_filestxt.py ./{0}".format(filename)) == 0:
        print(colored("Generate file with pictures paths and names OK", 'green'))
    else:
        print(colored("Generate file with pictures paths and names  FAILED", 'red'))
        sys.exit()

    #class_type = filename[:filename.find('_')]
    class_type = filename.replace(os.sep, '').replace('.', '')
    print(class_type)
    class_label = (0 if class_type == "normal" else 1)
    if os.system("cp {0}_files_paths.txt ./PatternSpectrumConsole/{0}_files_paths.txt".format(class_type)) == 0:
        print(colored("Copy files with path to PatternSpectrumConsole OK", "green"))
    else:
        print(colored("Copy files with path to PatternSpectrumConsole FAILED", "red"))
        sys.exit()

    print(colored("Processing PatternSpectrum for bones", "yellow"))
    start = time.time()
    name = "bones" + str(idx)
    if os.system("cd ./PatternSpectrumConsole && ./PatternSpectrumConsole 3 0.05 {0}_files_paths.txt {1} {0}_{2}.txt {3}".format(class_type, class_label, name, pruning)) == 0:
        print(colored("Processing PatternSpectrum for bones OK", "green"))
    else:
        print(colored("Processing PatternSpectrum for bones FAILED", "red"))
        sys.exit()
    print(colored("PROCESSING TIME: {0} s".format(time.time() - start), "magenta"))
    if os.system("mv ./PatternSpectrumConsole/{0}_{1}.txt ./{0}_{1}.txt".format(class_type, name)) == 0:
        print(colored("Move files bones to ./ OK", "green"))
    else:
        print(colored("Move files bones to ./ FAILED", "red"))
        sys.exit()        
    
print(colored("-------------------------------------", "cyan"))
print(colored("TOTAL TIME: {0} s".format(time.time() - all_time), "cyan"))
