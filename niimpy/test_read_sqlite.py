import niimpy
from . import read
from . import sampledata

def test_read_sqlite():
    data = niimpy.read_sqlite(sampledata.DATA, table='AwareScreen')

def test_read_sqlite_tables():
    assert niimpy.read_sqlite_tables(sampledata.DATA) == {'AwareScreen'}
