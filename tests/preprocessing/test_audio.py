import os

import numpy as np
import pandas as pd
import numpy as np

import niimpy
import niimpy.preprocessing.audio as audio
from niimpy.config import config

# read sample data
data = niimpy.read_csv(config.MULTIUSER_AWARE_AUDIO_PATH, tz='Europe/Helsinki')

def test_audio_features():
    
    test = audio.extract_features_audio(data, features=None)
    
    assert test.loc["jd9INuQ5BBlW", :]["audio_count_silent"].sum() == 0
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["audio_count_silent"] == 0
    assert test.loc["jd9INuQ5BBlW", :]["audio_count_loud"].sum() == 12
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 10:30:00", tz='Europe/Helsinki')]["audio_min_freq"] == 9601
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 10:30:00", tz='Europe/Helsinki')]["audio_max_freq"] == 9601
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 10:30:00", tz='Europe/Helsinki')]["audio_mean_freq"] == 9601
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 10:30:00", tz='Europe/Helsinki')]["audio_median_freq"] == 9601
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_min_db"] == 75
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_max_db"] == 75
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_mean_db"] == 75
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_median_db"] == 75
    
    
    assert test.loc["iGyXetHE3S8u", :]["audio_count_silent"].sum() == 3
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_count_silent"] == 2
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 15:30:00", tz='Europe/Helsinki')]["audio_count_speech"] == 1
    assert test.loc["iGyXetHE3S8u", :]["audio_count_loud"].sum() == 10
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_min_freq"] == 2914
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_max_freq"] == 7195
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_mean_freq"] == 5054.5
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_median_freq"] == 5054.5
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_std_freq"] < 3028
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_min_db"] == 44
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_max_db"] == 49
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_mean_db"] == 46.5
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_median_db"] == 46.5
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_std_db"] < 3.54
    
    features ={"audio_count_silent":{"audio_column_name":"is_silent","resample_args":{"rule":"1D"}},
               "audio_count_speech":{"audio_column_name":"is_silent","audio_freq_name":"double_frequency","resample_args":{"rule":"1D"}},
               "audio_count_loud":{"audio_column_name":"double_decibels","resample_args":{"rule":"1D"}}}
    test = audio.extract_features_audio(data, features=features)
    
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_count_silent"] == 0
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_count_silent"] == 3
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_count_speech"] == 1
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_count_loud"] == 12
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_count_loud"] == 10
    
    features ={"audio_min_freq":{"audio_column_name":"double_frequency","resample_args":{"rule":"2H"}},
               "audio_max_freq":{"audio_column_name":"double_frequency","resample_args":{"rule":"2H"}},
               "audio_mean_freq":{"audio_column_name":"double_frequency","resample_args":{"rule":"2H"}},
               "audio_median_freq":{"audio_column_name":"double_frequency","resample_args":{"rule":"3H"}},
               "audio_std_freq":{"audio_column_name":"double_frequency","resample_args":{"rule":"3H"}}}
    test = audio.extract_features_audio(data, features=features)
    
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_min_freq"] == 4138
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_max_freq"] == 13308
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_mean_freq"] == 8229.75
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_median_freq"] == 7736.5
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_std_freq"] < 3876
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 14:00:00", tz='Europe/Helsinki')]["audio_min_freq"] == 91
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 14:00:00", tz='Europe/Helsinki')]["audio_max_freq"] == 7195
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 14:00:00", tz='Europe/Helsinki')]["audio_mean_freq"] == 4336.5
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_median_freq"] == 3853
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_std_freq"] < 3081
    
    features ={"audio_min_db":{"audio_column_name":"double_decibels","resample_args":{"rule":"1D"}},
               "audio_max_db":{"audio_column_name":"double_decibels","resample_args":{"rule":"1D"}},
               "audio_mean_db":{"audio_column_name":"double_decibels","resample_args":{"rule":"1D"}},
               "audio_median_db":{"audio_column_name":"double_decibels","resample_args":{"rule":"1D"}},
               "audio_std_db":{"audio_column_name":"double_decibels","resample_args":{"rule":"1D"}}}
    test = audio.extract_features_audio(data, features=features)
    
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_min_db"] == 52
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_max_db"] == 99
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_mean_db"] == 79.125
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_median_db"] == 79
    assert test.loc["jd9INuQ5BBlW", pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_std_db"] < 14.8
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_min_db"] == 36
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_max_db"] == 104
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_mean_db"] == 73
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_median_db"] == 76
    assert test.loc["iGyXetHE3S8u", pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_std_db"] < 21.8