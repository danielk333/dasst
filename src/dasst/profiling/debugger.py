#!/usr/bin/env python

'''

'''

#Python standard import
import pdb
import traceback
import logging

#Third party import


#Local import


def try_wrapper(exceptions = (Exception, ), logger = None, level = logging.DEBUG):
    def tryw(func):
        def try_func(*args, **kwargs):

            try:
                ret = func(*args, **kwargs)
            except exceptions:
                traceback_str = traceback.format_exc()
                if logger is not None:
                    logger.log(level, traceback_str)
                    logger.log(level, 'Arguments: \n  args  : ' + str(args) + '\n  kwargs: ' + str(kwargs))
                ret = None

            return ret
        return try_func

    return tryw


def pdb_try_wrapper(exceptions = (Exception, )):
    def pdb_try(func):
        def try_func(*args, **kwargs):

            try:
                ret = func(*args, **kwargs)
            except exceptions:
                traceback.print_exc()
                pdb.post_mortem()

            return ret
        return try_func

    return pdb_try
