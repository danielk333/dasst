'''
This is my example script
=========================

Docstring for this example
'''

import numpy as np
import matplotlib.pyplot as plt

np.random.seed(1)

alt = np.linspace(77e3, 120e3, num=200)
dat = np.random.randn(200)

plt.plot(alt, dat)
