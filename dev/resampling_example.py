'''
This is my example script
=========================

Docstring for this example
'''

import numpy as np
import matplotlib.pyplot as plt

from dasst.distributions import Resampling

np.random.seed(1)

samples = np.random.randn(3, 100)

dist = Resampling(samples, axis=1)

resamples = dist.sample(1000)

fig, ax = plt.subplots(3,1)
for i in range(3):
    ax[i].hist(samples[i,:])

fig, ax = plt.subplots(3,1)
for i in range(3):
    ax[i].hist(resamples[i,:])

plt.show()