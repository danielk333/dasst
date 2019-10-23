#!/usr/bin/env python

'''

'''
import sys
from typing import Type

import numpy as np

from dasst.persistence.converter import Converter
from dasst.persistence.file_system import FileSystem
from dasst.persistence import PERSISTENT_OBJECTS


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

    def __init__(self, obj: Type[MyClass]):
        self.obj = obj
        self.offset = sys.getsizeof(int)


    def as_bytes(self):
        byte_data = b''
        byte_data += self.obj.num.to_bytes(self.offset, byteorder='big', signed=False)
        byte_data += self.obj.data.tobytes(order='C')
        return byte_data


    def from_bytes(self, byte_data: bytes):
        
        num = int.from_bytes(byte_data[0:self.offset], byteorder='big', signed=False)
        data = np.frombuffer(byte_data[:], dtype=np.float64, count=num, offset=self.offset)

        obj = MyClass(num)
        obj.data = data

        return obj

PERSISTENT_OBJECTS['MyClass'] = (MyClass, MyClassConverter)


if __name__ == '__main__':

    my_object = MyClass(100)
    my_object.generate()

    fs = FileSystem('test.bin')

    fs.save(my_object)

    new_object = fs.load(MyClass)

    print(my_object)
    print(new_object)