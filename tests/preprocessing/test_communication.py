import os

import numpy as np
import pandas as pd
import numpy as np

import niimpy
import niimpy.preprocessing.communication as comms
from niimpy import config

# read sample data
data = niimpy.read_csv(config.MULTIUSER_AWARE_CALLS_PATH, tz='Europe/Helsinki')

def test_audio_features():
    
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
       
    features ={comms.call_count:{"communication_column_name":"call_duration","resample_args":{"rule":"1D"}},
               comms.call_outgoing_incoming_ratio:{"communication_column_name":"call_duration","resample_args":{"rule":"1D"}}}
    test = comms.extract_features_comms(data, features=features)
    
    test_user = test[test["user"] == "jd9INuQ5BBlW"]
    assert test_user.loc[pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["missed_count"] == 1
    assert test_user.loc[pd.Timestamp("2020-01-09", tz='Europe/Helsinki')]["incoming_count"] == 7
    test_user = test[test["user"] == "iGyXetHE3S8u"]
    assert test_user.loc[pd.Timestamp("2019-08-10", tz='Europe/Helsinki')]["outgoing_count"] == 2
    assert test_user.loc[pd.Timestamp("2019-08-10", tz='Europe/Helsinki')]["outgoing_incoming_ratio"] == 2
    
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
    