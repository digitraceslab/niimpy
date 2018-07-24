import datetime

import niimpy

DATA = 'Sample.sqlite3'

def test_connect():
    data = niimpy.Data1(DATA)
    data.users()

def test_users():
    data = niimpy.Data1(DATA)
    data.users()

def test_tables():
    data = niimpy.Data1(DATA)
    print(data.tables())

def test_user_table_counts():
    data = niimpy.Data1(DATA)
    print(data.user_table_counts())

def test_firstlast():
    data = niimpy.Data1(DATA)
    print(data.first('AwareScreen', user=niimpy.ALL))
    print(data.first('AwareScreen', user=niimpy.ALL))
    print(data.count('AwareScreen', user=niimpy.ALL))

def test_start_end():
    data = niimpy.Data1(DATA)
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
    data = niimpy.Data1(DATA)
    data.hourly('AwareScreen', columns="screen_status", user=niimpy.ALL)

def test_hourly():
    data = niimpy.Data1(DATA)
    data.hourly('AwareScreen', user=niimpy.ALL, columns="screen_status")

def test_raw():
    data = niimpy.Data1(DATA)
    data.raw('AwareScreen', user=niimpy.ALL)

# Sample db doesn't have this data yet.
#def test_get_survey_score():
#    data = niimpy.Data1(DATA)

