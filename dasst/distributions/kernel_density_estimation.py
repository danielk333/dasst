#!/usr/bin/env python

'''Doc

'''

#Python standard import
from typing import Union

#Third party import
import numpy as np

#Local import
from .distribution import Distribution
from .scipy import MvnNorm


def MISE_kernel_optimization(kde_dist):
    #https://link.springer.com/article/10.1007/s10827-009-0180-4
    #
    #implement the functions described in the paper and use 
    #scipy to minimize them
    #
    # kde_dist.bandwidth = result
    return NotImplementedError('TODO')


class KernelDensityEstimation(Distribution):
    '''Axis is the axis that samples are distributed along
    '''

    def __init__(self, distribution: np.ndarray, bandwidth: np.ndarray, axis = 0):
        assert len(distribution.shape) <= 2, 'Dimensions must be concentrated along one axis'
        self.distribution = distribution
        self.axis = axis
        self.bandwidth = bandwidth
        self.kernel = MvnNorm()


    def sample(self, size: Union[tuple,int], **kwargs) -> np.ndarray:
        '''Docstring
        '''
        if isinstance(size, tuple):
            if len(size) > 1:
                raise TypeError(f'Size for sampling cannot be multidimensional: "{size}"')
            size = size[0]

        dims = [slice(None)]*len(self.distribution.shape)
        dims[self.axis] = np.random.randint(0,self.distribution.shape[self.axis], size=size)

        samples = self.distribution[tuple(dims)].copy()
        for ind_ in range(size):
            dims[self.axis] = ind_
            samples[tuple(dims)] = self.kernel.sample(size = 1, mean=samples[tuple(dims)], cov=self.bandwidth)

        return samples



    def pdf(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        dims = [slice(None)]*len(self.distribution.shape)

        #TODO: we can here put a exclusion radius that only 
        #      uses samples that are sufficiently close to x

        for ind_ in range(self.distribution.shape[self.axis]):
            dims[self.axis] = ind_
            kp = self.kernel.pdf(x, mean=self.distribution[tuple(dims)], cov=self.bandwidth)
            if ind_ == 0:
                p_ = kp
            else:
                p_ += kp

        p_ /= self.distribution.shape[self.axis]

        return p_
        


    def logpdf(self, x: np.ndarray, **kwargs) -> np.ndarray:
        '''Docstring
        '''
        return np.log(self.pdf(x))