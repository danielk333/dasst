#!/usr/bin/env python

'''

'''

#Python standard import
from abc import abstractmethod
from typing import NoReturn, Type
import struct

#Third party import


#Local import


def unpack(fmt, bytes_data):
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, bytes_data[:size]), bytes_data[size:]


class ChainConverter:

    def pack_bytes_stream(self, objects, converters):
        bytes_stream = b''
        for item, converter in zip(objects, converters):
            byte_data = converter.as_bytes(item)
            bytes_stream += struct.pack('q', len(byte_data))
            bytes_stream += byte_data
        return bytes_stream

    def unpack_bytes_stream(self, converters, bytes_stream):
        objects = []
        for converter in converters:
            size, bytes_stream = unpack('q', bytes_stream)
            objects.append(converter.from_bytes(bytes_stream[:size[0]]))
            bytes_stream = bytes_stream[size[0]:]
        return objects


class Converter:

    @abstractmethod
    def as_bytes(self, obj: object) -> bytes:
        pass


    @abstractmethod
    def from_bytes(self, byte_data: bytes) -> object:
        pass

