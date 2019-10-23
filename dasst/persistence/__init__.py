#!/usr/bin/env python

'''

'''

#Python standard import
from abc import ABC
from abc import abstractmethod
from typing import NoReturn, Type, Generic

#Third party import


#Local import


PERSISTENT_OBJECTS = {}


class Persistence:

    def save(self, obj: object) -> NoReturn:
        for type_, converter in PERSISTENT_OBJECTS.values():
            if isinstance(obj, type_):
                obj_converter = converter(obj)
                self.save_bytes(obj_converter.as_bytes())
                break


    def load(self, cls: Type[object]) -> object:
        for type_, converter in PERSISTENT_OBJECTS.values():
            if cls is type_:
                obj_converter = converter(None)
                return obj_converter.from_bytes(self.load_bytes())


    @abstractmethod
    def save_bytes(self, byte_data: bytes) -> NoReturn:
        pass


    @abstractmethod
    def load_bytes(self) -> bytes:
        pass

