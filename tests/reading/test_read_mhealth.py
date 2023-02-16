import pandas as pd
import numpy as np

import niimpy
from niimpy import config


def test_read_mhealth_total_sleep_time():
    """test reading mixed mhealth data from the example file."""
    data = niimpy.reading.mhealth.total_sleep_time_from_file(config.MHEALTH_TOTAL_SLEEP_TIME_PATH)
    assert data['total_sleep_time'][0] == 465.0
    assert data['total_sleep_time_unit'][0] == "min"
    assert data['descriptive_statistic'][1] == "average"
    assert data['descriptive_statistic_denominator'][1] == "d"
    assert data['date'][3] == pd.to_datetime("2013-02-05")
    assert data['part_of_day'][3] == "evening"
    assert data['start'][0] == pd.to_datetime("2016-02-06 04:35:00+00:00")
    assert data['end'][0] == pd.to_datetime("2016-02-06 14:35:00+00:00")
    assert data['start'][2] == pd.to_datetime("2013-01-26 07:35:00+00:00")
    assert data['end'][2] == pd.to_datetime("2013-02-05 07:35:00+00:00")
