#!/usr/bin/env python

'''

'''
import os

import numpy as np
from dasst.persistence import FileSystemBinary, GZipBinary

data = np.arange(100000)

fs = FileSystemBinary('test.bin', append=False)
fs_compressed = GZipBinary('test.gz', level=9, append=False)

fs.save(data)
fs_compressed.save(data)

print(os.path.getsize(fs.path))
print(os.path.getsize(fs_compressed.path))

ratio = os.path.getsize(fs_compressed.path)/os.path.getsize(fs.path)*100

print(f'{ratio} %')