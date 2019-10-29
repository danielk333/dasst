#!/usr/bin/env python

'''

'''
import sys
from typing import Type
import struct
import os

import numpy as np
import xarray as xr

from dasst.persistence import FileSystemBinary, GZipBinary
from dasst.persistence import NumpyConverter
from dasst.persistence import PickleConverter
from dasst.persistence import register_converter, ChainConverter, Converter

from dasst.profiling import set_loggers


set_loggers(level=10, logfile = './')


class MyBase:
    pass

class MyClass(MyBase):
    def __init__(self, num: int):
        self.data = None
        self.num = num

    def generate(self):
        self.data = np.random.randn(self.num)

    def __str__(self):
        with np.printoptions(precision=3, suppress=True):
            str_ = str(self.data)
        str_ += f'\n size: {self.num}'
        return str_


class MyClassConverter(Converter):

    def __init__(self):
        self.converters = [NumpyConverter(), PickleConverter()]
        self.chain = ChainConverter()


    def as_bytes(self, obj: Type[MyClass]) -> bytes:
        objects = [obj.data, obj.num]
        return self.chain.pack_bytes_stream(objects, self.converters)


    def from_bytes(self, bytes_data: bytes) -> MyClass:
        objects = self.chain.unpack_bytes_stream(self.converters, bytes_data)

        obj = MyClass(objects[1])
        obj.data = objects[0]

        return obj

register_converter(MyClass, MyClassConverter)

if __name__ == '__main__':

    from dasst.persistence import PERSISTENT_OBJECTS
    print('All registered converters for persistency')
    for item, value in PERSISTENT_OBJECTS.items():
        print(f'{item}: {value}')

    data = np.random.randn(5, 2)

    fs = FileSystemBinary('test.bin')

    fs.save(data)
    new_data = fs.load()

    print(data)
    print(new_data)

    my_object = MyClass(1000)
    my_object.generate()

    fs = FileSystemBinary('test2.bin')
    fs_compressed = GZipBinary('test2.gz', level=9)

    fs.save(my_object)
    fs_compressed.save(my_object)

    new_object = fs.load()
    new_object_comp = fs_compressed.load()

    print(my_object)
    print(new_object)
    print(new_object_comp)
    
    print(os.path.getsize(fs.path))
    print(os.path.getsize(fs_compressed.path))