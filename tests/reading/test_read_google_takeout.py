import pandas as pd
import numpy as np
import pytest
import os
import tempfile
import zipfile

import niimpy
from niimpy import config


def create_zip(zip_filename):
    """ Compress the google takeout folder into a zip file"""
    test_zip = zipfile.ZipFile(zip_filename, mode="w")

    for dirpath,dirs,files in os.walk(config.GOOGLE_TAKEOUT_DIR):
        for f in files:
            filename = os.path.join(dirpath, f)
            filename_in_zip = filename.replace(config.GOOGLE_TAKEOUT_DIR, "")
            test_zip.write(filename, filename_in_zip)

    test_zip.close()


@pytest.fixture
def zipped_data():
    with tempfile.TemporaryDirectory() as ddir:
        zip_filename = os.path.join(ddir, "test.zip")
        create_zip(zip_filename)
        yield zip_filename


def test_read_location(zipped_data):
    """test reading location data form a Google takeout file."""
    data = niimpy.reading.google_takeout.location_history(zipped_data)
    
    assert data['latitude'][0] == 35.9974880
    assert data['longitude'][0] == -78.9221943
    assert data['source'][0] == "WIFI"
    assert data['accuracy'][0] == 25
    assert data['device'][0] == -577680260
    assert data.index[0] == pd.to_datetime("2016-08-12T19:29:43.821Z")
    
    assert len(data[data["source"] == "GPS"]) == 2

    assert data['activity_type'][1] == "STILL"
    assert data['activity_inference_confidence'][1] == 62


def test_read_activity(zipped_data):
    """test reading activity data form a Google takeout file."""
    data = niimpy.reading.google_takeout.activity(zipped_data).sort_index()
    
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


def test_read_email_activity(zipped_data):
    data = niimpy.reading.google_takeout.email_activity(zipped_data)

    assert data.index[0] == pd.to_datetime("2023-12-15 12:19:43+00:00")
    assert data.index[1] == pd.to_datetime("2023-12-15 12:29:43+00:00")
    assert data.index[2] == pd.to_datetime("2023-12-15 12:39:43+00:00")

    assert pd.isnull(data.iloc[0]["received"])
    assert pd.isnull(data.iloc[1]["received"])
    assert data.iloc[2]["received"] == pd.to_datetime("2023-12-15 12:19:43+00:00")

    assert pd.isnull(data.iloc[0]["in_reply_to"])
    assert pd.isnull(data.iloc[1]["in_reply_to"])
    assert data.iloc[2]["in_reply_to"] == data.iloc[0]["message_id"]

    assert pd.isnull(data.iloc[0]["from"]) == 0
    assert pd.isnull(data.iloc[1]["from"]) == 0
    assert data.iloc[2]["from"] == data.iloc[1]["to"][0]
    assert data.iloc[2]["cc"] == data.iloc[2]["bcc"]
    assert data.iloc[0]["to"][0] == data.iloc[1]["to"][1]


