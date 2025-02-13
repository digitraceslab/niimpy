"""Test that sample data can be opened.
"""

import pandas as pd
import pytest
from niimpy import config

import niimpy
from niimpy.reading import csv
from niimpy.preprocessing import sampledata

TZ = 'Europe/Helsinki'

@pytest.mark.parametrize("datafile",
                         ['MULTIUSER_AWARE_BATTERY_PATH',
                          'MULTIUSER_AWARE_SCREEN_PATH',
                          'GPS_PATH',
                          'SURVEY_PATH'
                          ])
def test_sampledata_csv(datafile):
    """Test existence of reading of CSV sampledata"""
    filename = getattr(config, datafile)
    data = niimpy.read_csv(filename, tz=TZ)
    assert isinstance(data, pd.DataFrame)
    # The index should be set to the times
    #assert isinstance(data.index, pd.DatetimeIndex)


@pytest.mark.parametrize("datafile",
                         ['MULTIUSER_AWARE_BATTERY_PATH',
                          'MULTIUSER_AWARE_SCREEN_PATH',
                          'GPS_PATH'
                          ])
def test_datetime_index_csv(datafile):
    """Test that those CSV sampledata have datetime index"""
    filename = getattr(config, datafile)
    data = niimpy.read_csv(filename, tz=TZ)
    # The index should be set to the times
    assert isinstance(data.index, pd.DatetimeIndex)
    
@pytest.mark.parametrize("datafile",
                         ['SQLITE_SINGLEUSER_PATH',
                          'SQLITE_MULTIUSER_PATH',
                          ])
def test_sampledata_sqlite(datafile):
    """Test existence and openining (not reading) of sqlite sampledata"""
    filename = getattr(config, datafile)
    data = niimpy.open(filename)
    assert isinstance(data, niimpy.Data1)
