#!/usr/bin/env python

'''Doc

'''

#Python standard import
from abc import abstractmethod
from typing import Union

#Third party import
import numpy as np
import scipy.stats as st

#Local import
from .distribution import Distribution


class Scipy(Distribution):
    '''Docstring
    '''

    def sample(self, size: Union[tuple,int], **kwargs) -> np.ndarray:
        '''Docstring
        '''
        kwargs['size'] = size
        return self._scipy_dist.rvs(**kwargs)

    def logcdf(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        return self._scipy_dist.logcdf(x, **kwargs)


    def logpdf(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        return self._scipy_dist.logpdf(x, **kwargs)


    def cdf(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        return self._scipy_dist.cdf(x, **kwargs)


    def pdf(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        return self._scipy_dist.pdf(x, **kwargs)



class MvnNorm(Scipy):
    def __init__(self):
        self._scipy_dist = st.multivariate_normal


class Norm(Scipy):
    def __init__(self):
        self._scipy_dist = st.norm


class Uniform(Scipy):
    def __init__(self):
        self._scipy_dist = st.uniform


class Exp(Scipy):
    def __init__(self):
        self._scipy_dist = st.expon


class HalfNorm(Scipy):
    def __init__(self):
        self._scipy_dist = st.halfnorm



class CustomDiscrete(Distribution):
    '''Docstring
    '''

    def __init__(self, x, p):
        '''Docstring
        '''
        self._scipy_dist = st.rv_discrete(name='custm', values=(x, p))


    def sample(self, size: Union[tuple,int], **kwargs) -> np.ndarray:
        '''Docstring
        '''
        kwargs['size'] = size
        return self._scipy_dist.rvs(**kwargs)


    def logcdf(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        return self._scipy_dist.logcdf(x, **kwargs)


    def logpmf(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        return self._scipy_dist.logpmf(x, **kwargs)


    def cdf(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        return self._scipy_dist.cdf(x, **kwargs)


    def pmf(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        return self._scipy_dist.pmf(x, **kwargs)