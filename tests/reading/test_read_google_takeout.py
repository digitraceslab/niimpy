import pandas as pd
import numpy as np
import pytest
import datetime

import niimpy
from niimpy import config


def test_read_google_takeout_location():
    """test reading location data form a Google takeout file."""
    data = niimpy.reading.google_takeout.location_history(config.GOOGLE_TAKEOUT_PATH)
    
    assert data['latitude'][0] == 35.9974880
    assert data['longitude'][0] == -78.9221943
    assert data['source'][0] == "WIFI"
    assert data['accuracy'][0] == 25
    assert data['device'][0] == -577680260
    assert data.index[0] == pd.to_datetime("2016-08-12T19:29:43.821Z")
    
    assert len(data[data["source"] == "GPS"]) == 2

    assert data['activity_type'][1] == "STILL"
    assert data['activity_inference_confidence'][1] == 62


def test_read_google_takeout_activity():
    """test reading activity data form a Google takeout file."""
    data = niimpy.reading.google_takeout.activity(config.GOOGLE_TAKEOUT_PATH)
    
    assert data.index[0] == pd.to_datetime("2023-11-20 00:00:00+0200")
    assert np.isnan(data.iloc[4]["move_minutes_count"])
    assert data.iloc[75]["move_minutes_count"] == 13.0
    assert data.iloc[75]["calories_(kcal)"] == pytest.approx(43.42468) 
    assert data.iloc[75]["distance_(m)"] == pytest.approx(1174.961861)
    assert data.iloc[75]["heart_points"] == 17.0
    assert data.iloc[75]["heart_minutes"] == 11.0
    assert np.isnan(data.iloc[75]["low_latitude_(deg)"])
    assert np.isnan(data.iloc[75]["low_longitude_(deg)"])
    assert np.isnan(data.iloc[75]["high_latitude_(deg)"])
    assert np.isnan(data.iloc[75]["high_longitude_(deg)"])
    assert data.iloc[75]["average_speed_(m/s)"] == pytest.approx(1.539091)
    assert data.iloc[75]["max_speed_(m/s)"] == pytest.approx(2.123024)
    assert data.iloc[75]["min_speed_(m/s)"] == pytest.approx(0.3197519)
    assert data.iloc[75]["step_count"] == 1537.0
    assert np.isnan(data.iloc[75]["average_weight_(kg)"])
    assert np.isnan(data.iloc[75]["max_weight_(kg)"])
    assert np.isnan(data.iloc[75]["min_weight_(kg)"])
    assert pd.isnull(data.iloc[75]["road_biking_duration"])
    assert data.iloc[75]["start_time"] == pd.to_datetime("2023-11-20 18:45:00+02:00")
    assert data.iloc[75]["end_time"] == pd.to_datetime("2023-11-20 19:00:00+02:00")
    assert data.iloc[75]["walking_duration"] == pd.to_timedelta("0 days 00:00:00.337365")

