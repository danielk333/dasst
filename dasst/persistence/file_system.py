#!/usr/bin/env python

'''


'''

#Python standard import
from typing import NoReturn

#Third party import

#Local import
from . import wrapper
from . import Persistence


class FileSystem(Persistence):

    def __init__(self, path):
        self.path = path


    def save_bytes(self, byte_data: bytes) -> NoReturn:
        with open(self.path,'wb') as fh:
            fh.write(byte_data)


    def load_bytes(self) -> bytes:
        with open(self.path,'rb') as fh:
            byte_data = fh.read()
        return byte_data