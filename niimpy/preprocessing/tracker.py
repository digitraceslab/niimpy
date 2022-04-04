import pandas as pd
import numpy as np
import sys
import sklearn as sckit
from sklearn import preprocessing
from scipy.stats import wasserstein_distance

def step_summary(df, value_col='values', user_id=None, start_date=None, end_date=None):
    """Return the summary

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing the hourly step count of an individual. The dataframe must be date time index.
    value_col: str.
        Column contains step values. Default value is "values".
    user_id: list. Optional
        List of user id. If none given, returns summary for all users.
    start_date: string. Optional
        Start date of time segment used for computing the summary. If not given, acquire summary for the whole time range.
    end_date: string.  Optional
        End date of time segment used for computing the summary. If not given, acquire summary for the whole time range.
        
    Returns
    -------
    summary_df: pandas DataFrame
        A dataframe containing user id and associated step summary.
    """

    assert 'user' in df.columns, 'User column does not exist'
    assert df.index.inferred_type == 'datetime64', "Dataframe must have a datetime index"    
        
    if user_id != None:
        assert isinstance(user_id, list), 'User id must be a list'
        df = df[df['user'] in user_id]
    
    if start_date != None and end_date != None:
        df = df[start_date:end_date]
    elif start_date == None and end_date != None:
        df = df[:end_date]
    elif start_date != None and end_date == None:
        df = df[start_date:]
        
    # Calculate sum of step
    df['daily_sum'] = df.groupby(by=[df.index.day, df.index.month, 'user'])[value_col].transform('sum') # stores sum of daily step

    # Under the assumption that a user cannot have zero steps per day, we remove rows where daily_sum are zero
    df = df[~(df.daily_sum == 0)]

    summary_df = pd.DataFrame()
    summary_df['median_sum_step'] = df.groupby('user')['daily_sum'].median()
    summary_df['avg_sum_step'] = df.groupby('user')['daily_sum'].mean()
    summary_df['std_sum_step'] = df.groupby('user')['daily_sum'].std()
    summary_df['min_sum_step'] = df.groupby('user')['daily_sum'].min()
    summary_df['max_sum_step'] = df.groupby('user')['daily_sum'].max()
    
    return summary_df.reset_index()

def daily_step_distribution(steps_df):

    """Return distribution of steps within each day.

    Parameters
    ----------
    steps_df : Pandas Dataframe
        Dataframe containing the hourly step count of an individual.
        
    Returns
    -------
    df: pandas DataFrame
        A dataframe containing the distribution of step count per day.
    """

    # Combine date and time to acquire  timestamp 
    df = steps_df.copy()
    df['time'] = pd.to_datetime(df['date'] + ":" + df['time'], format='%Y-%m-%d:%H:%M:%S.%f')

    # Dummy columns for hour, month, day for easier operations later on
    df['hour'] = df.level_0.dt.hour
    df['month'] = df.level_0.dt.month
    df['day'] = df.level_0.dt.day

    df = steps_df.df(columns={"subject_id": "user"}) # rename column, to be niimpy-compatible

    # Remove duplicates
    df = df.drop_duplicates(subset=['user', 'date', 'time'], keep='last')

    # Convert the absolute values into distribution. This can be understood as the portion of steps the users took during each hour
    df['daily_sum'] = df.groupby(by=['day', 'month', 'user'])['steps'].transform('sum') # stores sum of daily step

    # Divide hourly steps by daily sum to get the distribution
    df['daily_distribution'] = df['steps'] / df['daily_sum'] 

    # Set timestamp index
    df = df.set_index("time")

    return df

