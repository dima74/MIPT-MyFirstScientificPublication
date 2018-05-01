# данный файл используется только для отладки

import numpy as np

skeletons = np.load('../2_skeleton_creator/skeletons.npy')
np.save('single_skeleton.npy', skeletons[:1])