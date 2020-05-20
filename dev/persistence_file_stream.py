#!/usr/bin/env python

'''

'''
import numpy as np
from dasst.persistence import FileSystemBinary
from dasst.profiling import set_loggers

set_loggers(level=10)

if __name__ == '__main__':

    fs1 = FileSystemBinary('test.bin')
    data = np.random.randn(2,2)
    print(data)
    fs1.save(data)
    print(fs1.load())
    print(fs1.load(0))

    print('='*30)

    fs2 = FileSystemBinary('test2.bin')
    for i in range(4):
        data = np.random.randn(2,2)
        fs2.save(data)

    print(fs2.load(2))
    print(fs2.load([0,2]))
    print(fs2.load())
