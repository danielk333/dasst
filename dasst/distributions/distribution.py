#!/usr/bin/env python

'''Docstring

'''

#Python standard import
from abc import abstractmethod

#Third party import
import numpy

#Local import




class Distribution:
    '''Abstract distribution base class. 
    '''

    @abstractmethod
    def sample(self, shape: tuple, **kwargs) -> numpy.ndarray:
        '''Docstring
        '''
        pass


    def cdf(self, x: numpy.ndarray, **kwargs) -> numpy.ndarray:
        '''Docstring
        '''
        raise NotImplementedError()


    def logcdf(self, x: numpy.ndarray, **kwargs) -> numpy.ndarray:
        '''Docstring
        '''
        raise NotImplementedError()


    def pdf(self, x: numpy.ndarray, **kwargs) -> numpy.ndarray:
        '''Docstring
        '''
        raise NotImplementedError()


    def logpdf(self, x: numpy.ndarray, **kwargs) -> numpy.ndarray:
        '''Docstring
        '''
        raise NotImplementedError()


class InverseTransformDistribution(Distribution):
    '''Abstract distribution base class. 
    '''

    def sample(self, shape: tuple, **kwargs) -> numpy.ndarray:
        '''Docstring
        '''
        samples = numpy.random.rand(*shape)
        samples = self.cdf_inverse(samples, **kwargs)
        return samples


    @abstractmethod
    def cdf_inverse(self, p: numpy.ndarray, **kwargs) -> numpy.ndarray:
        '''Docstring
        '''
        pass


class ForwardTransformDistribution(Distribution):
    '''Abstract distribution base class. 
    '''

    def __init__(self, base_distribution, base_kwargs):
        self.base_distribution = base_distribution
        self.base_kwargs = base_kwargs


    def sample(self, shape: tuple, **kwargs) -> numpy.ndarray:
        '''Docstring
        '''
        samples = self.base_distribution.sample(shape, **self.base_kwargs)
        samples = self.transform(samples, **kwargs)
        return samples


    @abstractmethod
    def transform(self, x: numpy.ndarray, **kwargs) -> numpy.ndarray:
        '''Docstring
        '''
        pass

