#!/usr/bin/env python

'''Docstring

'''

#Python standard import
from abc import abstractmethod
from typing import Union

#Third party import
import numpy as np

#Local import




class Distribution:
    '''Abstract distribution base class. 
    '''

    @abstractmethod
    def sample(self, size: Union[tuple,int], **kwargs) -> np.ndarray:
        '''Docstring
        '''
        pass


    def cdf(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        raise NotImplementedError()


    def logcdf(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        raise NotImplementedError()


    def pdf(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        raise NotImplementedError()


    def logpdf(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        raise NotImplementedError()


class InverseTransform(Distribution):
    '''Abstract distribution base class. 
    '''

    def sample(self, size: Union[tuple,int], **kwargs) -> np.ndarray:
        '''Docstring
        '''
        samples = np.random.rand(*size)
        samples = self.cdf_inverse(samples, **kwargs)
        return samples


    @abstractmethod
    def cdf_inverse(self, p: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        pass


class ForwardTransform(Distribution):
    '''Abstract distribution base class. 
    '''

    def __init__(self, base_distribution, base_kwargs):
        self.base_distribution = base_distribution
        self.base_kwargs = base_kwargs


    def sample(self, size: Union[tuple,int], **kwargs) -> np.ndarray:
        '''Docstring
        '''
        samples = self.base_distribution.sample(size, **self.base_kwargs)
        samples = self.transform(samples, **kwargs)
        return samples


    @abstractmethod
    def transform(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        pass

