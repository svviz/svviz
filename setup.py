# from distutils.core import setup, Extension
import os
from setuptools import setup, Extension, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read()

def get_version(string):
    """ Parse the version number variable __version__ from a script. """
    import re
    version_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
    version_str = re.search(version_re, string, re.M).group(1)
    return version_str

setup(
      name='svviz',
      version=get_version(open('src/svviz/__init__.py').read()),

      install_requires = ['requests', 'numpy', 'pyfaidx', 'pysam >= 0.7.8', 'flask', 'joblib'],

      # Packages
      packages = find_packages("src"),
      package_dir = {"": "src"},#{"ssw":"src/ssw", "svviz":"src/svviz"},

      # C extension
      ext_modules=[Extension('ssw/libssw',
                             ['src/ssw/ssw.c'],
                             include_dirs=["src/ssw"])],

      # Command line script
      entry_points={
        'console_scripts' : ["svviz = svviz.app:main"]
        },

      # Data
      include_package_data = True,
      package_data = {"": ["*.html", "*.css", "*.js"]},

      # Overview
      description='A read visualizer for structural variants',
      long_description=long_description,

      # The project's main homepage.
      url='https://github.com/svviz/svviz',

      # Author details
      author='Noah Spies',
      author_email='nspies@stanford.edu',

      # Metadata
      license='MIT',
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License",
          "Intended Audience :: Science/Research",
          "Natural Language :: English",
          "Operating System :: Unix",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 2.6",
          "Topic :: Scientific/Engineering :: Bio-Informatics",
          "Topic :: Scientific/Engineering :: Visualization"
          ],

      # What does your project relate to?
      keywords='bioinformatics, structural variants, sequence analysis',

      )