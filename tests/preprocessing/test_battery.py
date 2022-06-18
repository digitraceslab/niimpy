import pandas as pd
from pandas import Timestamp
import numpy as np
import pytest

import niimpy
from niimpy.preprocessing.util import TZ

df11 = pd.DataFrame(
    {"user": ['wAzQNrdKZZax'] * 3 + ['Afxzi7oI0yyp'] * 3 + ['lb983ODxEFUD'] * 3,
     "device": ['iMTB2alwYk1B'] * 3 + ['3Zkk0bhWmyny'] * 3 + ['n8rndM6J5_4B'] * 3,
     "time": [1547709614.05, 1547709686.036, 1547709722.06, 1547710540.99, 1547710688.469, 1547711339.439,
              1547711831.275, 1547711952.182, 1547712028.281],
     "battery_level": [96, 96, 95, 95, 94, 93, 94, 94, 94],
     "battery_status": ['3'] * 5 + ['2', '2', '3', '3'],
     "battery_health": ['2'] * 9,
     "battery_adaptor": ['0'] * 5 + ['1', '1', '0', '0'],
     "datetime": ['2019-01-17 09:20:14.049999872+02:00', '2019-01-17 09:21:26.036000+02:00',
                  '2019-01-17 09:22:02.060000+02:00',
                  '2019-01-17 09:35:40.990000128+02:00', '2019-01-17 09:38:08.469000192+02:00',
                  '2019-01-17 09:48:59.438999808+02:00',
                  '2019-01-17 09:57:11.275000064+02:00', '2019-01-17 09:59:12.181999872+02:00',
                  '2019-01-17 10:00:28.280999936+02:00']
     })
df11['datetime'] = pd.to_datetime(df11['datetime'])
df11 = df11.set_index('datetime', drop=False)


def test_get_battery_data():
    df = df11.copy()
    battery = niimpy.preprocessing.battery.get_battery_data(df)
    assert battery.loc[Timestamp('2019-01-17 09:20:14.049999872+02:00'), 'battery_level'] == 96
    assert battery.loc[Timestamp('2019-01-17 09:21:26.036000+02:00'), 'battery_health'] == '2'
    assert battery.loc[Timestamp('2019-01-17 09:48:59.438999808+02:00'), 'battery_status'] == '2'
    assert battery.loc[Timestamp('2019-01-17 09:57:11.275000064+02:00'), 'battery_adaptor'] == '1'


def test_battery_occurrences():
    df = df11.copy()
    k = niimpy.preprocessing.battery.battery_occurrences
    occurences = niimpy.preprocessing.battery.extract_features_battery(df, feature_functions={k: {'hours':0,'minutes':10}})
    print(occurences)
    assert occurences.loc[Timestamp('2019-01-17 09:20:14.049999872+02:00'), 'occurrences'] == 2
    assert occurences.loc[Timestamp('2019-01-17 09:40:14.049999872+02:00'), 'occurrences'] == 1


def test_battery_gaps():
    df = df11.copy()

    k = niimpy.preprocessing.battery.battery_gaps
    gaps = niimpy.preprocessing.battery.extract_features_battery(df, feature_functions={k: {}})
    assert gaps.delta.dtype == 'timedelta64[ns]'
    assert gaps.tvalue.dtype == 'datetime64[ns, pytz.FixedOffset(120)]'
    assert gaps.loc[Timestamp('2019-01-17 09:22:02.060000+02:00'), 'delta'] == pd.Timedelta('0 days 00:00:36.024000')
    assert gaps.loc[Timestamp('2019-01-17 09:57:11.275000064+02:00'), 'tvalue'] == pd.Timestamp(
        '2019-01-17 09:57:11.275000064+0200', tz='Europe/Helsinki')


def test_battery_charge_discharge():
    df = df11.copy()
    k = niimpy.preprocessing.battery.battery_charge_discharge
    chdisch = niimpy.preprocessing.battery.extract_features_battery(df, feature_functions={k: {}})
    assert chdisch.tdelta.dtype == 'timedelta64[ns]'
    assert chdisch.tvalue.dtype == 'datetime64[ns, pytz.FixedOffset(120)]'
    assert chdisch.loc[Timestamp('2019-01-17 09:48:59.438999808+02:00'), 'bdelta'] == -1
    assert chdisch.loc[Timestamp('2019-01-17 09:48:59.438999808+02:00'), 'charge/discharge'] == -0.0015361691024008617
