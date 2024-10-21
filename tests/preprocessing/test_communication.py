import os
import pytest

import pandas as pd

import niimpy
import niimpy.preprocessing.communication as comms
from niimpy import config

# read sample data

def test_audio_features():
    data = niimpy.read_csv(config.MULTIUSER_AWARE_CALLS_PATH, tz='Europe/Helsinki')
    data["group"] = "group1"
    test = comms.extract_features_comms(data, features=None)
    
    test_user = test[test["user"] == "jd9INuQ5BBlW"]
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["outgoing_duration_total"] == 5270 
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["outgoing_duration_mean"] < 753
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["outgoing_duration_median"] == 851
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["outgoing_duration_std"] < 443.1
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["incoming_duration_total"] == 2976
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["incoming_duration_mean"] == 992
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["incoming_duration_median"] == 1079
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["incoming_duration_std"] < 545.8
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["missed_duration_total"] == 0
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["missed_duration_mean"] == 0
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["missed_duration_median"] == 0    
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["outgoing_incoming_ratio"] < 2.34
    test_user = test[test["user"] == "iGyXetHE3S8u"]
    assert test_user.loc[pd.Timestamp("2019-08-10 15:00:00", tz='Europe/Helsinki')]["outgoing_duration_total"] == 2726
    assert test_user.loc[pd.Timestamp("2019-08-10 15:00:00", tz='Europe/Helsinki')]["outgoing_duration_mean"] == 1363
    assert test_user.loc[pd.Timestamp("2019-08-10 15:00:00", tz='Europe/Helsinki')]["outgoing_duration_median"] == 1363
    assert test_user.loc[pd.Timestamp("2019-08-10 15:00:00", tz='Europe/Helsinki')]["outgoing_duration_std"] < 63.64
    assert test_user.loc[pd.Timestamp("2019-08-10 15:00:00", tz='Europe/Helsinki')]["incoming_duration_total"] == 1298
    assert test_user.loc[pd.Timestamp("2019-08-10 15:00:00", tz='Europe/Helsinki')]["incoming_duration_mean"] == 1298
    assert test_user.loc[pd.Timestamp("2019-08-10 15:00:00", tz='Europe/Helsinki')]["incoming_duration_median"] == 1298
    assert test_user.loc[pd.Timestamp("2019-08-10 15:00:00", tz='Europe/Helsinki')]["missed_duration_total"] == 0
    assert test_user.loc[pd.Timestamp("2019-08-10 15:00:00", tz='Europe/Helsinki')]["missed_duration_mean"] == 0
    assert test_user.loc[pd.Timestamp("2019-08-10 15:00:00", tz='Europe/Helsinki')]["missed_duration_median"] == 0
    assert test_user.loc[pd.Timestamp("2019-08-10 15:00:00", tz='Europe/Helsinki')]["missed_duration_std"] == 0
    assert test_user.loc[pd.Timestamp("2019-08-10 15:00:00", tz='Europe/Helsinki')]["outgoing_incoming_ratio"] == 2
    assert test_user.loc[pd.Timestamp("2019-08-10 15:00:00", tz='Europe/Helsinki')]["group"] == "group1"
       
    features ={comms.call_count:{"communication_column_name":"call_duration","resample_args":{"rule":"1D"}},
               comms.call_outgoing_incoming_ratio:{"communication_column_name":"call_duration","resample_args":{"rule":"1D"}}}
    test = comms.extract_features_comms(data, features=features)
    
    test_user = test[test["user"] == "jd9INuQ5BBlW"]
    assert test_user.loc[pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["missed_count"] == 1
    assert test_user.loc[pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["incoming_count"] == 7
    test_user = test[test["user"] == "iGyXetHE3S8u"]
    assert test_user.loc[pd.Timestamp("2019-08-10", tz='Europe/Helsinki')]["outgoing_count"] == 2
    assert test_user.loc[pd.Timestamp("2019-08-10", tz='Europe/Helsinki')]["outgoing_incoming_ratio"] == 2
    assert test_user.loc[pd.Timestamp("2019-08-10", tz='Europe/Helsinki')]["group"] == "group1"
    
    features ={comms.call_duration_total:{"audio_column_name":"double_frequency","resample_args":{"rule":"2h"}},
               comms.call_duration_mean:{"audio_column_name":"double_frequency","resample_args":{"rule":"2h"}},
               comms.call_duration_median:{"audio_column_name":"double_frequency","resample_args":{"rule":"2h"}},
               comms.call_duration_std:{"audio_column_name":"double_frequency","resample_args":{"rule":"3h"}}}
    test = comms.extract_features_comms(data, features=features)
    
    test_user = test[test["user"] == "jd9INuQ5BBlW"]
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["outgoing_duration_total"] == 6062
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["outgoing_duration_mean"] < 673.6
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["outgoing_duration_median"] == 778
    assert test_user.loc[pd.Timestamp("2020-01-09 03:00:00", tz='Europe/Helsinki')]["outgoing_duration_std"] == 0
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["incoming_duration_total"] == 6643
    test_user = test[test["user"] == "iGyXetHE3S8u"]
    assert test_user.loc[pd.Timestamp("2019-08-13 06:00:00", tz='Europe/Helsinki')]["incoming_duration_mean"] == 591
    assert test_user.loc[pd.Timestamp("2019-08-13 06:00:00", tz='Europe/Helsinki')]["incoming_duration_median"] == 591
    assert test_user.loc[pd.Timestamp("2019-08-13 06:00:00", tz='Europe/Helsinki')]["incoming_duration_std"] == 0
    assert test_user.loc[pd.Timestamp("2019-08-13 06:00:00", tz='Europe/Helsinki')]["group"] == "group1"
    

def test_message_features():
    data = niimpy.read_csv(config.MULTIUSER_AWARE_MESSAGES_PATH, tz='Europe/Helsinki')
    data["group"] = "group1"
    test = comms.extract_features_comms(data, features=None)

    test_user = test[test["user"] == "jd9INuQ5BBlW"]
    assert test_user.loc[pd.Timestamp("2020-01-09 02:30:00+02:00", tz='Europe/Helsinki')]["outgoing_count"] == 5
    assert test_user.loc[pd.Timestamp("2020-01-09 02:30:00+02:00", tz='Europe/Helsinki')]["incoming_count"] == 5
    assert test_user.loc[pd.Timestamp("2020-01-09 02:30:00+02:00", tz='Europe/Helsinki')]["outgoing_incoming_ratio"] == 1.0
    assert test_user.loc[pd.Timestamp("2020-01-09 02:30:00+02:00", tz='Europe/Helsinki')]["group"] == "group1"


def test_message_features_with_gmail():
    path = os.path.join(config.GOOGLE_TAKEOUT_DIR, "Takeout", "Mail", "All mail Including Spam and Trash.mbox")
    with pytest.warns(UserWarning):
        data = niimpy.reading.google_takeout.email_activity(
            path, sentiment_batch_size = 2
        )
        data["group"] = "group1"

    test = comms.extract_features_comms(data, features=None)
    assert test.loc[pd.Timestamp("2023-12-15 12:30:00+00:00", tz='Europe/Helsinki')]["outgoing_count"] == 0
    assert test.loc[pd.Timestamp("2023-12-15 12:30:00+00:00", tz='Europe/Helsinki')]["incoming_count"] == 2
    assert test.loc[pd.Timestamp("2023-12-15 12:30:00+00:00", tz='Europe/Helsinki')]["outgoing_incoming_ratio"] == 0
    assert test.loc[pd.Timestamp("2023-12-15 12:30:00+00:00", tz='Europe/Helsinki')]["group"] == "group1"


def test_message_features_with_google_chat(google_takeout_zipped):
    with pytest.warns(UserWarning):
        data = niimpy.reading.google_takeout.chat(
            google_takeout_zipped,
            sentiment=False,
            sentiment_batch_size = 2
        )
        data["group"] = "group1"
        data["extra_column"] = "extra"

    test = comms.extract_features_comms(data, features=None)
    assert "extra_column" not in test.columns
    print(test.loc[pd.Timestamp("2024-01-30 13:00:00+00:00", tz='Europe/Helsinki')])
    assert test.loc[pd.Timestamp("2024-01-30 13:00:00+00:00", tz='Europe/Helsinki')]["outgoing_count"] == 2
    assert test.loc[pd.Timestamp("2024-01-30 13:00:00+00:00", tz='Europe/Helsinki')]["group"] == "group1"


def test_call_distribution():
    data = niimpy.read_csv(config.MULTIUSER_AWARE_CALLS_PATH, tz='Europe/Helsinki')
    data["group"] = "group1"
    test = niimpy.preprocessing.communication.call_distribution(data)
    test_user = test[test["user"] == "jd9INuQ5BBlW"]
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["distribution"] == pytest.approx(0.88888888)
    assert test_user.loc[pd.Timestamp("2020-01-09 02:00:00", tz='Europe/Helsinki')]["group"] == "group1"
