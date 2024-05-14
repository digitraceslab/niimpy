import pandas as pd
import numpy as np
import pytest
import os
import tempfile
import zipfile

import niimpy
from niimpy import config


@pytest.fixture
def empty_zip_file():
    with tempfile.TemporaryDirectory() as ddir:
        zip_filename = os.path.join(ddir, "test.zip")
        zipfile.ZipFile(zip_filename, mode="w").close()
        yield zip_filename


def test_read_location(google_takeout_zipped):
    """test reading location data from a Google takeout file."""
    data = niimpy.reading.google_takeout.location_history(google_takeout_zipped)

    assert data.shape == (7, 20)
    
    assert data['latitude']["2016-08-12T19:29:43.821Z"] == 35.9974880
    assert data['longitude']["2016-08-12T19:29:43.821Z"] == -78.9221943
    assert data['source']["2016-08-12T19:29:43.821Z"] == "WIFI"
    assert data['accuracy']["2016-08-12T19:29:43.821Z"] == 25
    assert data['device']["2016-08-12T19:29:43.821Z"] == -577680260
    assert data.index[0] == pd.to_datetime("2016-08-12T19:29:43.821Z")
    
    assert len(data[data["source"] == "GPS"]) == 2

    assert data['activity_type']["2016-08-12T19:30:49.531Z"] == "STILL"
    assert data['activity_inference_confidence']["2016-08-12T19:30:49.531Z"] == 62


def test_read_location_start_date(google_takeout_zipped):
    """test reading location data from a Google takeout file."""
    data = niimpy.reading.google_takeout.location_history(
        google_takeout_zipped,
        start_date=pd.to_datetime("2016-08-12T19:31:00.00Z", format='ISO8601')
    )
    assert data.shape == (5, 20)


def test_read_location_end_date(google_takeout_zipped):
    """test reading location data from a Google takeout file."""
    data = niimpy.reading.google_takeout.location_history(
        google_takeout_zipped,
        end_date=pd.to_datetime("2016-08-12T21:16:34.00Z", format='ISO8601')
    )
    assert data.shape == (5, 20)


def test_read_location_activity_threshold(google_takeout_zipped):
    """test reading location data from a Google takeout file."""
    data = niimpy.reading.google_takeout.location_history(
        google_takeout_zipped,
        inferred_activity = "threshold",
    )

    assert data.index[0] == pd.to_datetime("2016-08-12T19:30:49.531Z")
    assert data['latitude']["2016-08-12T19:30:49.531Z"].iloc[0] == 35.9975588
    assert data['longitude']["2016-08-12T19:30:49.531Z"].iloc[0] == -78.9225036
    
    assert len(data[data["source"] == "GPS"]) == 0

    assert data['activity_type']["2016-08-12T19:30:49.531Z"].iloc[0] == "STILL"
    assert data['activity_inference_confidence']["2016-08-12T19:30:49.531Z"].iloc[0] == 62
    assert data['activity_type']["2016-08-12T19:30:49.531Z"].iloc[1] == "IN_VEHICLE"
    assert data['activity_inference_confidence']["2016-08-12T19:30:49.531Z"].iloc[1] == 31
    assert data['activity_type']["2016-08-12T19:30:49.531Z"].iloc[2] == "UNKNOWN"
    assert data['activity_inference_confidence']["2016-08-12T19:30:49.531Z"].iloc[2] == 8


def test_read_location_no_location_data(empty_zip_file):
    """test reading location data not present in file. """
    data = niimpy.reading.google_takeout.location_history(empty_zip_file)
    assert data.empty


def test_read_activity(google_takeout_zipped):
    """test reading activity data from a Google takeout file."""
    data = niimpy.reading.google_takeout.activity(google_takeout_zipped).sort_index()

    assert data.shape == (192, 21)
    
    assert data.index[0] == pd.to_datetime("2023-11-20 00:00:000+02:00")
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


def test_read_activity_no_activity_data(empty_zip_file):
    """ test reading activity data not present in file. """
    data = niimpy.reading.google_takeout.activity(empty_zip_file)
    assert data.empty


def test_read_activity_start_date(google_takeout_zipped):
    """test reading location data from a Google takeout file."""
    data = niimpy.reading.google_takeout.activity(
        google_takeout_zipped,
        start_date=pd.to_datetime("2023-11-21T00:00:00.000Z", format="ISO8601")
    )
    assert data.shape == (96, 19)


def test_read_activity_end_date(google_takeout_zipped):
    """test reading location data from a Google takeout file."""
    data = niimpy.reading.google_takeout.activity(
        google_takeout_zipped,
        end_date=pd.to_datetime("2023-11-20T00:00:00.000Z", format="ISO8601")
    )
    assert data.shape == (96, 21)


