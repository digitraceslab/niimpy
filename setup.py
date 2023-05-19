#!/usr/bin/env python

from setuptools import setup, find_packages
from os.path import join, dirname

with open("README.md", "r") as fh:
    long_description = fh.read()

requirementstxt = join(dirname(__file__), "requirements.txt")
requirements = [ line.strip() for line in open(requirementstxt, "r") if line.strip() ]

setup(name='niimpy',
      version=1.1,
      description='Behavorial data analysis',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Digitraceslab',
      author_email='talayeh.aledavood@aalto.fi',
      url='https://github.com/digitraceslab/niimpy',
      #packages=['niimpy', 'niimpy.preprocessing', 'niimpy.reading'],
      packages=find_packages(where='.'),
      package_data={'niimpy': ['sampledata/*.sqlite3', 'sampledata/*.csv','config/config.ini']},
      include_package_data=True,
      python_requires=">=3.6",
      install_requires=requirements,
      classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],

  )
