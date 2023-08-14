'''
This is my example script
=========================

Docstring for this example
'''

import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

from dasst.distributions import InverseTransformDistribution

class MyDist(InverseTransformDistribution):

    def cdf_inverse(self, p: np.ndarray, **kwargs) -> np.ndarray:
        return norm.ppf(p, **kwargs)



np.random.seed(1)

dist = MyDist()
samples = dist.sample((10000,), loc=10)

plt.hist(samples,100)
plt.show()