import numpy as np
import pandas as pd

import niimpy.preprocessing.tracker as tracker
from niimpy.preprocessing import sampledata

def test_step_summary():
    
    df = pd.read_csv(sampledata.TEST_STEP_SUMMARY, index_col=0)
    # Converting the index as date
    df.index = pd.to_datetime(df.index)

    summary_df = tracker.step_summary(df, value_col='steps')
    assert summary_df['max_sum_step'].values[0] == 13025
    assert summary_df['min_sum_step'].values[0] == 5616
    assert round(summary_df['avg_sum_step'].values[0], 2) == 8437.38
    assert round(summary_df['std_sum_step'].values[0], 2) == 3352.35
    assert summary_df['median_sum_step'].values[0], 2 == 6480.0