import niimpy
from . import read
from . import sampledata

def test_read_sql():
    data = niimpy.read_sql(sampledata.DATA, table='AwareScreen')
        