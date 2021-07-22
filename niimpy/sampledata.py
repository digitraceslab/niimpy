"""
Sample data of different types
"""

import os

_dirname = os.path.join(os.path.dirname(__file__), 'sampledata')

# A simple single-user dataset, containing a little bit of Aware
# screen data.
DATA = os.path.join(_dirname, 'singleuser.sqlite3')
DATA_CSV = os.path.join(_dirname, 'singleuser.csv')

# A simple multi-user dataset: one user, two devices, AwareScreen and AwareBattery
MULTIUSER = os.path.join(_dirname, 'multiuser.sqlite3')
MULTIUSER_AWAREBATTERY_CSV = os.path.join(_dirname, 'multiuser_AwareBattery.csv')
MULTIUSER_AWARESCREEN_CSV = os.path.join(_dirname, 'multiuser_AwareScreen.csv')

# A simple single-user csv dataset
DATA2_CSV = os.path.join(_dirname, 'AwareBattery.csv')

# A syntethic survey PHQ9 dataset
SURVEY_PHQ9 = os.path.join(_dirname, 'survey_phq9.csv')

# Aware screen/battery for one month.
SCREEN_MONTH = os.path.join(_dirname, 'AwareScreen_1month.csv.gz')
BATTERY_MONTH = os.path.join(_dirname, 'AwareBattery_1month.csv.gz')
