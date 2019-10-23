#!/usr/bin/env python

'''

'''
import sys
from typing import Type
import struct

import numpy as np
import xarray as xr

from dasst.persistence.converter import Converter, unpack
from dasst.persistence.file_system_binary import FileSystemBinary
from dasst.persistence.numpy_converter import NumpyConverter
from dasst.persistence.list_converter import ListConverter
from dasst.persistence import register_converter

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
        self.npc = NumpyConverter()
        self.metac = ListConverter()


    def as_bytes(self, obj: Type[MyClass]) -> bytes:
        byte_data = b''

        npc_data = self.npc.as_bytes(obj.data)
        byte_data += struct.pack('q', len(npc_data))
        byte_data += npc_data

        lst_data = self.metac.as_bytes([obj.num])
        byte_data += struct.pack('q', len(lst_data))
        byte_data += lst_data

        return byte_data


    def from_bytes(self, bytes_data: bytes) -> MyClass:
        
        size, bytes_data = unpack('q', bytes_data)
        npc_data = self.npc.from_bytes(bytes_data[:size[0]])
        bytes_data = bytes_data[size[0]:]

        size, bytes_data = unpack('q', bytes_data)
        lst_data = self.metac.from_bytes(bytes_data[:size[0]])

        obj = MyClass(lst_data[0])
        obj.data = npc_data

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

    my_object = MyClass(100)
    my_object.generate()

    fs = FileSystemBinary('test2.bin')

    fs.save(my_object)

    new_object = fs.load()

    print(my_object)
    print(new_object)
    