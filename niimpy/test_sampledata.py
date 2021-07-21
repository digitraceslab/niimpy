"""Test that sample data can be opened.
"""

import pandas as pd
import pytest

import niimpy
from . import read
from . import sampledata


@pytest.mark.parametrize("datafile",
                         ['DATA_CSV',
                          'DATA2_CSV',
                          'MULTIUSER_AWAREBATTERY_CSV',
                          'MULTIUSER_AWARESCREEN_CSV',
                          'SURVEY_PHQ9',
                          ])
def test_sampledata_csv(datafile):
    """Test existence of reading of CSV sampledata"""
    filename = getattr(sampledata, datafile)
    data = niimpy.read_csv(filename)
    assert isinstance(data, pd.DataFrame)
    # The index should be set to the times
    assert isinstance(data.index, pd.DatetimeIndex)


@pytest.mark.parametrize("datafile",
                         ['DATA',
                          'MULTIUSER',
                          ])
def test_sampledata_sqlite(datafile):
    """Test existence and openining (not reading) of sqlite sampledata"""
    filename = getattr(sampledata, datafile)
    data = niimpy.open(filename)
    assert isinstance(data, niimpy.Data1)
