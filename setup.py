# from distutils.core import setup, Extension
from setuptools import setup, Extension

setup(name='ssw',
      version='1.0',
      install_requires = ['pyfaidx', 'pysam', 'flask', 'joblib'],
      packages=['svviz', 'ssw'],
      ext_modules=[Extension('ssw/libssw', ['ssw/ssw.c'])],
      entry_points={
        'console_scripts' : ["svviz = svviz.app:main"]
        }
      )