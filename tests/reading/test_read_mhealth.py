import pandas as pd

import niimpy
from niimpy import config


def test_format_part_of_day():
    df = pd.DataFrame([{
        "prefix.col.date": "2022-01-14",
        "prefix.col.part_of_day": "afternoon"
    }])
    df = niimpy.reading.mhealth.format_part_of_day(df, "prefix.col")

    assert df["date"][0] == pd.to_datetime("2022-01-14 00:00:00+00:00")
    assert df["part_of_day"][0] == "afternoon"


def test_duration_to_timedelta():
    df = pd.DataFrame([{
            "prefix.col.value": 20,
            "prefix.col.unit": "min"
        },
        {
            "prefix.col.value": 20,
            "prefix.col.unit": "ps"
        }
    ])

    df = niimpy.reading.mhealth.duration_to_timedelta(df, "prefix.col")

    assert df.iloc[0]["prefix.col"] == pd.to_timedelta(20, unit="minutes")
    assert df.iloc[1]["prefix.col"] == pd.to_timedelta(0.02, unit="nanoseconds")


def test_format_time_interval():
    df = pd.DataFrame([{
            "prefix.col.start_date_time": "2022-01-03 10:00:00+02:00",
            "prefix.col.duration.value": 35,
            "prefix.col.duration.unit": "min"
        },
        {
            "prefix.col.end_date_time": "2022-01-03 10:35:00+02:00",
            "prefix.col.duration.value": 35,
            "prefix.col.duration.unit": "min"
        },
        {
            "prefix.col.start_date_time": "2022-01-03 10:00:00+02:00",
            "prefix.col.end_date_time": "2022-01-03 10:35:00+02:00"
        }
    ])

    df = niimpy.reading.mhealth.format_time_interval(df, "prefix.col")

    assert df["timestamp"][0] == pd.to_datetime("2022-01-03 10:00:00+02:00")
    assert df["start"][0] == pd.to_datetime("2022-01-03 10:00:00+02:00")
    assert df["end"][0] == pd.to_datetime("2022-01-03 10:35:00+02:00")
    assert df["timestamp"][1] == pd.to_datetime("2022-01-03 10:00:00+02:00")
    assert df["start"][1] == pd.to_datetime("2022-01-03 10:00:00+02:00")
    assert df["end"][1] == pd.to_datetime("2022-01-03 10:35:00+02:00")
    assert df["timestamp"][2] == pd.to_datetime("2022-01-03 10:00:00+02:00")
    assert df["start"][2] == pd.to_datetime("2022-01-03 10:00:00+02:00")
    assert df["end"][2] == pd.to_datetime("2022-01-03 10:35:00+02:00")
    assert all(df.columns == ["start", "end", "timestamp"])



def test_read_mhealth_total_sleep_time():
    data = niimpy.reading.mhealth.total_sleep_time_from_file(config.MHEALTH_TOTAL_SLEEP_TIME_PATH)

    row = data.loc["2016-02-06 04:35:00+00:00"]
    assert row['total_sleep_time'] == pd.Timedelta(465, unit="minutes")
    assert row['start'] == pd.to_datetime("2016-02-06 04:35:00+00:00")
    assert row['end'] == pd.to_datetime("2016-02-06 14:35:00+00:00")

    row = data.loc["2016-02-05 15:00:00+00:00"]
    assert row['descriptive_statistic'] == "average"
    assert row['descriptive_statistic_denominator'] == "d"

    row = data.loc["2013-01-26 07:35:00+00:00"]
    assert row['start'] == pd.to_datetime("2013-01-26 07:35:00+00:00")
    assert row['end'] == pd.to_datetime("2013-02-05 07:35:00+00:00")

    part_of_day_row = data.iloc[3]
    assert part_of_day_row['date'] == pd.to_datetime("2013-02-05", utc=True)
    assert part_of_day_row['part_of_day'] == "evening"



def test_read_mhealth_heart_rate():
    data = niimpy.reading.mhealth.heart_rate_from_file(config.MHEALTH_HEART_RATE_PATH)
    assert data.iloc[0]['heart_rate'] == 70
    assert data.iloc[1]['heart_rate'] == 65
    assert data.iloc[2]['descriptive_statistic'] == "average"
    assert data.iloc[2]['temporal_relationship_to_sleep'] == "during sleep"
    assert data.iloc[0]['temporal_relationship_to_sleep'] == "on waking"
    assert data.iloc[2]['start'] == pd.to_datetime("2023-12-20T01:50:00-02:00")


def test_read_mhealth_geolocation():
    data = niimpy.reading.mhealth.geolocation_from_file(config.MHEALTH_GEOLOCATION_PATH)

    assert data.iloc[0]['latitude'] == 60.1867
    assert data.iloc[0]['longitude'] == 24.8283
    assert data.iloc[1]['latitude'] == 60.1867
    assert data.iloc[1]['longitude'] == 24.8283

