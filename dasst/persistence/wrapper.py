#!/usr/bin/env python

'''

'''

#Python standard import

#Third party import

#Local import

def DataSaveWrapperGenerator(xdata_save, *args, **kwargs):
    fargs = args
    del args
    fkwargs = kwargs
    del kwargs

    def DataSaveWrapper(func):
        
        def wrapped_func(*args, **kwargs):
            ret = func(*args, **kwargs)
            xdata_save(ret, *fargs, **fkwargs)
            return ret

        return wrapped_func

    return DataSaveWrapper

