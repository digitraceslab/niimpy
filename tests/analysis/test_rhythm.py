import os
import pandas as pd
import pytest

import niimpy
import niimpy.analysis.rhythms as rh
from niimpy import config

import datetime
import pytz

# Define starting dates
start_date_1 = datetime.datetime(2019, 8, 13, tzinfo=pytz.timezone('Etc/GMT+3'))
start_date_2 = datetime.datetime(2020, 1, 9, tzinfo=pytz.timezone('Etc/GMT+2'))

# Generate timestamps for 2 weeks with multiple records per day
timestamps_1 = [(start_date_1 + datetime.timedelta(days=i, hours=j)).strftime('%Y-%m-%d %H:%M:%S%z') 
                for i in range(14) for j in range(0, 24, 8)]
timestamps_2 = [(start_date_2 + datetime.timedelta(days=i, hours=j)).strftime('%Y-%m-%d %H:%M:%S%z') 
                for i in range(14) for j in range(0, 24, 8)]

# Combine data for both users
timestamps = timestamps_1 + timestamps_2
users = ['iGyXetHE3S8u'] * len(timestamps_1) + ['jd9INuQ5BBlW'] * len(timestamps_2)

# Generate sample outgoing and incoming counts
outgoing_counts = [i % 3 for i in range(len(timestamps))]
incoming_counts = [i % 2 + 1 for i in range(len(timestamps))]

data = {
    "time": timestamps,
    "user": users,
    "outgoing_count": outgoing_counts,
    "incoming_count": incoming_counts,
}

df = pd.DataFrame(data)
df["time"] = pd.to_datetime(df["time"])
df = df.set_index("time")

# 1. Basic functionality test
def test_basic_daily_rhythms():
    result = rh.compute_rhythms(
        df,
        timebin="1H",
        cols=["outgoing_count", "incoming_count"],
        groupby_cols=["user"],
        period=24,
        freq="daily",
    )
    assert len(result) > 0, "The result should not be empty."
    assert all(
        col in result.columns
        for col in [
            "outgoing_count",
            "outgoing_count_distr",
            "incoming_count",
            "incoming_count_distr",
        ]
    ), "Required columns are missing."


def test_basic_weekly_rhythms():
    result = rh.compute_rhythms(
        df,
        timebin="1H",
        cols=["outgoing_count", "incoming_count"],
        groupby_cols=["user"],
        period=168,
        freq="weekly",
    )
    assert len(result) > 0, "The result should not be empty."
    assert all(
        col in result.columns
        for col in [
            "outgoing_count",
            "outgoing_count_distr",
            "incoming_count",
            "incoming_count_distr",
        ]
    ), "Required columns are missing."


# 2. Validate DateTime index requirement
def test_validate_datetime_index():
    df_wrong_index = df.reset_index()
    with pytest.raises(
        ValueError, match="The input DataFrame must have a DateTime index."
    ):
        rh.compute_rhythms(
            df_wrong_index,
            timebin="1H",
            cols=["outgoing_count", "incoming_count"],
            groupby_cols=["user"],
            period=24,
            freq="daily",
        )


# 3. Handling of incorrect frequencies
def test_incorrect_frequency():
    with pytest.raises(
        ValueError,
        match="The specified frequency 'monthly' is not valid. Choose 'daily' or 'weekly'.",
    ):
        rh.compute_rhythms(
            df,
            timebin="1H",
            cols=["outgoing_count", "incoming_count"],
            groupby_cols=["user"],
            period=24,
            freq="monthly",
        )

# 4. Verification that aggregation is done correctly
def test_aggregation_daily():
    result = rh.compute_rhythms(
        df,
        timebin="1H",
        cols=["outgoing_count", "incoming_count"],
        groupby_cols=["user"],
        period=24,
        freq="daily",
    )
    assert (
        result.loc[result.index[0], "outgoing_count"] == 1
    ), "Aggregation failed for 'iGyXetHE3S8u'."


def test_aggregation_weekly():
    result = rh.compute_rhythms(
        df,
        timebin="1H",
        cols=["outgoing_count", "incoming_count"],
        groupby_cols=["user"],
        period=168,
        freq="weekly",
    )
    assert (
        result.loc[result.index[-1], "incoming_count"] == 6.0
    ), "Aggregation failed for 'jd9INuQ5BBlW'."