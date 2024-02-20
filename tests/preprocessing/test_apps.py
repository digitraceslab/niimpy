import os

import numpy as np
import pandas as pd
import numpy as np

import niimpy
import niimpy.preprocessing.application as app
from niimpy import config

# read sample data
data = niimpy.read_csv(config.SINGLEUSER_AWARE_APP_PATH, tz='Europe/Helsinki')
screen = niimpy.read_csv(config.MULTIUSER_AWARE_SCREEN_PATH, tz='Europe/Helsinki')
battery = niimpy.read_csv(config.MULTIUSER_AWARE_BATTERY_PATH, tz='Europe/Helsinki')

def test_audio_features():
    
    test = app.extract_features_app(data, battery, screen, features=None)    
    time = "2019-08-05 14:00:00+03:00"
    
    user_comm = test[(test["user"] == "iGyXetHE3S8u") & (test["app_group"] == "comm")]
    user_work = test[(test["user"] == "iGyXetHE3S8u") & (test["app_group"] == "work")]
    assert user_comm.loc[time]["count"] == 86
    assert user_work.loc[time]["count"] == 7
    assert user_comm.loc[time]["duration"] == 37
    assert user_work.loc[time]["duration"] == 6
       
    features ={app.app_count:{"app_column_name":"application_name", "screen_column_name":"screen_status","resample_args":{"rule":"30S"}},
               app.app_duration:{"resample_args":{"rule":"1min"}}}
    test = app.extract_features_app(data, battery, screen, features=features)
    
    time = "2019-08-05 14:03:00+03:00"
    
    user_comm = test[(test["user"] == "iGyXetHE3S8u") & (test["app_group"] == "comm")]
    user_work = test[(test["user"] == "iGyXetHE3S8u") & (test["app_group"] == "work")]
    assert user_comm.loc[time]["count"] == 34
    assert user_work.loc[time]["count"] == 3
    assert user_comm.loc[time]["duration"] == 26
    assert user_work.loc[time]["duration"] == 5