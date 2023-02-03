import io

import numpy
from pandas import Series

import niimpy

TZ = 'Europe/Helsinki'
csv = io.StringIO(
"""\
user,time,value
a,0,0
a,100,1
a,3700,2
b,90000,3
b,90001,4
b,90002,5
"""
    )

def test_filter_dataframe():
    df = niimpy.read_csv(csv, tz=TZ)
    assert len(niimpy.filter_dataframe(df)) == 6

    # User limits
    assert len(niimpy.filter_dataframe(df, user='a')) == 3

    # Time limits
    assert len(niimpy.filter_dataframe(df, end='1970-01-01')) == 3
    assert len(niimpy.filter_dataframe(df, start='1970-01-02')) == 3
    assert len(niimpy.filter_dataframe(df, start='1970-01-01 02:01:00', end='1970-01-01')) == 2
    df2 = niimpy.filter_dataframe(df, start='1970-01-01 02:01:00', end='1970-01-01')
    numpy.testing.assert_array_equal(df2['value'].values, [1,2])

    # Renaming columns
    assert 'new' in niimpy.filter_dataframe(df, rename_columns={'value': 'new'})
