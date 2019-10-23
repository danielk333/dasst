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


class Converter:

    @abstractmethod
    def as_bytes(self, obj: object) -> bytes:
        pass


    @abstractmethod
    def from_bytes(self, byte_data: bytes) -> object:
        pass