def test_read_email_activity(google_takeout_zipped, request):
    sentiment = request.config.getoption("--run_sentiment")
    with pytest.warns(UserWarning):
        data = niimpy.reading.google_takeout.email_activity(
            google_takeout_zipped, sentiment=sentiment, sentiment_batch_size = 2
        )

    if sentiment:
        assert data.shape == (5, 13)
    else:
        assert data.shape == (5, 11)

    assert data.index[0] == pd.to_datetime("2023-12-15 12:19:43+00:00")
    assert data.index[1] == pd.to_datetime("2023-12-15 12:29:43+00:00")
    assert data.index[3] == pd.to_datetime("2023-12-15 12:39:43+00:00")

    assert pd.isnull(data.iloc[0]["received"])
    assert pd.isnull(data.iloc[1]["received"])
    assert data.iloc[3]["received"] == pd.to_datetime("2023-12-15 12:19:43+00:00")

    assert pd.isnull(data.iloc[0]["in_reply_to"])
    assert pd.isnull(data.iloc[1]["in_reply_to"])
    assert data.iloc[3]["in_reply_to"] == data.iloc[0]["message_id"]

    assert pd.isnull(data.iloc[0]["from"]) == 0
    assert pd.isnull(data.iloc[1]["from"]) == 0
    assert data.iloc[3]["from"] == data.iloc[1]["to"][0]
    assert data.iloc[3]["cc"] == data.iloc[3]["bcc"]
    assert data.iloc[0]["to"][0] == data.iloc[1]["to"][1]

    assert data.iloc[0]["word_count"] == 6
    assert data.iloc[0]["character_count"] == 33

    if sentiment:
        assert data.iloc[0]["sentiment"] == "positive"
        assert data.iloc[1]["sentiment"] == "negative"
        assert data.iloc[2]["sentiment"] == "negative"
        assert data.iloc[3]["sentiment"] == "positive"


def test_read_email_activity_mbox_file(request):
    sentiment = request.config.getoption("--run_sentiment")
    path = os.path.join(config.GOOGLE_TAKEOUT_DIR, "Takeout", "Mail", "All mail Including Spam and Trash.mbox")
    with pytest.warns(UserWarning):
        data = niimpy.reading.google_takeout.email_activity(
            path, sentiment=sentiment, sentiment_batch_size = 2
        )

    if sentiment:
        assert data.shape == (5, 13)
    else:
        assert data.shape == (5, 11)

    assert data.index[0] == pd.to_datetime("2023-12-15 12:19:43+00:00")
    assert data.index[1] == pd.to_datetime("2023-12-15 12:29:43+00:00")
    assert data.index[3] == pd.to_datetime("2023-12-15 12:39:43+00:00")
    
    assert pd.isnull(data.iloc[0]["received"])
    assert pd.isnull(data.iloc[1]["received"])
    assert data.iloc[3]["received"] == pd.to_datetime("2023-12-15 12:19:43+00:00")

    assert pd.isnull(data.iloc[0]["in_reply_to"])
    assert pd.isnull(data.iloc[1]["in_reply_to"])
    assert data.iloc[3]["in_reply_to"] == data.iloc[0]["message_id"]

    assert pd.isnull(data.iloc[0]["from"]) == 0
    assert pd.isnull(data.iloc[1]["from"]) == 0
    assert data.iloc[3]["from"] == data.iloc[1]["to"][0]
    assert data.iloc[3]["cc"] == data.iloc[3]["bcc"]
    assert data.iloc[0]["to"][0] == data.iloc[1]["to"][1]

    assert data.iloc[0]["word_count"] == 6
    assert data.iloc[0]["character_count"] == 33

    if sentiment:
        assert data.iloc[0]["sentiment"] == "positive"
        assert data.iloc[1]["sentiment"] == "negative"
        assert data.iloc[2]["sentiment"] == "negative"
        assert data.iloc[3]["sentiment"] == "positive"


def test_read_email_activity_no_email_data(empty_zip_file):
    """test reading email activity data not present in file. """
    data = niimpy.reading.google_takeout.email_activity(empty_zip_file)
    assert data.empty


def test_read_email_activity_start_date(google_takeout_zipped, request):
    sentiment = request.config.getoption("--run_sentiment")
    with pytest.warns(UserWarning):
        data = niimpy.reading.google_takeout.email_activity(
            google_takeout_zipped, sentiment=sentiment, sentiment_batch_size = 2,
            start_date = pd.to_datetime("2023-12-15 12:20:00+00:00"),
        )

    if sentiment:
        assert data.shape == (4, 13)
    else:
        assert data.shape == (4, 11)


def test_read_email_activity_end_date(google_takeout_zipped, request):
    sentiment = request.config.getoption("--run_sentiment")
    with pytest.warns(UserWarning):
        data = niimpy.reading.google_takeout.email_activity(
            google_takeout_zipped, sentiment=sentiment, sentiment_batch_size = 2,
            end_date = pd.to_datetime("2023-12-15 12:20:00+00:00"),
        )

    if sentiment:
        assert data.shape == (1, 13)
    else:
        assert data.shape == (1, 11)


def test_read_email_unknown_file():
    with pytest.raises(ValueError):
        niimpy.reading.google_takeout.email_activity("unknown_file")


