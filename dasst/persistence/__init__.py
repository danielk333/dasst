#!/usr/bin/env python

'''

'''

#Python standard import
from abc import abstractmethod
from typing import NoReturn

#Third party import


#Local import


PERSISTENT_OBJECTS = {}
_ID_length = 10


class Persistence:

    def save(self, obj: object) -> NoReturn:
        for type_, converter, ID in PERSISTENT_OBJECTS.values():
            if isinstance(obj, type_):
                obj_converter = converter()

                bytes_data = ID.to_bytes(_ID_length, byteorder='big', signed=False)
                bytes_data += obj_converter.as_bytes(obj)
                
                self.save_bytes(bytes_data)
                break


    def load(self) -> object:
        byte_data = self.load_bytes()
        data_ID = int.from_bytes(byte_data[:_ID_length], byteorder='big', signed=False)
        byte_data = byte_data[_ID_length:]

        for type_, converter, ID in PERSISTENT_OBJECTS.values():
            if data_ID == ID:
                obj_converter = converter()
                return obj_converter.from_bytes(byte_data)


    @abstractmethod
    def save_bytes(self, byte_data: bytes) -> NoReturn:
        pass


    @abstractmethod
    def load_bytes(self) -> bytes:
        pass


def register_converter(cls, converter):
    PERSISTENT_OBJECTS[repr(cls)] = (cls, converter, len(PERSISTENT_OBJECTS))