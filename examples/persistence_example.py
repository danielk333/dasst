'''
This is my example script
=========================

Docstring for this example
'''

import numpy as np
from dasst.persistence import FileSystemBinary

np.random.seed(1)

data = np.random.randn(200)

fs = FileSystemBinary('/tmp/dasst_example_cache.bin')
fs.save(data)

loaded_data = fs.load(data)

print('Reconstruction error:')
print(np.mean(data - loaded_data))