"""
Sample data of different types
"""

import os

'''
path = os.getcwd()
print(path)
parent = os.path.abspath(os.path.join(path, os.pardir))
print(parent)
'''

SAMPLEDATA_DIR = os.path.join(os.path.dirname(__file__),'..', 'sampledata')
_dirname = SAMPLEDATA_DIR


#_dirname = os.path.join(parent,'sampledata')


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


# Data for tests
TEST_STEP_SUMMARY = os.path.join(_dirname, 'step_summary.csv')
TEST_SCREEN_1 = os.path.join(_dirname, 'test_screen_1.csv')
TEST_BATTERY_1 = os.path.join(_dirname, 'test_battery_1.csv')
LOCATION_FILE = os.path.join(_dirname, 'gps.csv')
AUDIO_FILE = os.path.join(_dirname, 'multiuser_AwareAudio.csv')
SCREEN_FILE = os.path.join(_dirname, 'multiuser_AwareScreen.csv')
CALLS_FILE = os.path.join(_dirname, 'multiuser_AwareCalls.csv')
BATTERY_FILE = os.path.join(_dirname, 'multiuser_AwareBattery.csv')
SMS_FILE = os.path.join(_dirname, 'multiuser_AwareMessages.csv')
APPS_FILE = os.path.join(_dirname, 'singleuser_AwareApplicationNotifications.csv')
