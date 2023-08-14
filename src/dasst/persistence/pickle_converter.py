#!/usr/bin/env python

"""

"""
import pickle

from .converter import Converter
from .persistence import register_converter


class PickleConverter(Converter):
    """ """

    def as_bytes(self, obj: object) -> bytes:
        bytes_data = pickle.dumps(obj)
        return bytes_data

    def from_bytes(self, byte_data: bytes) -> object:
        list_ = pickle.loads(byte_data)
        return list_


register_converter(list, PickleConverter)
register_converter(dict, PickleConverter)
register_converter(str, PickleConverter)
register_converter(float, PickleConverter)
register_converter(int, PickleConverter)
register_converter(complex, PickleConverter)
register_converter(set, PickleConverter)
register_converter(tuple, PickleConverter)
