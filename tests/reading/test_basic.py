import datetime
import os
import pandas as pd
import time

import pytest

import niimpy
from niimpy import config

DATA = config.SQLITE_SINGLEUSER_PATH

TZ = os.environ['TZ'] = 'Europe/Helsinki'
time.tzset() #

def test_connect():
    data = niimpy.open(DATA, tz=TZ)
    data.users()

def test_users():
    data = niimpy.open(DATA, tz=TZ)
    data.users()

def test_tables():
    data = niimpy.open(DATA, tz=TZ)
    print(data.tables())

def test_user_table_counts():
    data = niimpy.open(DATA, tz=TZ)
    print(data.user_table_counts())

def test_username_validatation_singleuser():
    data = niimpy.open(niimpy.sampledata.DATA, tz=TZ)
    with pytest.raises(ValueError):
        data.validate_username('some_name')
    # Should return the proper value
    assert data.validate_username(niimpy.ALL)  == niimpy.ALL
    assert data.validate_username(None) == niimpy.ALL

def test_username_validatation_multiuser():
    data = niimpy.open(niimpy.sampledata.MULTIUSER, tz=TZ)
    with pytest.raises(ValueError):   # None not allowed for multiuser
        data.validate_username(None)
    with pytest.raises(ValueError):   # Not a string
        data.validate_username(5)
    assert data.validate_username('jd9INuQ5BBlW') == 'jd9INuQ5BBlW'
    # Username not in the DB, this does not raise an error currently:
    assert data.validate_username('abcdefg') == 'abcdefg'
    assert data.validate_username(niimpy.ALL) == niimpy.ALL

def test_firstlast():
    data = niimpy.open(DATA, tz=TZ)
    print(data.first('AwareScreen', user=niimpy.ALL))
    print(data.first('AwareScreen', user=niimpy.ALL))
    print(data.count('AwareScreen', user=niimpy.ALL))
    print(data.exists('AwareScreen', user=niimpy.ALL))

def test_start_end():
    data = niimpy.open(DATA, tz=TZ)
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

def test_occurrence_db():
    data = niimpy.open(DATA, tz=TZ)
    occs = data.occurrence('AwareScreen', user=niimpy.ALL)
    data.occurrence('AwareScreen', user=niimpy.ALL, limit=100)
    data.occurrence('AwareScreen', user=niimpy.ALL, limit=100, offset=10)
    data.occurrence('AwareScreen', user=niimpy.ALL, offset=10)
    data.occurrence('AwareScreen', user=niimpy.ALL, start='2018-07-12')
    data.occurrence('AwareScreen', user=niimpy.ALL, end='2018-07-12')
    data.occurrence('AwareScreen', user=niimpy.ALL, bin_width=720)

    assert occs['occurrence']['2018-07-10 00:00:00'] == 1
    assert occs['occurrence']['2018-07-10 12:00:00'] == 4
    #assert occs['hour']['2018-07-10 12:00:00'] == 12
    #assert occs['day']['2018-07-10 12:00:00'] == '2018-07-10'

def test_util_occurrence():
    data = niimpy.open(DATA, tz=TZ)
    timestamps = data.timestamps('AwareScreen', niimpy.ALL)
    occs = niimpy.util.occurrence(timestamps)
    assert occs['occurrence']['2018-07-10 00:00:00'] == 1
    assert occs['occurrence']['2018-07-10 12:00:00'] == 4

def test_hourly():
    data = niimpy.open(DATA, tz=TZ)
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
    data = niimpy.open(DATA, tz=TZ)
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
    data = niimpy.open(DATA, tz=TZ)
    timestamps = data.raw("AwareScreen", None).index
    gb2 = niimpy.util.occurrence(timestamps)
    gb2.loc['2018-07-10 00:00:00']['occurrence'] == 1
    gb2.loc['2018-07-10 12:00:00']['occurrence'] == 4

    gb2 = niimpy.util.occurrence(timestamps, bins=5)
    gb2.loc['2018-07-10 00:00:00']['occurrence'] == 1
    gb2.loc['2018-07-10 12:00:00']['occurrence'] == 4

def test_filled_bins_ints():
    timestamps = pd.Series([1, 10, 50, 600, 900, 3600, 3601, 4201])
    timestamps = pd.to_datetime(timestamps, unit='s')
    gb2 = niimpy.util.occurrence(timestamps)
    print(gb2)
    assert gb2.loc['1970-01-01 00:00:00']['occurrence'] == 2
    assert gb2.loc['1970-01-01 01:00:00']['occurrence'] == 1


def test_to_datetime():
    with niimpy.util.tmp_timezone('Europe/Helsinki'):
        # pd.Series as input
        x = niimpy.util.to_datetime(pd.Series([0, 1]))
        # This should be localtime in Europe/Helsinki
        assert x[0].hour == 2

        # raw unixtime list as input
        x = niimpy.util.to_datetime([0, 1])
        assert x[0].hour == 2

    with niimpy.util.tmp_timezone('Europe/Berlin'):
        x = niimpy.util.to_datetime(pd.Series([0, 1]))
        # This should be localtime in Europe/Helsinki
        assert x[0].hour == 1


def test_df_normalize():
    df = pd.DataFrame({'time': [0, 3600, 7200], 'x': [2, 3, 5]})
    niimpy.util.df_normalize(df, tz=TZ)
    assert df['x']['1970-01-01 03:00:00'] == 3
    assert df.iloc[1]['datetime'].hour == 3

    df = pd.DataFrame({'day': (['2018-01-01']*3), 'hour':[2, 3, 4], 'x': [2, 3, 5]})
    print(df)
    niimpy.util.df_normalize(df, tz=TZ)
    print(df)
    assert df['x']['2018-01-01 03:00:00'] == 3
    assert df.index[1].hour == 3
