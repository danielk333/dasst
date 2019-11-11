#!/usr/bin/env python

'''Doc

'''

#Python standard import
from abc import abstractmethod

#Third party import
import numpy
import scipy.stats as st

#Local import
from .distribution import Distribution


class ScipyDistribution(Distribution):
    '''Docstring
    '''

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



class NormDistribution(ScipyDistribution):
    def __init__(self):
        self._scipy_dist = st.norm


class UniformDistribution(ScipyDistribution):
    def __init__(self):
        self._scipy_dist = st.uniform


class ExpDistribution(ScipyDistribution):
    def __init__(self):
        self._scipy_dist = st.expon


class HalfNormDistribution(ScipyDistribution):
    def __init__(self):
        self._scipy_dist = st.halfnorm



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