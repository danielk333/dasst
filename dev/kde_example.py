'''
This is my example script
=========================

Docstring for this example
'''

import numpy as np
import matplotlib.pyplot as plt

from dasst.distributions import KernelDensityEstimation

np.random.seed(1)


x = np.linspace(-2,2,num=100)

for i in [10, 100]:

    samples = np.random.randn(1, i)
    bandwidth = np.eye(1)*0.2

    dist = KernelDensityEstimation(samples, bandwidth, axis=1)

    resamples = dist.sample(2000)

    fig, ax = plt.subplots(3,1)
    ax[0].hist(samples.flatten())
    ax[1].hist(resamples.flatten())
    ax[2].plot(x, dist.pdf(x))

plt.show()