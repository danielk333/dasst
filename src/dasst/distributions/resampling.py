#!/usr/bin/env python

'''Doc

'''

#Python standard import
from typing import Union

#Third party import
import numpy as np

#Local import
from .distribution import Distribution



class Resampling(Distribution):
    '''Axis is the axis that samples are distributed along
    '''

    def __init__(self, distribution: np.ndarray, axis=0):
        self.distribution = distribution
        self.axis = axis

    def sample(self, size: Union[tuple,int], **kwargs) -> np.ndarray:
        '''Docstring
        '''
        if isinstance(size, tuple):
            if len(size) > 1:
                raise TypeError(f'Size for resampling cannot be multidimensional: "{size}"')
            size = size[0]

        dims = [slice(None)]*len(self.distribution.shape)
        dims[self.axis] = np.random.randint(0,self.distribution.shape[self.axis], size=size)
        return self.distribution[tuple(dims)].copy()
