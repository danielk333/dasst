#!/usr/bin/env python

'''

'''

#Python standard import
from abc import abstractmethod
from typing import NoReturn, Type
import sys
import pickle

#Third party import
import numpy as np

#Local import
from .converter import Converter
from .persistence import register_converter


class ListConverter(Converter):
    '''
    
    '''

    def as_bytes(self, obj: list) -> bytes:
        bytes_data = pickle.dumps(obj)
        return bytes_data


    def from_bytes(self, byte_data: bytes) -> list:
        list_ = pickle.loads(byte_data)
        return list_

register_converter(list, ListConverter)