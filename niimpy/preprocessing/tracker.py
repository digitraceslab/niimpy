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

def self_refeference_distance_df(df, window=1, method='wass', bins=None):
    """Calculate the distance of distribution between one day and individual-average.

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing the data. The dataframe is assumed to be in wide format, and timestamp indexed.
    window : int
        The length of day-window between distribution. Default to 1, which means that 
        the distance will be calculated between consecutive days.
    method : str
        Method to calculate the distance. Possible values: 'kl', 'js', 'wass'.
        'kl': Kullback–Leibler divergence
        'js': Jensen-Shannon divergence
        'wass': Wasserstein distance, or Earth's mover distance
        Default to 'js'
    bins: int, optional
        If given, apply binning on consecutive values. 
        
    Returns
    -------
    df: pandas DataFrame
        A dataframe containing the self-average routine distance for each month of each year.
    """
    # Fill the NaN with 0
    df = df.fillna(0)
    
    if method == 'kl':
        dist_func = kl_divergence
    elif method == 'js':
        dist_func = js_divergence
    elif method == 'wass':
        dist_func = earth_mover_distance
    else:
        print("Cant recognize method")
        
    ids = []
    final_df = pd.DataFrame()
    
    # Upsample data
    upsampled_df = df.resample("{}H".format(int(24/bins))).sum()

    # Iterate by columns
    for uid in df.columns:
        
        # First, get rid of all zero rows that contain no value
        sample = upsampled_df[uid].loc[~(upsampled_df==0).all(axis=1)]

        # Calculate baseline average distance 
        avg_dist = sample.groupby(sample.index.hour).mean()
        
        # Now, calculate everday distance against the baseline
        day_dist = sample.groupby([sample.index.month,sample.index.day, sample.index.year]).apply(lambda x: dist_func(x, avg_dist))
        day_dist.index = pd.MultiIndex.from_tuples(day_dist.index, names=['month', 'day', 'year'])
        day_dist = day_dist.reset_index()
                
        # Finally, get the monthly average
        monthly_avg_dist = day_dist.groupby(['month', 'year'])[uid].mean()

        # Concatenate to the final result
        final_df = pd.concat([final_df, monthly_avg_dist], axis=1)

    # Reset the index and rename columns
    final_df = final_df.reset_index()
    final_df = final_df.rename(columns={"level_0": "month", "level_1": "year"}, errors="raise")

    return final_df

def between_day_distance_df(df, window=1, method='js', bins=None):
    """Calculate the distance of distribution between consecutive days.

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing the data. The dataframe is assumed to be in wide format, and timestamp indexed.
    window : int
        The length of day-window between distribution. Default to 1, which means that 
        the distance will be calculated between consecutive days.
    method : str
        Method to calculate the distance. Possible values: 'kl', 'js', 'wass'.
        'kl': Kullback–Leibler divergence
        'js': Jensen-Shannon divergence
        'wass': Wasserstein distance, or Earth's mover distance
        Default to 'js'
    bins: int, optional
        If given, apply binning on consecutive values. 
        
    Returns
    -------
    df: pandas DataFrame
        A dataframe containing the average consecutive-routine distance for each month of each year.
    """
    # Fill the NaN with 0
    df = df.fillna(0)
    
    if method == 'kl':
        dist_func = kl_divergence
    elif method == 'js':
        dist_func = js_divergence
    elif method == 'wass':
        dist_func = earth_mover_distance
    else:
        print("Cant recognize method")
        
    def _calculate_within_day_distance(x, bins):
        ls = np.split(x.values, int(len(x.values) / bins)) 
        dist = []
        for i in range(len(ls)-1):
            d1 = ls[i]
            d2 = ls[i+1]
            dist.append(dist_func(d1, d2))
        
        return np.array(dist).mean()
    
        
    # Upsample data
    upsampled_df = df.resample("{}H".format(int(24/bins))).sum()
    final_df = pd.DataFrame()
    
    # Iterate by columns
    for uid in df.columns:
        # First, get rid of all zero rows that contain no value
        sample = upsampled_df[uid].loc[~(upsampled_df==0).all(axis=1)]
        
        # Now, calculate everday distance against the baseline
        day_dist = sample.groupby([sample.index.month, sample.index.year]).apply(lambda x: _calculate_within_day_distance(x, bins))
        day_dist.index = pd.MultiIndex.from_tuples(day_dist.index, names=['month', 'year'])
        day_dist = day_dist.reset_index()
                
        # Finally, get the monthly average
        monthly_avg_dist = day_dist.groupby(['month', 'year'])[uid].mean()

        # Concatenate to the final result
        final_df = pd.concat([final_df, monthly_avg_dist], axis=1)
        
    # Reset the index and rename columns
    final_df = final_df.reset_index()
    final_df = final_df.rename(columns={"level_0": "month", "level_1": "year"}, errors="raise")
    return final_df


# Helper functions
def kl_divergence(p, q):
    # Add tiny values to avoid division by zeros
    p += 1e-9
    q += 1e-9
    return sum(p[i] * log2(p[i]/q[i]) for i in range(len(p)))

def js_divergence(p, q):
    m = 0.5 * (p + q)
    return 0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)

def earth_mover_distance(p, q):
    return wasserstein_distance(p, q)
