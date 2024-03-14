import numpy as np
import pandas as pd
import pytest

import niimpy.analysis.rhythms as rh
from niimpy import config

import datetime
import pytz

@pytest.fixture(scope='module')
def df():

    # Define starting dates
    start_date_1 = datetime.datetime(2019, 8, 13, tzinfo=pytz.timezone('Etc/GMT+3'))
    start_date_2 = datetime.datetime(2020, 1, 9, tzinfo=pytz.timezone('Etc/GMT+3'))
    start_date_3 = datetime.datetime(2020, 3, 4, tzinfo=pytz.timezone('Etc/GMT+3'))
    
    # Generate timestamps for 2 weeks with multiple records per day
    timestamps_1 = [(start_date_1 + datetime.timedelta(days=i, hours=j)).strftime('%Y-%m-%d %H:%M:%S%z') 
                    for i in range(14) for j in range(0, 24, 8)]
    timestamps_2 = [(start_date_2 + datetime.timedelta(days=i, hours=j)).strftime('%Y-%m-%d %H:%M:%S%z') 
                    for i in range(14) for j in range(0, 24, 8)]
    timestamps_3 = [(start_date_3 + datetime.timedelta(days=i, hours=j)).strftime('%Y-%m-%d %H:%M:%S%z') 
                    for i in range(14) for j in range(0, 24, 8)]
    
    # Combine data for both users
    timestamps = timestamps_1 + timestamps_2 + timestamps_3 
    users = ['iGyXetHE3S8u'] * len(timestamps_1) + ['jd9INuQ5BBlW'] * len(timestamps_2) + ['me2Mokdm2930'] * len(timestamps_3)
    groups = ['Control'] * len(timestamps_1) + ['Patient'] * len(timestamps_2) + ['Control'] * len(timestamps_3)
    
    # Generate sample outgoing and incoming counts
    outgoing_counts = [i % 3 for i in range(len(timestamps))]
    incoming_counts = [i % 2 + 1 for i in range(len(timestamps))]

    data = {
        "time": timestamps,
        "user": users,
        "groups": groups,
        "outgoing_count": outgoing_counts,
        "incoming_count": incoming_counts,
    }

    res = pd.DataFrame(data)
    res["time"] = pd.to_datetime(res["time"], errors='coerce')
    res = res.set_index("time")

    return res 

# 1. Basic functionality test
def test_correct_rhythms_colname(df):

    result = rh.compute_rhythms(
        df,
        timebin="2h",
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


def test_correct_daily_rhythm_index(df):   
    
    result = rh.compute_rhythms(
        df,
        timebin="6h",
        cols=["outgoing_count", "incoming_count"],
        groupby_cols=["user"],
        period=24,
        freq="daily",
    )

    expected_index = [0,6,12,18]
    assert len(result) > 0, "The result should not be empty."
    assert all(pd.Series(expected_index).isin(result.index)), "The index does not contain all required values."
    
def test_correct_daily_rhythm_distributions(df):

    result = rh.compute_rhythms(
        df,
        timebin="6h",
        cols=["outgoing_count", "incoming_count"],
        groupby_cols=["user"],
        period=24,
        freq="daily",
    )

    expected_outgoing_count_distr = [0, 0.33, 0.66, 0]
    expected_incoming_count_distr = [0.5, 0.33, 0.16, 0]

    outgoing_count_distr = result.query('user == "iGyXetHE3S8u"').outgoing_count_distr.tolist()
    incoming_count_distr = result.query('user == "iGyXetHE3S8u"').incoming_count_distr.tolist()
    
    assert len(result) > 0, "The result should not be empty."
    assert np.allclose(outgoing_count_distr, expected_outgoing_count_distr, atol=1e-2), "Incorrect distribution for outgoing_count"
    assert np.allclose(incoming_count_distr, expected_incoming_count_distr, atol=1e-2), "Incorrect distribution for incoming_count"

def test_correct_weekly_rhythm_index(df):   
    
    result = rh.compute_rhythms(
        df,
        timebin="6h",
        cols=["outgoing_count", "incoming_count"],
        groupby_cols=["user"],
        period=168,
        freq="weekly",
    )

    expected_index = ["Friday 00", "Friday 06", "Friday 12", "Friday 18"]
    assert len(result) > 0, "The result should not be empty."
    assert all(pd.Series(expected_index).isin(result.index)), "The index does not contain all required values."


def test_correct_weekly_rhythm_distributions(df):
    result = rh.compute_rhythms(
        df,
        timebin="6h",
        cols=["outgoing_count", "incoming_count"],
        groupby_cols=["user"],
        period=168,
        freq="weekly",
    )

    expected_outgoing_count_distr = [0, 0.047, 0.095, 0] * 7
    expected_incoming_count_distr = [0.03, 0.06, 0.03, 0.0, 0.09, 0.06, 0.03, 0.0, 0.06, 0.03, 0.06, 0.0, 0.03, 0.06, 0.03, 0.0, 0.06, 0.03, 0.06,
                                     0.0, 0.06, 0.03, 0.06, 0.0, 0.03, 0.06, 0.03, 0.0]

    outgoing_count_distr = result.query('user == "iGyXetHE3S8u"').outgoing_count_distr.tolist()
    incoming_count_distr = result.query('user == "iGyXetHE3S8u"').incoming_count_distr.tolist()
    
    assert len(result) > 0, "The result should not be empty."
    assert np.allclose(outgoing_count_distr, expected_outgoing_count_distr, atol=1e-2), "Incorrect distribution for outgoing_count"
    assert np.allclose(incoming_count_distr, expected_incoming_count_distr, atol=1e-2), "Incorrect distribution for incoming_count"