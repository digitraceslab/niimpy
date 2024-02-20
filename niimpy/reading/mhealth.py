"""Read data from various formats, user entery point.

This module contains various functions `read_*` which load data from different
formats into pandas.DataFrame:s.  As a side effect, it provides the
authoritative information on how incoming data is converted to dataframes.

"""

import pandas as pd
import json


mHealth_duration_units = {
    "ps": "picoseconds",
    "ns": "nanoseconds",
    "us": "microseconds",
    "ms": "milliseconds",
    "sec": "seconds",
    "min": "minutes",
    "h": "hours",
    "d": "days",
    "wk": "weeks",
    "Mo": "months",
    "yr": "years",
}


def format_part_of_day(df, prefix):
    ''' Format columns with mHealth formatted part of day. Returns a dataframe
    with date stored in the column "date" and "part_of_day". Options for
    part of day are "morning", "afternoon", "evening", "night".
    '''

    date_col = f'{prefix}.date'
    part_of_day_col = f'{prefix}.part_of_day'

    df = df.rename(columns={
        date_col: "date",
        part_of_day_col: "part_of_day",
    })

    rows = ~df["part_of_day"].isnull()
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df.loc[rows, "timestamp"] = df.loc[rows, "date"]
    return df


def duration_to_timedelta(df, duration_col):
    ''' Format a duration entry in the mHealth format. Duration
    is a dictionary that contains a value and a unit. The 
    dataframe should contain two columns, DURATION_COL_NAME.value
    and DURATION_COL_NAME.unit.

    Returns a dataframe with a DURATION_COL_NAME column containing a
    a timedelta object. The original columns will be dropped.
    '''
    duration_value_col = f'{duration_col}.value'
    duration_unit_col = f'{duration_col}.unit'

    def format_duration_row(row):
        unit = mHealth_duration_units[row[duration_unit_col]]
        value = row[duration_value_col]

        if unit == "picoseconds": # DateOffset doesn't support picoseconds
            unit = "nanoseconds"
            value *= 0.001

        return pd.to_timedelta(value, unit=unit)

    if duration_value_col in df.columns:
        # Format duration as DateOffset. We use this below to calculate either start of end
        rows = ~df[duration_value_col].isnull()
        df.loc[rows, duration_col] = df.loc[rows].apply(format_duration_row, axis=1)

    df = df.drop([duration_value_col, duration_unit_col], axis=1)
    return df


def format_time_interval(df, prefix):
    ''' Format a database containing columns in the mHealth time interval.
    
    A time interval in the mHealth format has either
     - a date and a time of day (morning, afternoon, evening or night), or
     - any two of start time, end time and duration.

    In the first case, the formatted database will contain two columns:
    measure_date and time_of_day.

    In the second case, the formatted database will contain two columns:
    start and end.

    Also sets the timestamp to "start" or "date" if available.
    '''    
    # Create any of the result columns thay may not exist
    for col in ["start", "end"]:
        if col not in df.columns:
            df[col] = pd.Series(pd.NaT, index=df.index)
            df[col] = pd.to_datetime(df[col], utc=True)

    if f'{prefix}.part_of_day' in df.columns:
        df = format_part_of_day(df, prefix)

    # Construct column names from the prefix
    start_col = f'{prefix}.start_date_time'
    end_col = f'{prefix}.end_date_time'
    duration_col = f'{prefix}.duration'

    # Format the date-like columns. All the mHealth columns might exist if the formatting in the data is mixed
    for col, mHealth_col in [("start", start_col), ("end", end_col)]:
        if mHealth_col in df.columns:
            df[col] = pd.to_datetime(df[mHealth_col], utc=True)

    # Format duration as DateOffset. We use this below to calculate either start of end
    df = duration_to_timedelta(df, duration_col)

    # If duration is provided, we calculate either start or end
    if start_col in df.columns and duration_col in df.columns:
        rows = ~df[duration_col].isnull() & ~df[start_col].isnull()
        df.loc[rows, "end"] = df.loc[rows, "start"] + df.loc[rows, duration_col]
        df["end"] = pd.to_datetime(df["end"], utc=True)

    if end_col in df.columns and duration_col in df.columns:
        rows = ~df[end_col].isnull() & ~df[duration_col].isnull()
        df.loc[rows, "start"] = df.loc[rows, "end"] - df.loc[rows, duration_col]
        df["start"] = pd.to_datetime(df["start"], utc=True)


    # Drop the original columns
    for col in [start_col, end_col, duration_col]:
        if col in df.columns:
            df = df.drop(col, axis=1)

    # Set timestamp to the start time
    df["timestamp"] = df["start"]

    # where start time is abset (happens when time interval is given as
    # date and part of day), set timestamp to date
    if "date" in df.columns:
        rows = df["timestamp"].isnull()
        df.loc[rows, "timestamp"] = df.loc[rows, "date"]
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    return df



def total_sleep_time(data_list):
    '''
    Format mHealth total sleep data from json formatted data to a Niimpy
    compatible DataFrame. The DataFrame contains the columns
        - total_sleep_time : The total sleep time measurement
        - total_sleep_time_unit : The unit the measuremnet is expressed in
        - measurement interval columns
        - possible descriptive statistics columns

    The measurement interval column are either
        - start : start time of the measurement interval
        - end : end time of the measurement interval
    or
        - date : the date of the measurement
        - part_of_day : the time of day the measurement was made
    
    The descriptive statistics columns would be
        - descriptive_statistics : Describes how the measurement is calculated
        - descriptive_statistics_denominator : Time interval the above desciption refers to.

    The dataframe is indexed by "timestamp", which is either the "start" or the "date".

    Parameters
    ----------

    data_list: list of dictionaries
        MHealth formatted sleep duration data loaded with json.load()
    
    Returns
    -------

    data: A pandas.DataFrame containing sleep duration data

    
    '''
    
    df = pd.json_normalize(data_list)

    df = duration_to_timedelta(df, "total_sleep_time")
    df = format_time_interval(df, "effective_time_frame.time_interval")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df.set_index('timestamp', inplace=True)
    return df


