# from distutils.core import setup, Extension
from setuptools import setup, Extension, find_packages

setup(name='svviz',
      version='1.0',
      install_requires = ['numpy', 'pyfaidx', 'pysam >= 0.7.8', 'flask', 'joblib'],

      # Packages
      packages = find_packages("src"),
      package_dir = {"": "src"},#{"ssw":"src/ssw", "svviz":"src/svviz"},

      # C extension
      ext_modules=[Extension('ssw/libssw', ['src/ssw/ssw.c'])],

      # Command line script
      entry_points={
        'console_scripts' : ["svviz = svviz.app:main"]
        },

      # Data
      include_package_data = True,
      package_data = {"": ["*.html", "*.css", "*.js"]}
      )