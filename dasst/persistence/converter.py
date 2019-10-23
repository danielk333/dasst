#!/usr/bin/env python

'''

'''

#Python standard import
from abc import ABC
from abc import abstractmethod
from typing import NoReturn

#Third party import


#Local import

class Converter:

    @abstractmethod
    def __init__(self, obj: object):
        pass


    @abstractmethod
    def as_bytes(self) -> bytes:
        pass


    @abstractmethod
    def from_bytes(self, byte_data) -> object:
        pass