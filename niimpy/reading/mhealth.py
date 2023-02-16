"""Read data from various formats, user entery point.

This module contains various functions `read_*` which load data from different
formats into pandas.DataFrame:s.  As a side effect, it provides the
authoritative information on how incoming data is converted to dataframes.

"""

import pandas as pd
import warnings
import json

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

    rows = ~df["date"].isnull()
    df.loc[rows, "date"] = pd.to_datetime(df.loc[rows, "date"])
    df.loc[rows, "timestamp"] = df.loc[rows, "date"]
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
    '''    
    # Create any of the result columns thay may not exist
    for col in ["start", "end"]:
        if col not in df.columns:
            df[col] = None

    if f'{prefix}.part_of_day' in df.columns:
        df = format_part_of_day(df, prefix)

    # Construct column names from the prefix
    start_col = f'{prefix}.start_date_time'
    end_col = f'{prefix}.end_date_time'
    duration_value_col = f'{prefix}.duration.value'
    duration_unit_col = f'{prefix}.duration.unit'

    # Format the date-like columns. All the mHealth columns might exist if the formatting in the data is mixed
    for col, mHealth_col in [("start", start_col), ("end", end_col)]:
        if col in df.columns:
            rows = ~df[mHealth_col].isnull()
            df.loc[rows, col] = pd.to_datetime(df.loc[rows, mHealth_col])

    if duration_value_col in df.columns:
        # Format duration as DateOffset. We use this below to calculate either start of end
        mHealth_DateOffset = {
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
        
        def mHealth_to_DateOffset(row):
            unit = mHealth_DateOffset[row[duration_unit_col]]
            value = row[duration_value_col]

            if unit == "picoseconds": # DateOffset doesn't support picoseconds
                unit = "nanoseconds"
                value *= 0.001
            
            return pd.tseries.offsets.DateOffset(**{unit: value})

        rows = ~df[duration_value_col].isnull()
        df.loc[rows, duration_value_col] = df.loc[rows].apply(mHealth_to_DateOffset, axis=1)

    # If duration is provided, we calculate either start or end
    if start_col in df.columns and duration_value_col in df.columns:
        rows = ~df[duration_value_col].isnull() & ~df[start_col].isnull()
        df.loc[rows, "end"] = df.loc[rows, "start"] + df.loc[rows, duration_value_col]

    if start_col in df.columns and duration_value_col in df.columns:
        rows = ~df[end_col].isnull() & ~df[duration_value_col].isnull()
        df.loc[rows, "start"] = df.loc[rows, "end"] - df.loc[rows, duration_value_col]

    # Drop the original columns
    df = df.drop([start_col, end_col, duration_value_col, duration_unit_col], axis=1)
    rows = ~df["start"].isnull()
    df.loc[rows, "timestamp"] = df.loc[rows, "start"]

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
        - descriptive_statistics_denomirator : Time interval the above desciption refers to.

    The dataframe is indexed by "timestamp", which is either the "start" or the "date".
    '''
    
    df = pd.json_normalize(data_list)
    total_sleep_time_columns = {
        "total_sleep_time.value": "total_sleep_time",
        "total_sleep_time.unit": "total_sleep_time_unit",
    }

    df = format_time_interval(df, "effective_time_frame.time_interval")
    df = df.rename(columns=total_sleep_time_columns)

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
        - descriptive_statistics_denomirator : Time interval the above desciption refers to.

    The dataframe is indexed by "timestamp", which is either the "start" or the "date".
    '''
    with open(filename) as f:
        data = json.load(f)

    df = total_sleep_time(data)

    return df
