import pandas as pd
from pandas import Timestamp

import niimpy
from niimpy.util import TZ

def test_screen():
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
