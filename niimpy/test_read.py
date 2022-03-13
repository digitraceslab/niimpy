import pandas as pd
import numpy as np

import niimpy
from . import read
from . import sampledata

TZ = 'Europe/Helsinki'

def test_read_preprocess_add_group():
    """Test of add_group= option"""
    data = pd.DataFrame({'user': ['u1', 'u2', 'u3'], 'a': [1,2,3], 'b': [4,5,6]})
    data2 = read._read_preprocess(data, add_group='group1')
    assert 'group' in data2
    assert (data2['group'] == 'group1').all()


def test_read_preprocess_add_group_csv():
    """Test of add_group= option"""
    data = niimpy.read_csv(sampledata.DATA_CSV, add_group='group1', tz=TZ)
    assert 'group' in data
    assert data['group'][0] == 'group1'
