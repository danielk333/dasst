#!/usr/bin/env python

'''

'''

#Python standard import
from abc import abstractmethod
from typing import NoReturn, Type
import sys
import struct

#Third party import
import numpy as np

#Local import
from .converter import Converter
from .converter import unpack
from . import register_converter


class NumpyConverter(Converter):
    '''
    
    Note: 10s strings because the longest dtype identifier is "complex128" which is 10 chars long
    '''

    def as_bytes(self, obj: np.ndarray) -> bytes:
        bytes_data = b''
        bytes_data += struct.pack('q', obj.ndim)
        bytes_data += struct.pack('c', obj.dtype.char.encode('utf-8'))
        bytes_data += struct.pack(obj.ndim*'q', *obj.shape)
        bytes_data += obj.tobytes(order='C')

        return bytes_data


    def from_bytes(self, byte_data: bytes) -> np.ndarray:

        num, byte_data = unpack('q', byte_data)
        dtype, byte_data = unpack('c', byte_data)
        shape, byte_data = unpack(num[0]*'q', byte_data)

        dtype = dtype[0].decode('utf-8')
        count = 1
        for dim in shape:
            count *= dim

        np_array = np.frombuffer(byte_data, dtype=dtype, count=count, offset=0)
        np_array = np_array.reshape(*shape)

        return np_array

register_converter(np.ndarray, NumpyConverter)