import pandas as pd
import datetime

def _align_data(data: pd.DataFrame, period: int, freq: str) -> pd.DataFrame:
    """
    Align user records by timestamp ensuring the first record starts either at 00:00 
    daily or 00:00 of a Monday weekly.

    Parameters:
    - data (pd.DataFrame): Input dataframe with a Timestamp index.
    - period (int): Number of hours for the time span (e.g., 24 for 1 day, 168 for 1 week).
    - type (str): Type of alignment, either 'daily' or 'weekly'.

    Returns:
    - pd.DataFrame: Aligned data based on the provided type.

    Raises:
    - ValueError: If an incorrect type is provided.
    """
    
    if freq not in ["daily", "weekly"]:
        raise ValueError(f"Incorrect type '{type}'. Choose between 'daily' and 'weekly'.")
    
    results = []

    for user in data['user'].unique():
        user_data = data[data['user'] == user].sort_index()
        
        # Identify the first index starting at hour 0
        start_indices = user_data.index[user_data.index.hour == 0]

        # If freq is weekly, further refine to start on a Monday
        if freq == "weekly":
            start_indices = start_indices[start_indices.dayofweek == 0]

        if start_indices.empty:
            continue
        
        start_time = start_indices[0]
        end_time = start_time + datetime.timedelta(hours=period)

        # Check if data spans the given period
        if end_time <= user_data.index.max():
            filtered_data = user_data[start_time:end_time]
            results.append(filtered_data)

    results = pd.concat(results)

    return results

def _aggregate(data: pd.DataFrame, groupby_cols: list, freq: str) -> pd.DataFrame:
    """
    Aggregates the data based on the specified frequency either 'daily' or 'weekly'.
    
    Parameters:
    - data (pd.DataFrame): Input dataframe with a Timestamp index and 'user' column.
    - freq (str): Frequency for aggregation. Options: 'daily' or 'weekly'.
    
    Returns:
    - pd.DataFrame: Aggregated data based on the given frequency.
    
    Raises:
    - ValueError: If an incorrect frequency is provided.
    """
    
    if freq not in ["daily", "weekly"]:
        raise ValueError(f"Incorrect frequency '{freq}'. Choose between 'daily' and 'weekly'.")
    
    agg_data = []

    for name, user_data in data.groupby(groupby_cols):
        if freq == 'daily':

            agg_features = user_data.groupby(user_data.index.hour).sum(numeric_only=True)
        else:  # freq == 'weekly'
            user_data['hour_dayofweek'] = user_data.index.strftime('%A %H')
            agg_features = user_data.groupby(['hour_dayofweek']).sum(numeric_only=True)
            agg_features.index.names = ['time']

        for idx, col in enumerate(groupby_cols):
            agg_features[col] = name if isinstance(name, str) else name[idx]
        agg_data.append(agg_features)

    return pd.concat(agg_data)

def _compute_distribution(data: pd.DataFrame,  cols: list, groupby_cols: list, freq: str) -> pd.DataFrame:
    """
    Computes the count distribution for each unique value in a specified column based on frequency.

    Args:
        data (pd.DataFrame): The input dataframe with a Timestamp index.
        cols (list): The name(s) of the column(s) to compute distribution.
        frequency (str): The frequency for aggregation - "daily" or "weekly".

    Returns:
        pd.DataFrame: A dataframe with count distribution for the specified column(s).

    Raises:
        ValueError: If the specified column does not exist in the input dataframe.
    """
    
    # Validate frequency
    if freq not in ["daily", "weekly"]:
        raise ValueError(f"The specified frequency '{freq}' is not valid. Choose 'daily' or 'weekly'.")

    for col in cols:
        if col not in data.columns:
            raise ValueError(f"The specified column '{col}' does not exist in the input dataframe.")
        
        values_sum = data.groupby(by=groupby_cols)[col].transform('sum')
        data[f'{col}_distr'] = data[col] / values_sum
    return data

def compute_rhythms(df: pd.DataFrame, 
                    timebin: str, 
                    cols: list,
                    groupby_cols: list,
                    period: int,
                    freq: str,
                    group: str = None) -> pd.DataFrame:

    """
    Computes rhythms of the input data for a single group based on the provided frequency.

    Steps:
    1. Aligns the data based on the given frequency:
       - 'daily': starts sampling from the first occurrence of 00 hour.
       - 'weekly': starts sampling from the first occurrence of Monday 00 hour.
    2. Resamples data based on the provided timebin.
    3. Aggregates columns by summing values within the same bin.
    4. Normalizes the data to compute the percentage each bin contributes to the total.

    Args:
        df (pd.DataFrame): The input dataframe with a Timestamp index and 'user' column.
        timebin (str): Time bin for grouping, in pandas frequency string format. Possible values: '1H', '2H', '4H', '6H'
        cols (list): Columns to compute the count distribution for.
        groupby_cols (list): Columns to group. 
        period (int): Hours, defines the length for which rhythm is computed. 
                      For instance, 8 weeks would be 8*7*24 hours.
        freq (str): Frequency for sampling, options are 'daily' or 'weekly'.

    Returns:
        pd.DataFrame: A dataframe with call count distribution rhythms.

    Raises:
        ValueError: If an incorrect frequency is provided or if any of the specified columns are not in the input dataframe.
    """

    # Check if index is a DateTime index
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("The input DataFrame must have a DateTime index.")

    aligned_df = _align_data(df, period=period, freq=freq)

    resampled_df = aligned_df.groupby(groupby_cols).resample(timebin).sum().reset_index(level=0) # keep time index

    agg_data = _aggregate(resampled_df, groupby_cols=groupby_cols, freq=freq)
    
    rhythms = _compute_distribution(agg_data, cols, freq)

    return rhythms

