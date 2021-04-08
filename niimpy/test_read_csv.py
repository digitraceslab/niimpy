import niimpy
from . import read
from . import sampledata

def test_read_csv():
    data = niimpy.read_csv(sampledata.DATA_CSV)