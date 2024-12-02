import pandas as pd
from pandas import Timestamp
import numpy as np
import pytest

import niimpy
from niimpy.preprocessing.util import TZ

df11 = pd.DataFrame(
    {"user": ['wAzQNrdKZZax'] * 3 + ['Afxzi7oI0yyp'] * 3 + ['lb983ODxEFUD'] * 4,
     "device": ['iMTB2alwYk1B'] * 3 + ['3Zkk0bhWmyny'] * 3 + ['n8rndM6J5_4B'] * 4,
     "time": [1547709614.05, 1547709686.036, 1547709722.06, 1547710540.99, 1547710688.469, 1547711339.439,
              1547711831.275, 1547711952.182, 1547712028.281, 1547713932.182],
     "battery_level": [96, 96, 95, 95, 94, 93, 94, 94, 94, 92],
     "battery_status": ['3'] * 5 + ['-2', '2', '3', '-2', '2'],
     "battery_health": ['2'] * 10,
     "battery_adaptor": ['0'] * 5 + ['1', '1', '0', '0', '1'],
     "datetime": ['2019-01-17 09:20:14.049999872+02:00', '2019-01-17 09:21:26.036000+02:00',
                  '2019-01-17 09:22:02.060000+02:00',
                  '2019-01-17 09:35:40.990000128+02:00', '2019-01-17 09:38:08.469000192+02:00',
                  '2019-01-17 09:48:59.438999808+02:00',
                  '2019-01-17 09:57:11.275000064+02:00', '2019-01-17 09:59:12.181999872+02:00',
                  '2019-01-17 10:00:28.280999936+02:00', '2019-01-17 10:32:12.181999872+02:00'
                 ]
     })
df11['datetime'] = pd.to_datetime(df11['datetime'])
df11 = df11.set_index('datetime', drop=False)
df11["group"] = "group1"

def test_format_battery_data():
    df = df11.copy()
    battery = niimpy.preprocessing.battery.format_battery_data(df)

    assert battery.loc[Timestamp('2019-01-17 09:20:14.049999872+02:00'), 'battery_level'] == 96
    assert battery.loc[Timestamp('2019-01-17 09:21:26.036000+02:00'), 'battery_health'] == '2'
    assert battery.loc[Timestamp('2019-01-17 09:48:59.438999808+02:00'), 'battery_status'] == '-2'
    assert battery.loc[Timestamp('2019-01-17 09:57:11.275000064+02:00'), 'battery_adaptor'] == '1'
    assert battery.loc[Timestamp('2019-01-17 09:57:11.275000064+02:00'), 'group'] =="group1"
    

def test_battery_occurrences():
    df = df11.copy()
    df["extra_column"] = "extra"
    k = niimpy.preprocessing.battery.battery_occurrences
    occurrences = niimpy.preprocessing.battery.extract_features_battery(df, features={k: {}})

    assert "extra_column" not in occurrences.columns
    occurrences_user = occurrences[occurrences["user"] == "wAzQNrdKZZax"]
    assert occurrences_user.loc[Timestamp('2019-01-17 09:00:00+02:00')]["occurrences"] == 3
    occurrences_user = occurrences[occurrences["user"] == "lb983ODxEFUD"]
    assert occurrences_user.loc[Timestamp('2019-01-17 10:00:00+02:00')]["occurrences"] == 1
    occurrences_user = occurrences[occurrences["user"] == "Afxzi7oI0yyp"]
    assert occurrences_user.loc[Timestamp('2019-01-17 09:30:00+02:00')]["occurrences"] == 3
    assert occurrences_user.loc[Timestamp('2019-01-17 09:30:00+02:00'), 'group'] =="group1"


def test_battery_gaps():
    df = df11.copy()

    k = niimpy.preprocessing.battery.battery_gaps
    gaps = niimpy.preprocessing.battery.extract_features_battery(df, features={k: {}})
    assert gaps.battery_gap.dtype == 'timedelta64[ns]'
    gaps_user = gaps[gaps["user"] == "Afxzi7oI0yyp"]
    assert gaps_user.loc[Timestamp('2019-01-17 09:30:00+02:00')]["battery_gap"] == pd.Timedelta('0 days 00:04:26.149666560')
    gaps_user = gaps[gaps["user"] == "lb983ODxEFUD"]
    assert gaps_user.loc[Timestamp('2019-01-17 09:30:00+02:00')]["battery_gap"] == pd.Timedelta('0 days 00:01:00.453499904')
    assert gaps_user.loc[Timestamp('2019-01-17 09:30:00+02:00'), 'group'] =="group1"


def test_battery_charge_discharge():
    df = df11.copy()
    k = niimpy.preprocessing.battery.battery_charge_discharge
    chdisch = niimpy.preprocessing.battery.extract_features_battery(df, features={k: {}})
    chdisch_user = chdisch[chdisch["user"] == "lb983ODxEFUD"]
    assert chdisch_user.loc[Timestamp('2019-01-17 10:30:00+02:00')]['bdelta'] == -2.
    chdisch_user = chdisch[chdisch["user"] == "lb983ODxEFUD"]
    assert chdisch_user.loc[Timestamp('2019-01-17 10:30:00+02:00')]['charge/discharge'] == -0.001050474788377773
    assert chdisch_user.loc[Timestamp('2019-01-17 10:30:00+02:00'), 'group'] =="group1"
