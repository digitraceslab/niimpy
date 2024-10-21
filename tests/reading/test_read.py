import pandas as pd

import niimpy
from niimpy.preprocessing import util
from niimpy import config

TZ = 'Europe/Helsinki'

def test_read_preprocess_add_group():
    """Test of add_group= option"""
    data = pd.DataFrame({'user': ['u1', 'u2', 'u3'], 'a': [1,2,3], 'b': [4,5,6]})
    data2 = util.read_preprocess(data, add_group='group1')
    assert 'group' in data2
    assert (data2['group'] == 'group1').all()


def test_read_preprocess_add_group_csv():
    """Test of add_group= option"""
    data = niimpy.read_csv(config.MULTIUSER_AWARE_BATTERY_PATH, add_group='group1', tz=TZ)
    assert 'group' in data
    assert data.iloc[0]['group'] == 'group1'
