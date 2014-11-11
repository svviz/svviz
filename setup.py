# from distutils.core import setup, Extension
from setuptools import setup, Extension, find_packages

setup(name='svviz',
      version='1.0',
      install_requires = ['pyfaidx', 'pysam', 'flask', 'joblib'],
      # packages=['svviz', 'ssw'],
      packages = find_packages("src"),
      package_dir = {"": "src"},#{"ssw":"src/ssw", "svviz":"src/svviz"},
      ext_modules=[Extension('ssw/libssw', ['src/ssw/ssw.c'])],
      entry_points={
        'console_scripts' : ["svviz = svviz.app:main"]
        },
      include_package_data = True,
      package_data = {"": ["*.html", "*.css", "*.js"]}
      )