import numpy as np
import pandas as pd
import math
import pytest

import niimpy.preprocessing.tracker as tracker
from niimpy import config


def test_step_summary():
    df = pd.read_csv(config.STEP_SUMMARY_PATH, index_col=0)
    # Converting the index as date
    df.index = pd.to_datetime(df.index)
    df = df.rename(columns={"subject_id": "user"})
    df["extra_column"] = "extra"

    summary_df = tracker.step_summary(df, value_col = 'steps')

    assert "extra_column" not in summary_df.columns
    assert summary_df['max_sum_step'].values[0] == 13025
    assert summary_df['min_sum_step'].values[0] == 5616
    assert round(summary_df['avg_sum_step'].values[0], 2) == 8437.38
    assert round(summary_df['std_sum_step'].values[0], 2) == 3352.35
    assert summary_df['median_sum_step'].values[0], 2 == 6480.0


def test_step_distribution():
    df = pd.read_csv(config.STEP_SUMMARY_PATH, index_col=0)
    # Converting the index as date
    df.index = pd.to_datetime(df.index)
    df = df.rename(columns={"subject_id": "user"})

    res = tracker.extract_features_tracker(df)

    assert isinstance(res, pd.DataFrame)
    assert math.isclose(res.loc[(res["user"] == 'wiam9xme') & (res.index == '2021-07-03 19:00:00')][
               'step_distribution'].values[0], 0.025162, rel_tol = 0.0001), "Incorrect daily distribution calculation"


def test_daily_step_distribution_with_short_timeframe():
    df = pd.read_csv(config.STEP_SUMMARY_PATH, index_col=0)

    df.index = pd.to_datetime(df.index)
    df = df.rename(columns={"subject_id": "user"})
    
    with pytest.raises(ValueError) as exc_info:
        tracker.tracker_step_distribution(df,
            timeframe= '1s',
            resample_args= {'rule': '1d'}
        )
