import pandas as pd
import datetime


def _align_data(data: pd.DataFrame, period: int, freq: str) -> pd.DataFrame:
    """
    Returns a pandas DataFrame aligned by timestamp, starting either at 00:00 daily or 00:00 of a Monday weekly.

    Parameters
    ----------
    data : pandas.DataFrame
        Input dataframe with a Timestamp index.
    period : int
        Number of hours for the desired time span (e.g., 24 for daily, 168 for weekly).
    type : str
        Type of alignment to perform, can be 'daily' or 'weekly'.

    Returns
    -------
    aligned_data : pandas.DataFrame
        Dataframe aligned based on the provided alignment type.

    Raises
    ------
    ValueError:
        Raised if an invalid alignment type is provided.
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
    Returns a pandas DataFrame aggregated based on the given frequency ('daily' or 'weekly').

    Parameters
    ----------
    data : pandas.DataFrame
        Input dataframe with a Timestamp index and 'user' column.
    freq : str
        Desired frequency for aggregation, either 'daily' or 'weekly'.

    Returns
    -------
    aggregated_data : pandas.DataFrame
        Dataframe aggregated by the specified frequency.

    Raises
    ------
    ValueError:
        Raised if an invalid aggregation frequency is provided.
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
    Returns a pandas DataFrame with count distribution for each unique value in specified columns, aggregated by frequency.

    Parameters
    -------
    data : pandas.DataFrame
        Input dataframe with a Timestamp index.
    cols : list
        List of column name(s) for which to compute distribution.
    frequency : str
        Aggregation frequency, either 'daily' or 'weekly'.

    Returns
    -------
    distribution : pandas.DataFrame
        Dataframe with count distribution for specified columns.

    Raises
    -------
    ValueError:
        Raised if a specified column is not present in the input dataframe.
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
    Returns a pandas DataFrame containing rhythm computations for the input data based on specified frequency.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe with a Timestamp index and 'user' column.
    timebin : str
        Time bin for grouping, using pandas frequency string (e.g., '1h', '2h', '4h', '6h').
    cols : list
        List of columns to compute the count distribution for.
    groupby_cols : list
        Columns by which to group the data.
    period : int
        Duration in hours for which rhythm is computed. E.g., 8 weeks would be 8*7*24 hours.
    freq : str
        Sampling frequency, either 'daily' or 'weekly'.

    Steps
    -----
    1. Data alignment based on the given frequency: 
        - 'daily' starts at the first 00 hour.
        - 'weekly' starts at the first Monday 00 hour.
    2. Resample data based on the given timebin.
    3. Aggregate columns by summing values within each bin.
    4. Normalize data to compute bin's percentage contribution to the total.

    Returns
    -------
    rhythms : pandas.DataFrame
        Dataframe detailing call count distribution rhythms.

    Raises
    ------
    ValueError:
        If provided frequency is incorrect or a specified column isn't in the dataframe.
    """

    # Check if index is a DateTime index
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("The input DataFrame must have a DateTime index.")

    aligned_df = _align_data(df, period=period, freq=freq)

    resampled_df = aligned_df.groupby(groupby_cols).resample(timebin, include_groups=False).sum().reset_index(level=0) # keep time index
    
    agg_data = _aggregate(resampled_df, groupby_cols=groupby_cols, freq=freq)
    
    rhythms = _compute_distribution(agg_data, cols=cols, groupby_cols=groupby_cols, freq=freq)

    return rhythms


def rhythm(
        df,
        period = "4W",
        freq = "1W",
        bin = "1D",
        cols= [],
        groupby_cols= None,
    ):
    """
    Compute rhythms from the input data.

    - Resample data to the given frequency.
    - Aggregate data to the specified period.
    - Compute the distribution over the frequency for the specified columns.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe with a Timestamp index.

    period : str
        Period for which to compute the rhythm. Default is 'M' for monthly.

    freq : str
        Frequency for the rhythm. Default is 'W' for weekly.

    bin : str
        Time bin for the rhythm computation. Defaults to 'D' for daily.
    
    cols : list
        List of columns to compute the count distribution for.
    
    groupby_cols : list
        Columns by which to group the data. Defaults to user and device
    
    Returns
    -------
    rhythms : pandas.DataFrame
        Dataframe detailing rhythms.
    """

    if groupby_cols is None:
        groupby_cols = ["user", "device"]
        groupby_cols = [col for col in groupby_cols if col in df.columns]

    df = df[groupby_cols+cols]

    # if column type is not numeric, use count, otherwise sum
    for col in cols:
        if df[col].dtype == 'object':
            df[col] = 1

    df = df.groupby(groupby_cols).resample(bin, include_groups=False).sum()
    df.reset_index(groupby_cols, inplace=True)
    
    freq_in_bins = pd.to_timedelta(freq) // pd.to_timedelta(bin)
    period_in_bins = pd.to_timedelta(period) // pd.to_timedelta(bin)

    def _get_bin_index(df):
        df = df.reset_index()
        df["bin"] = df.index % period_in_bins
        df = df.set_index("index")
        return df

    df = df.groupby(groupby_cols).apply(_get_bin_index, include_groups=False)
    df.reset_index(groupby_cols, inplace=True)
    
    df = df.groupby(groupby_cols+["bin"]).sum()
    df.reset_index(groupby_cols, inplace=True)

    df["freq"] = df.index // freq_in_bins
    freq_sum = df.groupby(groupby_cols+["freq"], as_index=False).sum()
    df = pd.merge(df, freq_sum, on=groupby_cols+["freq"], how="left", suffixes=('', '_sum'))
    for col in cols:
        df[col+"_rhythm"] = df[col] / df[col+"_sum"]
        df.fillna(0, inplace=True)
        df.drop(columns=[col, col+"_sum"], inplace=True)
    df.drop(columns=["freq"], inplace=True)
    return df

