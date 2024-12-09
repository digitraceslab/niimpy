import pandas as pd
from niimpy.preprocessing import util

group_by_columns = ["user", "device"]


def step_summary(df, value_col='values', user_id=None, start_date=None, end_date=None):
    # value_col='values', user_id=None, start_date=None, end_date=None):
    """Return the summary of step count in a time range. The summary includes the following information
    of step count per day: mean, standard deviation, min, max

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing the hourly step count of an individual. The dataframe must be date time index.
    config: dict, optional
        Dictionary keys containing optional arguments. These can be:

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

    df['month'] = df.index.month
    df['day'] = df.index.day

    # Calculate sum of steps for each date
    df['daily_sum'] = util.group_data( df,
        ['day', 'month']
    )[value_col].transform('sum')

    # Under the assumption that a user cannot have zero steps per day, we remove rows where daily_sum are zero
    df = df[~(df.daily_sum == 0)]

    summary_df = pd.DataFrame()
    
    summary_df['median_sum_step'] = util.group_data(df)['daily_sum'].median()
    summary_df['avg_sum_step'] = util.group_data(df)['daily_sum'].mean()
    summary_df['std_sum_step'] = util.group_data(df)['daily_sum'].std()
    summary_df['min_sum_step'] = util.group_data(df)['daily_sum'].min()
    summary_df['max_sum_step'] = util.group_data(df)['daily_sum'].max()

    summary_df = util.reset_groups(summary_df)
    summary_df = util.select_columns(summary_df, 
        ["median_sum_step", "avg_sum_step", "std_sum_step", "min_sum_step", "max_sum_step"]
    )
    return summary_df


def tracker_step_distribution(steps_df, steps_column='steps', resample_args={'rule': 'h'}, timeframe='d', **kwargs):
    """Return distribution of steps within a time range.
    The number of step is sampled according to the frequency rule in resample_args.
    This is divided by the total number of steps in a larger time frame, given by
    the timeframe argument.

    Using default parameters produces a daily step distribution.

    Parameters
    ----------
    steps_df : Pandas Dataframe
        Dataframe the step distribution of each individual.
    config: dict, optional
        Dictionary keys containing optional arguments. These can be:

        steps_column: str. Optional
            Column contains step values. Default value is "steps".
        resample_args: dict. Optional
            Dictionary containing the resample arguments. Default value is {'rule': 'h'}.
        timeframe: string. Optional
            Time frame used for computing the distribution. Default value is 'D'.
        
    Returns
    -------
    df: pandas DataFrame
        A dataframe containing the distribution of step count.
    """
    assert isinstance(steps_df, pd.DataFrame), "df_u is not a pandas dataframe"

    # time frame must be longer than resample_args["rule"]
    to_offset = pd.tseries.frequencies.to_offset
    if to_offset(timeframe) <= to_offset(resample_args["rule"]):
        raise ValueError("Time frame must be longer than resample rule")

    # Extract date and time columns from timestamp
    df = steps_df.copy()

    # Remove duplicates
    df = df.drop_duplicates(subset=['user', 'date', 'time'], keep='last')

    # Convert the absolute values into distribution. This can be understood as the
    # portion of steps the users took during each hour
    steps = df.groupby(["user"]).resample(**resample_args, include_groups=False).agg({steps_column: 'sum'})
    step_sum = steps.reset_index(["user"]).groupby(["user"]).resample(timeframe).agg({steps_column: 'sum'})

    steps["step_sum"] = step_sum[steps_column]
    # fill down
    steps["step_sum"] = steps["step_sum"].ffill()

    # Divide hourly steps by daily sum to get the distribution
    steps['step_distribution'] = steps[steps_column] / steps['step_sum']

    # Set index and select columns
    steps = util.select_columns(steps, ["step_distribution", "step_sum"])
    return steps[["step_distribution", "step_sum"]]


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
    for feature_function, kwargs in features.items():
        print(features, kwargs)
        computed_feature = feature_function(df, **kwargs)
        index_by = list(set(group_by_columns) & set(computed_feature.columns))
        computed_feature = computed_feature.set_index(index_by, append=True)
        computed_features.append(computed_feature)

    computed_features = pd.concat(computed_features, axis=1)

    if 'group' in df:
        computed_features['group'] = df.groupby('user')['group'].first()

    computed_features = util.reset_groups(computed_features)
    return computed_features

