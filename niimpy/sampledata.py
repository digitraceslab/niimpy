"""
Sample data of different types
"""

import os

_dirname = os.path.join(os.path.dirname(__file__), 'sampledata')

# A simple single-user dataset
DATA = os.path.join(_dirname, 'singleuser.sqlite3')
DATA_CSV = os.path.join(_dirname, 'singleuser.csv')

# A simple multi-user dataset: one user, two devices, AwareScreen and AwareBattery
MULTIUSER = os.path.join(_dirname, 'multiuser.sqlite3')
MULTIUSER_AWAREBATTERY_CSV = os.path.join(_dirname, 'multiuser_AwareBattery.csv')
MULTIUSER_AWARESCREEN_CSV = os.path.join(_dirname, 'multiuser_AwareScreen.csv')

# A simple single-user csv dataset
DATA2_CSV = os.path.join(_dirname, 'AwareBattery.csv')
