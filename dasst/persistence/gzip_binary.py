#!/usr/bin/env python

'''

TODO: extend with https://stackabuse.com/python-zlib-library-tutorial/
'''

#Python standard import
from typing import NoReturn
import zlib

#Third party import


#Local import
from .persistence import Persistence


class GZipBinary(Persistence):

    def __init__(self, path, level, append=False):
        self.path = path
        self.level = level
        if append:
            self.mode = 'a'
        else:
            self.mode = 'w'


    def save_bytes(self, byte_data: bytes) -> NoReturn:
        with open(self.path, self.mode + 'b') as fh:
            fh.write(zlib.compress(byte_data, self.level))


    def load_bytes(self) -> bytes:
        with open(self.path,'rb') as fh:
            byte_data = zlib.decompress(fh.read())
        return byte_data
