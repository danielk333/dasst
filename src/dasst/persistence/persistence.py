#!/usr/bin/env python

'''

'''

#Python standard import
from abc import abstractmethod
from typing import NoReturn
from collections.abc import Iterable

#Third party import


#Local import
from .logger import logger


PERSISTENT_OBJECTS = {}


def register_converter(cls, converter):
    global PERSISTENT_OBJECTS

    name = repr(cls)
    logger.debug(f'Registering "{name}" as a converter')
    if name not in PERSISTENT_OBJECTS:
        PERSISTENT_OBJECTS[name] = (cls, converter, len(PERSISTENT_OBJECTS))
    else:
        logger.warning(f'Converter "{name}" already registered, replacing')
        PERSISTENT_OBJECTS[name] = (cls, converter, PERSISTENT_OBJECTS[name][2])


class Persistence:

    ID_len = 10
    SIZE_len = 64
    HEAD_len = ID_len + SIZE_len

    def save(self, obj: object) -> NoReturn:
        logger.debug(f'{self.__class__}: Saving object {type(obj)}')

        for type_, converter, ID in PERSISTENT_OBJECTS.values():
            if isinstance(obj, type_):
                logger.debug(f'{self.__class__}: Using converter "{repr(converter)}"')

                obj_converter = converter()

                obj_bytes = self.compress(obj_converter.as_bytes(obj))

                bytes_data = ID.to_bytes(Persistence.ID_len, byteorder='big', signed=False)
                bytes_data += len(obj_bytes).to_bytes(Persistence.SIZE_len, byteorder='big', signed=False)
                bytes_data += obj_bytes
                
                self.save_bytes(bytes_data)
                break


    def load(self, index = None):
        logger.debug(f'{self.__class__}: Loading object(s) (index = {repr(index)})')

        if isinstance(index, Iterable):
            load_list = [(__id, __place) for __place, __id in enumerate(index)]
            load_list.sort()
        elif isinstance(index, int):
            load_list = [(index,0),]
        else:
            load_list = []

        offset = 0
        obj_ind = 0
        load_ind = 0
        load_size = len(load_list)
        if index is not None:
            objects = [None]*load_size
        else:
            objects = []

        while True:
            byte_data = self.load_bytes(
                offset=offset,
                size=Persistence.HEAD_len
            )
            offset += Persistence.HEAD_len

            if len(byte_data) == 0:
                break

            converter_ID = int.from_bytes(byte_data[:Persistence.ID_len], byteorder='big', signed=False)
            data_length = int.from_bytes(byte_data[Persistence.ID_len:], byteorder='big', signed=False)

            if index is None:
                __add = True
            else:
                if obj_ind == load_list[load_ind][0]:
                    __add = True
                else:
                    __add = False

            if __add:
                obj_bytes = self.load_bytes(offset=offset, size=data_length)
                obj = self._convert_bytes(
                    converter_ID, 
                    self.decompress(obj_bytes),
                )
                if index is not None:
                    objects[load_list[load_ind][1]] = obj
                    load_ind += 1
                else:
                    objects.append(obj)


            if index is not None and load_ind >= load_size:
                break

            offset += data_length
            obj_ind += 1


        if len(objects) == 0:
            return None
        elif len(objects) == 1:
            return objects[0]
        else:
            return objects


    def _convert_bytes(self, converter_ID: int, byte_data: bytes) -> object:
        for type_, converter, ID in PERSISTENT_OBJECTS.values():
            if converter_ID == ID:
                logger.debug(f'{self.__class__}: Using converter "{repr(converter)}" and type "{repr(type_)}"')

                obj_converter = converter()
                return obj_converter.from_bytes(byte_data)


    def compress(self, byte_data: bytes) -> bytes:
        return byte_data


    def decompress(self, byte_data: bytes) -> bytes:
        return byte_data


    @abstractmethod
    def save_bytes(self, byte_data: bytes) -> NoReturn:
        pass


    @abstractmethod
    def load_bytes(self, offset: int, size: int) -> bytes:
        pass
