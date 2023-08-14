#!/usr/bin/env python

"""


"""

from typing import NoReturn
from .persistence import Persistence


class FileSystemBinary(Persistence):
    def __init__(self, path, append=True):
        self.path = path
        if append:
            self.mode = "a"
        else:
            self.mode = "w"

    def save_bytes(self, byte_data: bytes) -> NoReturn:
        with open(self.path, self.mode + "b") as fh:
            fh.write(byte_data)

    def load_bytes(self, offset: int, size: int) -> bytes:
        with open(self.path, "rb") as fh:
            fh.seek(offset, 0)
            if size == 0:
                byte_data = fh.read()
            else:
                byte_data = fh.read(size)
        return byte_data
