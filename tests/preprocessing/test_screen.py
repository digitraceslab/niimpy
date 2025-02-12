import pandas as pd

import niimpy
import niimpy.preprocessing.screen as sc
from niimpy import config

# read sample data
data = niimpy.read_csv(config.MULTIUSER_AWARE_SCREEN_PATH, tz='Europe/Helsinki')
bat = niimpy.read_csv(config.MULTIUSER_AWARE_BATTERY_PATH, tz='Europe/Helsinki')
data["group"] = "group1"
bat["group"] = "group1"

def test_audio_features():
    
    data["extra_column"] = "extra"
    test = sc.extract_features_screen(data, bat, features=None)
    assert "extra_column" not in test.columns

    time = pd.Timestamp("2020-01-09 02:30:00", tz='Europe/Helsinki')
    
    test_user = test[test["user"] == "jd9INuQ5BBlW"]

    assert test_user.loc[time]["screen_on_count"] == 4
    assert test_user.loc[time]["screen_off_count"] == 5
    assert test_user.loc[time]["screen_use_count"] == 2
    assert test_user.loc[time]["screen_on_durationtotal"] < 37
    assert test_user.loc[time]["screen_on_durationminimum"] < 4
    assert test_user.loc[time]["screen_on_durationmaximum"] < 13
    assert test_user.loc[time]["screen_on_durationmean"] < 9.5
    assert test_user.loc[time]["screen_on_durationmedian"] < 10.5
    assert test_user.loc[time]["screen_on_durationstd"] < 3.8
    assert test_user.loc[time]["screen_off_durationtotal"] < 1204
    assert test_user.loc[time]["screen_off_durationminimum"] < 0.01
    assert test_user.loc[time]["screen_off_durationmaximum"] < 1204
    assert test_user.loc[time]["screen_off_durationmean"] < 241
    assert test_user.loc[time]["screen_off_durationmedian"] < 0.01
    assert test_user.loc[time]["screen_off_durationstd"] < 539
    assert test_user.loc[time]["screen_use_durationtotal"] < 93.5
    assert test_user.loc[time]["screen_use_durationminimum"] < 39
    assert test_user.loc[time]["screen_use_durationmaximum"] < 54.5
    assert test_user.loc[time]["screen_use_durationmean"] < 47
    assert test_user.loc[time]["screen_use_durationmedian"] < 47
    assert test_user.loc[time]["screen_use_durationstd"] < 11
    assert test_user.loc[time]["group"] == "group1"
    
    time = pd.Timestamp("2019-08-08 22:30:00", tz='Europe/Helsinki')
    
    test_user2 = test[test["user"] == "iGyXetHE3S8u"]
    assert test_user2.loc[time]["screen_on_count"] == 4
    assert test_user2.loc[time]["screen_off_count"] == 4
    assert test_user2.loc[time]["screen_use_count"] == 4
    assert test_user2.loc[time]["screen_on_durationtotal"] < 83.5
    assert test_user2.loc[time]["screen_on_durationminimum"] < 3
    assert test_user2.loc[time]["screen_on_durationmaximum"] < 70
    assert test_user2.loc[time]["screen_on_durationmean"] < 21
    assert test_user2.loc[time]["screen_on_durationmedian"] < 5.5
    assert test_user2.loc[time]["screen_on_durationstd"] < 33
    assert test_user2.loc[time]["screen_off_durationtotal"] < 32150
    assert test_user2.loc[time]["screen_off_durationminimum"] < 9.5
    assert test_user2.loc[time]["screen_off_durationmaximum"] < 31450
    assert test_user2.loc[time]["screen_off_durationmean"] < 8035
    assert test_user2.loc[time]["screen_off_durationmedian"] < 340
    assert test_user2.loc[time]["screen_off_durationstd"] < 15610
    assert test_user2.loc[time]["screen_use_durationtotal"] < 0.8
    assert test_user2.loc[time]["screen_use_durationminimum"] < 0.15
    assert test_user2.loc[time]["screen_use_durationmaximum"] < 0.3
    assert test_user2.loc[time]["screen_use_durationmean"] < 0.2
    assert test_user2.loc[time]["screen_use_durationmedian"] < 0.2
    assert test_user2.loc[time]["screen_use_durationstd"] < 0.1
    assert test_user2.loc[time]["group"] == "group1"
    
    
    features ={sc.screen_count:{"screen_column_name":"screen_status","resample_args":{"rule":"1D"}},
               sc.screen_duration:{"screen_column_name":"screen_status","resample_args":{"rule":"1D"}},
               sc.screen_first_unlock:{"screen_column_name":"screen_status","resample_args":{"rule":"1D"}}}
    test = sc.extract_features_screen(data, bat, features=features)
    
    test_user = test[test["user"] == "jd9INuQ5BBlW"]
    test_user2 = test[test["user"] == "iGyXetHE3S8u"]
    assert test_user.loc[pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["screen_on_count"] == 45
    assert test_user.loc[pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["screen_off_count"] == 45
    assert test_user2.loc[pd.Timestamp("2019-08-08", tz='Europe/Helsinki')]["screen_use_count"] == 6
    assert test_user2.loc[pd.Timestamp("2019-08-31", tz='Europe/Helsinki')]["screen_on_durationtotal"] < 0.25
    assert test_user2.loc[pd.Timestamp("2019-08-31", tz='Europe/Helsinki')]["screen_off_durationtotal"] < 446000
    assert test_user2.loc[pd.Timestamp("2019-08-31", tz='Europe/Helsinki')]["group"] == "group1"
    
    features ={sc.screen_duration_min:{"screen_column_name":"screen_status","resample_args":{"rule":"12h"}},
               sc.screen_duration_max:{"screen_column_name":"screen_status","resample_args":{"rule":"12h"}},
               sc.screen_duration_mean:{"screen_column_name":"screen_status","resample_args":{"rule":"12h"}},
               sc.screen_duration_median:{"screen_column_name":"screen_status","resample_args":{"rule":"6h"}},
               sc.screen_duration_std:{"screen_column_name":"screen_status","resample_args":{"rule":"6h"}}}
    test = sc.extract_features_screen(data, bat, features=features)
    
    test_user = test[test["user"] == "jd9INuQ5BBlW"]
    test_user2 = test[test["user"] == "iGyXetHE3S8u"]
    assert test_user.loc[pd.Timestamp("2020-01-09 12:00:00", tz='Europe/Helsinki')]["screen_on_durationminimum"] < 2.5
    assert test_user.loc[pd.Timestamp("2020-01-09 12:00:00", tz='Europe/Helsinki')]["screen_use_durationmaximum"] < 290
    assert test_user2.loc[pd.Timestamp("2019-08-15 12:00:00", tz='Europe/Helsinki')]["screen_on_durationmedian"] < 18.5
    assert test_user2.loc[pd.Timestamp("2019-08-15 12:00:00", tz='Europe/Helsinki')]["screen_use_durationmedian"] < 0.35
    assert test_user2.loc[pd.Timestamp("2019-08-15 12:00:00", tz='Europe/Helsinki')]["screen_off_durationmaximum"] < 182350
    assert test_user2.loc[pd.Timestamp("2019-08-15 12:00:00", tz='Europe/Helsinki')]["group"] == "group1"
