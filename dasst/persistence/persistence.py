#!/usr/bin/env python

'''

'''

#Python standard import
from abc import abstractmethod
from typing import NoReturn

#Third party import


#Local import
from .logger import logger


PERSISTENT_OBJECTS = {}
_ID_length = 10

def register_converter(cls, converter):
    global PERSISTENT_OBJECTS

    name = repr(cls)
    logger.debug(f'Registering "{name}" as a converter')
    if name not in PERSISTENT_OBJECTS:
        PERSISTENT_OBJECTS[name] = (cls, converter, len(PERSISTENT_OBJECTS))
    else:
        logger.warning(f'Converter "{name}" already registered')


class Persistence:

    def save(self, obj: object) -> NoReturn:
        logger.debug(f'{self.__class__}: Saving object {type(obj)}')

        for type_, converter, ID in PERSISTENT_OBJECTS.values():
            if isinstance(obj, type_):
                logger.debug(f'{self.__class__}: Using converter "{repr(converter)}"')

                obj_converter = converter()

                bytes_data = ID.to_bytes(_ID_length, byteorder='big', signed=False)
                bytes_data += obj_converter.as_bytes(obj)
                
                self.save_bytes(bytes_data)
                break


    def load(self) -> object:
        logger.debug(f'{self.__class__}: Loading object')

        byte_data = self.load_bytes()
        data_ID = int.from_bytes(byte_data[:_ID_length], byteorder='big', signed=False)
        byte_data = byte_data[_ID_length:]

        for type_, converter, ID in PERSISTENT_OBJECTS.values():
            if data_ID == ID:
                logger.debug(f'{self.__class__}: Using converter "{repr(converter)}" and type "{repr(type_)}"')

                obj_converter = converter()
                return obj_converter.from_bytes(byte_data)


    @abstractmethod
    def save_bytes(self, byte_data: bytes) -> NoReturn:
        pass


    @abstractmethod
    def load_bytes(self) -> bytes:
        pass
