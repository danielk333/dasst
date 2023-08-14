#!/usr/bin/env python

"""

TODO: extend with https://stackabuse.com/python-zlib-library-tutorial/
"""

import zlib
from .file_system_binary import FileSystemBinary


class GZipBinary(FileSystemBinary):
    def __init__(self, path, level, **kwargs):
        self.level = level
        super(GZipBinary, self).__init__(path, **kwargs)

    def compress(self, byte_data: bytes) -> bytes:
        return zlib.compress(byte_data, self.level)

    def decompress(self, byte_data: bytes) -> bytes:
        return zlib.decompress(byte_data)