def total_sleep_time_from_file(filename):
    ''' Read mHealth total sleep time from a file and convert into a Niimpy
    compatible DataFrame using total_sleep_time. The dataframe
    contains the columns
        - total_sleep_time : The total sleep time measurement
        - total_sleep_time_unit : The unit the measuremnet is expressed in
        - measurement interval columns
        - possible descriptive statistics columns

    The measurement interval column are either
        - start : start time of the measurement interval
        - end : end time of the measurement interval
    or
        - date : the date of the measurement
        - part_of_day : the time of day the measurement was made
    
    The descriptive statistics columns would be
        - descriptive_statistics : Describes how the measurement is calculated
        - descriptive_statistics_denomirator : Time interval the above 
          description refers to.

    The dataframe is indexed by "timestamp", which is either the "start" or the "date".

    Parameters
    ----------

    filename: string
        Path to the file containing mhealth formatted sleep duration data.
    
    Returns
    -------

    data: A pandas.DataFrame containing sleep duration data
    
    '''
    with open(filename) as f:
        data = json.load(f)

    df = total_sleep_time(data)

    return df

def heart_rate(data_list):
    ''' Format the heart rate json data into a niimpy dataframe.

    The dataframe contains the columns
        - heart_rate : Heart rate measurement in beats per minute
        - (optional) time interval columns
        - (optional) descriptive statistics column, a string
        - (optional) temporal relationship to sleep column, a string
        - (optional) temporal relationship to physical activity column, a 
           string

    Measurement time or interval columns. If exact time is given, only the
    index is set. If a time interval is given, we set two additional columns
        - start : start time of the measurement interval
        - end : end time of the measurement interval
    and set the index to the start time.
    
    The descriptive statistics column describes how the value is calculated
    over the given time interval. For example, "average" would denote a mean
    over the time period.

    The temporal relationship to sleep is one of "before sleeping", "during 
    sleep" or "on waking".

    The temporal relationship to physical activity is one of "at rest", 
    "active", "before exercise", "after exercise" or "during exercise".

    Parameters
    ----------

    data_list: list of dictionaries
        MHealth formatted heart rate data loaded using json.load().

    Returns
    -------

    data: A pandas.DataFrame containing geolocation data
    '''
    df = pd.json_normalize(data_list)

    # The mhealth standard specifies the unit is always beats per minute.
    # We can drop the unit column without converting the value
    df.drop("heart_rate.unit", axis=1, inplace=True)
    df = df.rename(columns={
        "heart_rate.value": "heart_rate",
    })

    # Each sample contains a time_frame, which is either a duration or a
    # date-time string
    rows = ~df["effective_time_frame.date_time"].isna()
    df.loc[rows, "timestamp"] = pd.to_datetime(df["effective_time_frame.date_time"], utc=True)

    df = format_time_interval(df, "effective_time_frame.time_interval")

    df.set_index('timestamp', inplace=True)
    return df


def heart_rate_from_file(filename):
    '''Read mHealth formatted heart rate data from a file and convert it to
    a Niimpy compatible dataframe.  

    The dataframe contains the columns
        - heart_rate : Heart rate measurement in beats per minute
        - (optional) time interval columns
        - (optional) descriptive statistics column, a string
        - (optional) temporal relationship to sleep column, a string
        - (optional) temporal relationship to physical activity column, a 
           string

    Measurement time or interval columns. If exact time is given, only the
    index is set. If a time interval is given, we set two additional columns
        - start : start time of the measurement interval
        - end : end time of the measurement interval
    and set the index to the start time.
    
    The descriptive statistics column describes how the value is calculated
    over the given time interval. For example, "average" would denote a mean
    over the time period.

    The temporal relationship to sleep is one of "before sleeping", "during 
    sleep" or "on waking".

    The temporal relationship to physical activity is one of "at rest", 
    "active", "before exercise", "after exercise" or "during exercise".

    Parameters
    ----------

    filename: string
        Path to the file containing mhealth formatted heart rate data.
    
    Returns
    -------

    data: A pandas.DataFrame containing heart rate data
    '''

    with open(filename) as f:
        data = json.load(f)

    df = heart_rate(data)

    return df



def geolocation(data_list):
    ''' Format the geolocation json data into a niimpy dataframe.

    Parameters
    ----------

    data_list: list of dictionaries
        MHealth formatted geolocation data loaded using json.load().

    Returns
    -------

    data: A pandas.DataFrame containing geolocation data
    '''
    df = pd.json_normalize(data_list)

    # Keep rows where latitude and longitude are given correctly
    df = df[df["latitude.unit"] == "deg"]
    df = df[df["longitude.unit"] == "deg"]
    df.rename(columns={
        "latitude.value": "latitude",
        "longitude.value": "longitude",
    }, inplace=True)

    return df


def geolocation_from_file(filename):
    '''Read mHealth formatted geolocation data from a file and convert it to
    a Niimpy compatible dataframe.  

    Parameters
    ----------

    filename: string
        Path to the file containing mhealth formatted geolocation data.
    
    Returns
    -------

    data: A pandas.DataFrame containing geolocation data
    '''

    with open(filename) as f:
        data = json.load(f)

    df = geolocation(data)

    return df

