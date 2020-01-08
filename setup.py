#!/usr/bin/env python

from distutils.core import setup

setup(name='Niimpy',
      version='0.1.dev0',
      description='Behavorial data analysis',
      author='Richard Darst',
      author_email='rkd@zgib.net',
      url='https://github.com/CxAalto/niimpy',
      packages=['niimpy'],
      package_data={'niimpy': ['sampledata/*.sqlite3']},
      include_package_data=True,
  )