def test_read_chat(google_takeout_zipped, request):
    sentiment = request.config.getoption("--run_sentiment")
    with pytest.warns(UserWarning):
        data = niimpy.reading.google_takeout.chat(
            google_takeout_zipped,
            sentiment=sentiment,
            sentiment_batch_size = 2
        )

    if sentiment:
        assert data.shape == (4, 12)
    else:
        assert data.shape == (4, 10)

    assert data.index[0] == pd.to_datetime("2024-01-30 13:27:33+00:00")
    assert data.index[1] == pd.to_datetime("2024-01-30 13:29:10+00:00")
    assert data.index[2] == pd.to_datetime("2024-01-30 13:29:17+00:00")
    assert data.index[3] == pd.to_datetime("2024-01-30 13:29:17+00:00")

    assert data.iloc[0]["creator_name"] == 0
    assert data.iloc[1]["creator_name"] == data.iloc[2]["creator_name"]
    assert data.iloc[3]["creator_name"] == 0

    assert data.iloc[0]["creator_email"] == 0
    assert data.iloc[1]["creator_email"] == data.iloc[2]["creator_email"]
    assert data.iloc[3]["creator_email"] == 0

    assert data.iloc[0]["creator_user_type"] == "Human"
    assert data.iloc[1]["creator_user_type"] == "Human"
    assert data.iloc[2]["creator_user_type"] == "Human"
    assert data.iloc[3]["creator_user_type"] == "Human"

    assert data.iloc[0]["word_count"] == 1
    assert data.iloc[1]["word_count"] == 1
    assert data.iloc[2]["word_count"] == 3
    assert data.iloc[3]["word_count"] == 5

    assert data.iloc[0]["character_count"] == 5
    assert data.iloc[1]["character_count"] == 5
    assert data.iloc[2]["character_count"] == 11
    assert data.iloc[3]["character_count"] == 22

    if sentiment:
        assert data.iloc[0]["sentiment"] == 'none'
        assert data.iloc[1]["sentiment"] == 'none'
        assert data.iloc[2]["sentiment"] == 'positive'
        assert data.iloc[3]["sentiment"] == 'positive'

    assert data.iloc[0]["chat_group"] == 0


def test_read_chat_no_chat_data(empty_zip_file):
    data = niimpy.reading.google_takeout.chat(empty_zip_file)
    assert data.empty


def test_read_chat_start_date(google_takeout_zipped, request):
    sentiment = request.config.getoption("--run_sentiment")
    with pytest.warns(UserWarning):
        data = niimpy.reading.google_takeout.chat(
            google_takeout_zipped,
            sentiment=sentiment,
            sentiment_batch_size = 2,
            start_date = pd.to_datetime("2024-01-30 13:29:00+00:00"),
        )

    if sentiment:
        assert data.shape == (3, 12)
    else:
        assert data.shape == (3, 10)


def test_read_chat_end_date(google_takeout_zipped, request):
    sentiment = request.config.getoption("--run_sentiment")
    with pytest.warns(UserWarning):
        data = niimpy.reading.google_takeout.chat(
            google_takeout_zipped,
            sentiment=sentiment,
            sentiment_batch_size = 2,
            end_date = pd.to_datetime("2024-01-30 13:29:00+00:00"),
        )

    if sentiment:
        assert data.shape == (1, 12)
    else:
        assert data.shape == (1, 10)


def test_read_youtube_watch_history(google_takeout_zipped):
    data = niimpy.reading.google_takeout.youtube_watch_history(google_takeout_zipped)

    assert data.shape == (4, 3)

    assert data.index[0] == pd.to_datetime("2024-02-13 06:36:49+00:00")
    assert data.index[1] == pd.to_datetime("2024-02-13 06:36:05+00:00")
    assert data.index[2] == pd.to_datetime("2024-02-13 06:35:38+00:00")
    assert data.index[3] == pd.to_datetime("2024-02-13 06:35:03+00:00")

    assert data.iloc[0]["video_title"] != data.iloc[1]["video_title"]
    assert data.iloc[0]["channel_title"] != data.iloc[1]["channel_title"]
    assert data.iloc[0]["video_title"] != data.iloc[2]["video_title"]
    assert data.iloc[0]["channel_title"] != data.iloc[2]["channel_title"]
    assert data.iloc[0]["video_title"] == data.iloc[3]["video_title"]
    assert data.iloc[0]["channel_title"] == data.iloc[3]["channel_title"]


def test_read_youtube_watch_history_no_youtube_data(empty_zip_file):
    data = niimpy.reading.google_takeout.youtube_watch_history(empty_zip_file)
    assert data.empty


def test_read_youtube_watch_history_start_date(google_takeout_zipped):
    data = niimpy.reading.google_takeout.youtube_watch_history(
        google_takeout_zipped,
        start_date = pd.to_datetime("2024-02-13 06:36:00+00:00"),
    )
    assert data.shape == (2, 3)

def test_read_youtube_watch_history_end_date(google_takeout_zipped):
    data = niimpy.reading.google_takeout.youtube_watch_history(
        google_takeout_zipped,
        end_date = pd.to_datetime("2024-02-13 06:36:00+00:00"),
    )
    assert data.shape == (2, 3)
