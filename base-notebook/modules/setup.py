# for modules compile
import sys
from distutils.core import setup
from Cython.Build import cythonize
args = sys.argv

setup(
    name="module",
    ext_modules=cythonize(args[3]),  # accepts a glob pattern
)
