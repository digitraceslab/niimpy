"""
Sample data of different types
"""

import os

_dirname = os.path.join(os.path.dirname(__file__), 'sampledata')
# A simple single-user dataset
DATA = os.path.join(_dirname, 'singleuser.sqlite3')
# A simple multi-user dataset: one user, two devices, AwareScreen and AwareBattery
MULTIUSER = os.path.join(_dirname, 'multiuser.sqlite3')
