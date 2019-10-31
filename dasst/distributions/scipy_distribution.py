#!/usr/bin/env python

'''Converter abstract definition and converting helper functions

'''

#Python standard import
from abc import abstractmethod

#Third party import
import numpy
import scipy.stats as st

#Local import
from .distribution import Distribution


def scipy_distribution_generator(name):

    class ScipyDistribution(Distribution):
        '''Docstring
        '''

        def __init__(self):
            self._scipy_dist = getattr(st, name)


        def sample(self, shape: tuple, **kwargs) -> numpy.ndarray:
            '''Docstring
            '''
            kwargs['size'] = shape
            return self._scipy_dist.rvs(**kwargs)

        def logcdf(self, x: numpy.ndarray, **kwargs) -> numpy.ndarray:
            '''Docstring
            '''
            return self._scipy_dist.logcdf(x, **kwargs)


        def logpdf(self, x: numpy.ndarray, **kwargs) -> numpy.ndarray:
            '''Docstring
            '''
            return self._scipy_dist.logpdf(x, **kwargs)


        def cdf(self, x: numpy.ndarray, **kwargs) -> numpy.ndarray:
            '''Docstring
            '''
            return self._scipy_dist.cdf(x, **kwargs)


        def pdf(self, x: numpy.ndarray, **kwargs) -> numpy.ndarray:
            '''Docstring
            '''
            return self._scipy_dist.pdf(x, **kwargs)

    return ScipyDistribution


NormDistribution = scipy_distribution_generator('norm')
UniformDistribution = scipy_distribution_generator('uniform')
ExpDistribution = scipy_distribution_generator('expon')
HalfNormDistribution = scipy_distribution_generator('halfnorm')


class CustomDiscreteDistribution(Distribution):
    '''Docstring
    '''

    def __init__(self, x, p):
        '''Docstring
        '''
        self._scipy_dist = st.rv_discrete(name='custm', values=(x, p))


    def sample(self, shape: tuple, **kwargs) -> numpy.ndarray:
        '''Docstring
        '''
        kwargs['size'] = shape
        return self._scipy_dist.rvs(**kwargs)


    def logcdf(self, x: numpy.ndarray, **kwargs) -> numpy.ndarray:
        '''Docstring
        '''
        return self._scipy_dist.logcdf(x, **kwargs)


    def logpmf(self, x: numpy.ndarray, **kwargs) -> numpy.ndarray:
        '''Docstring
        '''
        return self._scipy_dist.logpmf(x, **kwargs)


    def cdf(self, x: numpy.ndarray, **kwargs) -> numpy.ndarray:
        '''Docstring
        '''
        return self._scipy_dist.cdf(x, **kwargs)


    def pmf(self, x: numpy.ndarray, **kwargs) -> numpy.ndarray:
        '''Docstring
        '''
        return self._scipy_dist.pmf(x, **kwargs)