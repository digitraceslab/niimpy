import niimpy
from niimpy.reading import csv
from niimpy.preprocessing import sampledata

TZ = 'Europe/Helsinki'

def test_read_sqlite():
    data = niimpy.read_sqlite(sampledata.DATA, table='AwareScreen', tz=TZ)

def test_read_sqlite_tables():
    assert niimpy.read_sqlite_tables(sampledata.DATA) == {'AwareScreen'}
