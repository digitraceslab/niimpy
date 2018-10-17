import datetime
import pandas as pd

import niimpy

DATA = 'sampledata-singleuser.sqlite3'

def test_connect():
    data = niimpy.open(DATA)
    data.users()

def test_users():
    data = niimpy.open(DATA)
    data.users()

def test_tables():
    data = niimpy.open(DATA)
    print(data.tables())

def test_user_table_counts():
    data = niimpy.open(DATA)
    print(data.user_table_counts())

def test_firstlast():
    data = niimpy.open(DATA)
    print(data.first('AwareScreen', user=niimpy.ALL))
    print(data.first('AwareScreen', user=niimpy.ALL))
    print(data.count('AwareScreen', user=niimpy.ALL))

def test_start_end():
    data = niimpy.open(DATA)
    print(data.count('AwareScreen', user=niimpy.ALL))
    assert data.count('AwareScreen', user=niimpy.ALL)['count'][0] == 1156
    # Beyond the end range - sholud be zero
    print(data.count('AwareScreen', user=niimpy.ALL, start=1532449041))
    assert data.count('AwareScreen', user=niimpy.ALL, start=1532449041)['count'][0] == 0
    assert data.count('AwareScreen', user=niimpy.ALL, start="2018-07-25")['count'][0] == 0
    # Range
    assert data.count('AwareScreen', user=niimpy.ALL, start="2018-07-11", end="2018-07-12")['count'][0] == 163
    assert data.count('AwareScreen', user=niimpy.ALL, start=datetime.datetime(2018,7,11), end=datetime.datetime(2018,7,12))['count'][0] == 163
    assert data.count('AwareScreen', user=niimpy.ALL, start=1531256400, end=1531342800)['count'][0] == 163

def test_quality():
    data = niimpy.open(DATA)
    data.quality('AwareScreen', user=niimpy.ALL)
    data.quality('AwareScreen', user=niimpy.ALL, limit=100)
    data.quality('AwareScreen', user=niimpy.ALL, limit=100, offset=10)
    data.quality('AwareScreen', user=niimpy.ALL, offset=10)
    data.quality('AwareScreen', user=niimpy.ALL, start='2018-07-12')
    data.quality('AwareScreen', user=niimpy.ALL, end='2018-07-12')

def test_hourly():
    data = niimpy.open(DATA)
    data.hourly('AwareScreen', user=niimpy.ALL)

    data.hourly('AwareScreen', user=niimpy.ALL, columns="screen_status")
    data.hourly('AwareScreen', user=niimpy.ALL, columns="screen_status", limit=100)
    data.hourly('AwareScreen', user=niimpy.ALL, columns="screen_status", limit=100, offset=10)
    data.hourly('AwareScreen', user=niimpy.ALL, columns="screen_status", offset=10)
    data.hourly('AwareScreen', user=niimpy.ALL, columns="screen_status", start='2018-07-12')
    data.hourly('AwareScreen', user=niimpy.ALL, columns="screen_status", end='2018-07-12')
    data.hourly('AwareScreen', user=niimpy.ALL, columns="screen_status")
    data.hourly('AwareScreen', user=niimpy.ALL, columns="screen_status")

def test_raw():
    data = niimpy.open(DATA)
    data.raw('AwareScreen', user=niimpy.ALL)
    data.raw('AwareScreen', user=niimpy.ALL, limit=100)
    data.raw('AwareScreen', user=niimpy.ALL, limit=100, offset=10)
    data.raw('AwareScreen', user=niimpy.ALL, offset=10)
    data.raw('AwareScreen', user=niimpy.ALL, start='2018-07-12')
    data.raw('AwareScreen', user=niimpy.ALL, end='2018-07-12')

# Sample db doesn't have this data yet.
#def test_get_survey_score():
#    data = niimpy.open(DATA)


def test_filled_bins():
    data = niimpy.open(DATA)
    timestamps = data.raw("AwareScreen", None).index
    gb2 = niimpy.util.interval_group(timestamps)
    gb2.loc['2018-07-09 21:00:00']['filled_bins'] == 1
    gb2.loc['2018-07-10 09:00:00']['filled_bins'] == 4

def test_filled_bins_ints():
    timestamps = pd.Series([1, 10, 50, 600, 900, 3600, 3601, 4201])
    gb2 = niimpy.util.interval_group(timestamps)
    print(gb2)
    assert gb2.loc['1970-01-01 00:00:00']['filled_bins'] == 2
    assert gb2.loc['1970-01-01 01:00:00']['filled_bins'] == 1
