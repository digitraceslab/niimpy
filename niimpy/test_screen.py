import io

import pandas as pd
from pandas import Timestamp
import pytest

import niimpy
from niimpy.util import TZ


def test_screen_duration():
    screen  = niimpy.read_csv(niimpy.sampledata.TEST_SCREEN_1)
    battery = niimpy.read_csv(niimpy.sampledata.TEST_BATTERY_1)
    duration, count = niimpy.preprocess.screen_duration(screen, battery=battery)
    print('duration:')
    print(duration)
    print('count:')
    print(count)
    # On and off duration during this day
    assert duration.loc[Timestamp('1970-01-01', tz=niimpy.util.TZ), 'on'] == 10
    assert duration.loc[Timestamp('1970-01-01', tz=niimpy.util.TZ), 'off'] == 540
    # on==1 for some reason
    assert count.loc[Timestamp('1970-01-01', tz=niimpy.util.TZ), 'on_count'] == 1
    assert count.loc[Timestamp('1970-01-01', tz=niimpy.util.TZ), 'off_count'] == 1



@pytest.fixture
def screen1():
    return niimpy.read_csv_string("""\
time,screen_status
0,1
60,0
600,1
610,0
1700,1
3600,1
3601,2
""")

@pytest.fixture
def battery1():
    return niimpy.read_csv_string("""\
time,battery_level,battery_status
1800,,-1
""")

def test_screen_off(screen1, battery1):
    off = niimpy.preprocess.screen_off(screen1, battery=battery1)
    print(off)
    #import pdb ; pdb.set_trace()
    assert pd.Timestamp(60,  unit='s', tz=TZ) in off.index
    assert pd.Timestamp(610, unit='s', tz=TZ) in off.index
    # Phone was turned on at 1700, and battery ran out at 1800.
    assert pd.Timestamp(1800, unit='s', tz=TZ) in off.index
