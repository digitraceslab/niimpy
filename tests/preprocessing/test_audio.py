import pandas as pd

import niimpy
import niimpy.preprocessing.audio as audio
from niimpy import config

# read sample data
data = niimpy.read_csv(config.MULTIUSER_AWARE_AUDIO_PATH, tz='Europe/Helsinki')
data = data.rename(columns={"double_frequency": "frequency", "double_decibels": "decibels"})

def test_audio_features():
    data["group"] = "group1"
    data["extra_column"] = "extra"
    test = audio.extract_features_audio(data)

    assert "group" in test.columns
    assert "extra_column" not in test.columns
    
    test_user1 = test[test["user"] == "jd9INuQ5BBlW"]
    assert test_user1["audio_count_silent"].sum() == 0
    assert test_user1.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["audio_count_silent"] == 0
    assert test_user1["audio_count_loud"].sum() == 12
    assert test_user1.loc[pd.Timestamp("2020-01-09 10:30:00", tz='Europe/Helsinki')]["audio_min_freq"] == 9601
    assert test_user1.loc[pd.Timestamp("2020-01-09 10:30:00", tz='Europe/Helsinki')]["audio_max_freq"] == 9601
    assert test_user1.loc[pd.Timestamp("2020-01-09 10:30:00", tz='Europe/Helsinki')]["audio_mean_freq"] == 9601
    assert test_user1.loc[pd.Timestamp("2020-01-09 10:30:00", tz='Europe/Helsinki')]["audio_median_freq"] == 9601
    assert test_user1.loc[pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_min_db"] == 75
    assert test_user1.loc[pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_max_db"] == 75
    assert test_user1.loc[pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_mean_db"] == 75
    assert test_user1.loc[pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_median_db"] == 75
    assert test_user1.loc["2020-01-09 10:30:00"]["group"] == "group1"
    
    test_user2 = test[test["user"] == "iGyXetHE3S8u"]
    assert test_user2["audio_count_silent"].sum() == 3
    assert test_user2.loc[pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_count_silent"] == 2
    assert test_user2.loc[pd.Timestamp("2019-08-13 15:30:00", tz='Europe/Helsinki')]["audio_count_speech"] == 1
    assert test_user2["audio_count_loud"].sum() == 10
    assert test_user2.loc[pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_min_freq"] == 2914
    assert test_user2.loc[pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_max_freq"] == 7195
    assert test_user2.loc[pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_mean_freq"] == 5054.5
    assert test_user2.loc[pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_median_freq"] == 5054.5
    assert test_user2.loc[pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_std_freq"] < 3028
    assert test_user2.loc[pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_min_db"] == 44
    assert test_user2.loc[pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_max_db"] == 49
    assert test_user2.loc[pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_mean_db"] == 46.5
    assert test_user2.loc[pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_median_db"] == 46.5
    assert test_user2.loc[pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_std_db"] < 3.54
    
    features ={audio.audio_count_silent:{"audio_column_name":"is_silent","resample_args":{"rule":"1D"}},
               audio.audio_count_speech:{"audio_column_name":"is_silent","audio_freq_name":"frequency","resample_args":{"rule":"1D"}},
               audio.audio_count_loud:{"audio_column_name":"decibels","resample_args":{"rule":"1D"}}}
    test = audio.extract_features_audio(data, features=features)
    
    test_user1 = test[test["user"] == "jd9INuQ5BBlW"]
    test_user1_dev1 = test_user1[test_user1["device"] == "3p83yASkOb_B"]
    test_user1_dev2 = test_user1[test_user1["device"] == "OWd1Uau8POix"]
    test_user2 = test[test["user"] == "iGyXetHE3S8u"]
    assert test_user1_dev1.loc[pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_count_silent"] == 0
    assert test_user2.loc[pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_count_silent"] == 3
    assert test_user2.loc[pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_count_speech"] == 1
    assert test_user1_dev1.loc[pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_count_loud"] == 7
    assert test_user1_dev2.loc[pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_count_loud"] == 5
    assert test_user2.loc[pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_count_loud"] == 10
    
    features ={audio.audio_min_freq:{"audio_column_name":"frequency","resample_args":{"rule":"2h"}},
               audio.audio_max_freq:{"audio_column_name":"frequency","resample_args":{"rule":"2h"}},
               audio.audio_mean_freq:{"audio_column_name":"frequency","resample_args":{"rule":"2h"}},
               audio.audio_median_freq:{"audio_column_name":"frequency","resample_args":{"rule":"3h"}},
               audio.audio_std_freq:{"audio_column_name":"frequency","resample_args":{"rule":"3h"}}}
    test = audio.extract_features_audio(data, features=features)
    
    test_user1 = test[test["user"] == "jd9INuQ5BBlW"]
    test_user1_dev1 = test_user1[test_user1["device"] == "3p83yASkOb_B"]
    test_user2 = test[test["user"] == "iGyXetHE3S8u"]
    assert test_user1_dev1.loc[pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_min_freq"] == 4138
    assert test_user1_dev1.loc[pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_max_freq"] == 6729
    assert test_user1_dev1.loc[pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_mean_freq"] == 5433.50
    assert test_user1_dev1.loc[pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_median_freq"] == 5433.5
    assert test_user1_dev1.loc[pd.Timestamp("2020-01-09 06:00:00", tz='Europe/Helsinki')]["audio_std_freq"] < 3876
    assert test_user2.loc[pd.Timestamp("2019-08-13 14:00:00", tz='Europe/Helsinki')]["audio_min_freq"] == 91
    assert test_user2.loc[pd.Timestamp("2019-08-13 14:00:00", tz='Europe/Helsinki')]["audio_max_freq"] == 7195
    assert test_user2.loc[pd.Timestamp("2019-08-13 14:00:00", tz='Europe/Helsinki')]["audio_mean_freq"] == 4336.5
    assert test_user2.loc[pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_median_freq"] == 3853
    assert test_user2.loc[pd.Timestamp("2019-08-13 15:00:00", tz='Europe/Helsinki')]["audio_std_freq"] < 3081
    
    features ={audio.audio_min_db:{"audio_column_name":"decibels","resample_args":{"rule":"1D"}},
               audio.audio_max_db:{"audio_column_name":"decibels","resample_args":{"rule":"1D"}},
               audio.audio_mean_db:{"audio_column_name":"decibels","resample_args":{"rule":"1D"}},
               audio.audio_median_db:{"audio_column_name":"decibels","resample_args":{"rule":"1D"}},
               audio.audio_std_db:{"audio_column_name":"decibels","resample_args":{"rule":"1D"}}}
    test = audio.extract_features_audio(data, features=features)
    
    test_user1 = test[test["user"] == "jd9INuQ5BBlW"]
    test_user1_dev1 = test_user1[test_user1["device"] == "3p83yASkOb_B"]
    test_user2 = test[test["user"] == "iGyXetHE3S8u"]
    assert test_user1_dev1.loc[pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_min_db"] == 52
    assert test_user1_dev1.loc[pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_max_db"] == 99
    assert test_user1_dev1.loc[pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_mean_db"] == 75
    assert test_user1_dev1.loc[pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_median_db"] == 77.5
    assert test_user1_dev1.loc[pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["audio_std_db"] < 16
    assert test_user2.loc[pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_min_db"] == 36
    assert test_user2.loc[pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_max_db"] == 104
    assert test_user2.loc[pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_mean_db"] == 73
    assert test_user2.loc[pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_median_db"] == 76
    assert test_user2.loc[pd.Timestamp("2019-08-13", tz='Europe/Helsinki')]["audio_std_db"] < 21.8