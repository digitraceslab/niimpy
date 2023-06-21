import pandas as pd


def step_summary(df, value_col='values', user_id=None, start_date=None, end_date=None):
    """Return the summary of step count in a time range. The summary includes the following information
    of step count per day: mean, standard deviation, min, max

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

    if user_id is not None:
        assert isinstance(user_id, list), 'User id must be a list'
        df = df[df['user'] in user_id]

    if start_date is not None and end_date is not None:
        df = df[start_date:end_date]
    elif start_date is None and end_date is not None:
        df = df[:end_date]
    elif start_date is not None and end_date is None:
        df = df[start_date:]

    # Calculate sum of step
    df['daily_sum'] = df.groupby(by=[df.index.day, df.index.month, 'user'])[value_col].transform(
        'sum')  # stores sum of daily step

    # Under the assumption that a user cannot have zero steps per day, we remove rows where daily_sum are zero
    df = df[~(df.daily_sum == 0)]

    summary_df = pd.DataFrame()
    summary_df['median_sum_step'] = df.groupby('user')['daily_sum'].median()
    summary_df['avg_sum_step'] = df.groupby('user')['daily_sum'].mean()
    summary_df['std_sum_step'] = df.groupby('user')['daily_sum'].std()
    summary_df['min_sum_step'] = df.groupby('user')['daily_sum'].min()
    summary_df['max_sum_step'] = df.groupby('user')['daily_sum'].max()

    return summary_df.reset_index()


def tracker_daily_step_distribution(steps_df):
    """Return distribution of steps within each day. 
    Assuming the step count is recorded at hourly resolution, this function will compute
    the contribution of each hourly step count into the daily count (percentage wise).

    Parameters
    ----------
    steps_df : Pandas Dataframe
        Dataframe containing the hourly step count of an individual.
        
    Returns
    -------
    df: pandas DataFrame
        A dataframe containing the distribution of step count per day at hourly resolution.
    """

    # Combine date and time to acquire  timestamp 
    df = steps_df.copy()
    df = df.rename(columns={"subject_id": "user"})  # rename column, to be niimpy-compatible
    df['time'] = pd.to_datetime(df['date'] + ":" + df['time'], format='%Y-%m-%d:%H:%M:%S.%f')

    # Dummy columns for hour, month, day for easier operations later on
    df['hour'] = df.index.hour
    df['month'] = df.index.month
    df['day'] = df.index.day

    # Remove duplicates
    df = df.drop_duplicates(subset=['user', 'date', 'time'], keep='last')

    # Convert the absolute values into distribution. This can be understood as the portion of steps the users took
    # during each hour
    df['daily_sum'] = df.groupby(by=['day', 'month', 'user'])['steps'].transform('sum')  # stores sum of daily step

    # Divide hourly steps by daily sum to get the distribution
    df['daily_distribution'] = df['steps'] / df['daily_sum']

    # Set timestamp index
    #df = df.set_index("time")
    df = df.set_index("user")

    return df


ALL_FEATURES = [globals()[name] for name in globals()
                         if name.startswith('tracker_')]
ALL_FEATURES = {x: {} for x in ALL_FEATURES}

def extract_features_tracker(df, features=None):
    """ This function computes and organizes the selected features for tracker data
        recorded using Polar Ignite.

        The complete list of features that can be calculated are: tracker_daily_step_distribution

        Parameters
        ----------
        df: pandas.DataFrame
            Input data frame
        features: dict, optional
            Dictionary keys contain the names of the features to compute.
            The value of the keys is the list of parameters that will be passed to the function.
            If none is given, all features will be computed.

        Returns
        -------
        result: dataframe
            Resulting dataframe
        """
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"

    computed_features = []
    if features is None:
        features = ALL_FEATURES
    print(ALL_FEATURES)
    for feature_function, kwargs in features.items():
        computed_feature = feature_function(df, **kwargs)
        computed_features.append(computed_feature)


    assert len(computed_features) > 0, "Computed features cannot be empty"
    if len(computed_features) > 1:
        computed_features = pd.concat(computed_features, axis=1)
    else:
        computed_features = computed_features[0]

    if 'group' in df:
        computed_features['group'] = df.groupby('user')['group'].first()

    return computed_features

