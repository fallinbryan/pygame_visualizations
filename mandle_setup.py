from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules = cythonize('mandleGen.pyx'))

## python mandle_setup.py build_ext --inplace