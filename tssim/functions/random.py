"""This module is contains the numpy.random wrapper."""

import numpy as np

from .wrapper import NumpyWrapper

# Simple random data
# https://docs.scipy.org/doc/numpy/reference/routines.random.html#simple-random-data
rand = NumpyWrapper(np.random.rand)
randn = NumpyWrapper(np.random.randn)
randint = NumpyWrapper(np.random.randint, "kwarg")
random_integers =NumpyWrapper(np.random.random_integers, "kwarg")
random_sample =NumpyWrapper(np.random.random_sample, "kwarg")
random =NumpyWrapper(np.random.random, "kwarg")
ranf =NumpyWrapper(np.random.ranf, "kwarg")
sample =NumpyWrapper(np.random.sample, "kwarg")
choice =NumpyWrapper(np.random.choice, "kwarg")
bytes = NumpyWrapper(np.random.bytes)
