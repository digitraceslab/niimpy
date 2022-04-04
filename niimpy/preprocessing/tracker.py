import pandas as pd
import numpy as np
import sys
import sklearn as sckit
from sklearn import preprocessing
from scipy.stats import wasserstein_distance

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

