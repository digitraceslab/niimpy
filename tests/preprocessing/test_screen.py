import os

import numpy as np
import pandas as pd
import numpy as np

import niimpy
import niimpy.preprocessing.screen as sc
from niimpy.config import config

# read sample data
data = niimpy.read_csv(config.MULTIUSER_AWARE_SCREEN_PATH, tz='Europe/Helsinki')
bat = niimpy.read_csv(config.MULTIUSER_AWARE_BATTERY_PATH, tz='Europe/Helsinki')

def test_audio_features():
    
    test = sc.extract_features_screen(data, bat, features=None)
    time = pd.Timestamp("2020-01-09 02:30:00", tz='Europe/Helsinki')
    
    assert test.loc["jd9INuQ5BBlW", time]["screen_on_count"] == 4
    assert test.loc["jd9INuQ5BBlW", time]["screen_off_count"] == 5
    assert test.loc["jd9INuQ5BBlW", time]["screen_use_count"] == 2
    assert test.loc["jd9INuQ5BBlW", time]["screen_on_durationtotal"] < 37
    assert test.loc["jd9INuQ5BBlW", time]["screen_on_durationminimum"] < 4
    assert test.loc["jd9INuQ5BBlW", time]["screen_on_durationmaximum"] < 13
    assert test.loc["jd9INuQ5BBlW", time]["screen_on_durationmean"] < 9.5
    assert test.loc["jd9INuQ5BBlW", time]["screen_on_durationmedian"] < 10.5
    assert test.loc["jd9INuQ5BBlW", time]["screen_on_durationstd"] < 3.8
    assert test.loc["jd9INuQ5BBlW", time]["screen_off_durationtotal"] < 1204
    assert test.loc["jd9INuQ5BBlW", time]["screen_off_durationminimum"] < 0.01
    assert test.loc["jd9INuQ5BBlW", time]["screen_off_durationmaximum"] < 1204
    assert test.loc["jd9INuQ5BBlW", time]["screen_off_durationmean"] < 241
    assert test.loc["jd9INuQ5BBlW", time]["screen_off_durationmedian"] < 0.01
    assert test.loc["jd9INuQ5BBlW", time]["screen_off_durationstd"] < 539
    assert test.loc["jd9INuQ5BBlW", time]["screen_use_durationtotal"] < 93.5
    assert test.loc["jd9INuQ5BBlW", time]["screen_use_durationminimum"] < 39
    assert test.loc["jd9INuQ5BBlW", time]["screen_use_durationmaximum"] < 54.5
    assert test.loc["jd9INuQ5BBlW", time]["screen_use_durationmean"] < 47
    assert test.loc["jd9INuQ5BBlW", time]["screen_use_durationmedian"] < 47
    assert test.loc["jd9INuQ5BBlW", time]["screen_use_durationstd"] < 11
    
    time = pd.Timestamp("2019-08-08 22:30:00", tz='Europe/Helsinki')
    
    assert test.loc["iGyXetHE3S8u", time]["screen_on_count"] == 4
    assert test.loc["iGyXetHE3S8u", time]["screen_off_count"] == 4
    assert test.loc["iGyXetHE3S8u", time]["screen_use_count"] == 4
    assert test.loc["iGyXetHE3S8u", time]["screen_on_durationtotal"] < 83.5
    assert test.loc["iGyXetHE3S8u", time]["screen_on_durationminimum"] < 3
    assert test.loc["iGyXetHE3S8u", time]["screen_on_durationmaximum"] < 70
    assert test.loc["iGyXetHE3S8u", time]["screen_on_durationmean"] < 21
    assert test.loc["iGyXetHE3S8u", time]["screen_on_durationmedian"] < 5.5
    assert test.loc["iGyXetHE3S8u", time]["screen_on_durationstd"] < 33
    assert test.loc["iGyXetHE3S8u", time]["screen_off_durationtotal"] < 32150
    assert test.loc["iGyXetHE3S8u", time]["screen_off_durationminimum"] < 9.5
    assert test.loc["iGyXetHE3S8u", time]["screen_off_durationmaximum"] < 31450
    assert test.loc["iGyXetHE3S8u", time]["screen_off_durationmean"] < 8035
    assert test.loc["iGyXetHE3S8u", time]["screen_off_durationmedian"] < 340
    assert test.loc["iGyXetHE3S8u", time]["screen_off_durationstd"] < 15610
    assert test.loc["iGyXetHE3S8u", time]["screen_use_durationtotal"] < 0.8
    assert test.loc["iGyXetHE3S8u", time]["screen_use_durationminimum"] < 0.15
    assert test.loc["iGyXetHE3S8u", time]["screen_use_durationmaximum"] < 0.3
    assert test.loc["iGyXetHE3S8u", time]["screen_use_durationmean"] < 0.2
    assert test.loc["iGyXetHE3S8u", time]["screen_use_durationmedian"] < 0.2
    assert test.loc["iGyXetHE3S8u", time]["screen_use_durationstd"] < 0.1
    
    
    features ={"screen_count":{"screen_column_name":"screen_status","resample_args":{"rule":"1D"}},
               "screen_duration":{"screen_column_name":"screen_status","resample_args":{"rule":"1D"}},
               "screen_first_unlock":{"screen_column_name":"screen_status","resample_args":{"rule":"1D"}}}
    test = sc.extract_features_screen(data, bat, features=features)
    
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["screen_on_count"] == 45
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["screen_off_count"] == 45
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-08", tz='Europe/Helsinki')]["screen_use_count"] == 6
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-31", tz='Europe/Helsinki')]["screen_on_durationtotal"] < 0.25
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-31", tz='Europe/Helsinki')]["screen_off_durationtotal"] < 446000
    
    features ={"screen_duration_min":{"screen_column_name":"screen_status","resample_args":{"rule":"12H"}},
               "screen_duration_max":{"screen_column_name":"screen_status","resample_args":{"rule":"12H"}},
               "screen_duration_mean":{"screen_column_name":"screen_status","resample_args":{"rule":"12H"}},
               "screen_duration_median":{"screen_column_name":"screen_status","resample_args":{"rule":"6H"}},
               "screen_duration_std":{"screen_column_name":"screen_status","resample_args":{"rule":"6H"}}}
    test = sc.extract_features_screen(data, bat, features=features)
    
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 12:00:00", tz='Europe/Helsinki')]["screen_on_durationminimum"] < 2.5
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 12:00:00", tz='Europe/Helsinki')]["screen_use_durationmaximum"] < 290
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-15 12:00:00", tz='Europe/Helsinki')]["screen_on_durationmedian"] < 18.5
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-15 12:00:00", tz='Europe/Helsinki')]["screen_use_durationmedian"] < 0.35
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-15 12:00:00", tz='Europe/Helsinki')]["screen_off_durationmaximum"] < 182350