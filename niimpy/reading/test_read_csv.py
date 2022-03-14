import pandas as pd
import numpy as np

import niimpy
from . import read
from . import sampledata

TZ = 'Europe/Helsinki'

def test_read_csv():
    data = niimpy.read_csv(sampledata.DATA_CSV, tz=TZ)
    # The index should be set to the times
    assert isinstance(data.index, pd.DatetimeIndex)
    # There should be a column 'datetime' added in the setup.
    assert 'datetime' in data
