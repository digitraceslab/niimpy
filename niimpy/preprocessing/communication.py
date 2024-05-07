import pandas as pd
import warnings

group_by_columns = set(["user", "device"])

def group_data(df):
    """ Group the dataframe by a standard set of columns listed in
    group_by_columns."""
    columns = list(group_by_columns & set(df.columns))
    return df.groupby(columns)


def reset_groups(df):
    """ Group the dataframe by a standard set of columns listed in
    group_by_columns."""
    columns = list(group_by_columns & set(df.index.names))
    return df.reset_index(columns)


def _distribution(df, col_name = None, time_interval="d", bin_interval="h"):
    """ Calculates the distribution data entries over a time interval.

    If a col_name is provided, data is filtered to remove any NaN values in that
    column. Otherwise all rows are considered.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame

    col_name: str
        If provided, filter out NaN values in this column.
        If no column name is provided, all rows are considered valid.

    time_interval: str
        Time interval to calculate the distribution over.

    bin_interval: str
        The size of a single bin in the distribution.

    Returns
    -------
    result: dataframe
        DataFrame containing a distribution column.
    """
    assert isinstance(df, pd.DataFrame), "df_u is not a pandas dataframe"
    assert pd.to_timedelta(bin_interval) < pd.to_timedelta(time_interval), "bin interval must be smaller than time interval"

    if col_name is not None:
        df = df[~df[col_name].isna()]

    if len(df) == 0:
        return pd.DataFrame()
    
    bins = df[col_name].resample(bin_interval).count()
    sums = bins.resample(time_interval).sum()
    df = pd.concat([bins, sums], axis=1, keys=["bin", "sum"])

    # Fill in missing time intervals
    complete_time_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq=bin_interval)
    df = df.reindex(complete_time_range)
    df["bin"] = df["bin"].fillna(0)
    df["sum"] = df["sum"].ffill()

    df["distribution"] = df["bin"] / df["sum"]
    df.drop(columns=["bin", "sum"], inplace=True)

    return df



def call_duration_total(df, config={}):  
    """ This function returns the total duration of each call type, within the 
    specified timeframe. The call types are incoming, outgoing, and missed. If 
    there is no specified timeframe, the function sets a 30 min default time 
    window. The function aggregates this number by user, by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    config: dict
        Dictionary keys containing optional arguments for the computation of features.
        Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(config, dict), "config is not a dictionary"
    
    col_name = config.get("communication_column_name", "call_duration")
    call_type_column = config.get("call_type_column", "call_type")
    config["resample_args"] = config.get("resample_args", {"rule":"30min"}) 
    
    if col_name not in df.columns:
        return pd.DataFrame()
    if call_type_column not in df.columns:
        return pd.DataFrame()
    
    df[col_name]=pd.to_numeric(df[col_name])
    
    if len(df)>0:
        outgoing = group_data(df[df[call_type_column]=="outgoing"])[col_name].resample(**config["resample_args"]).sum()
        outgoing.rename("outgoing_duration_total", inplace=True)
        incoming = group_data(df[df[call_type_column]=="incoming"])[col_name].resample(**config["resample_args"]).sum()
        incoming.rename("incoming_duration_total", inplace=True)
        missed = group_data(df[df[call_type_column]=="missed"])[col_name].resample(**config["resample_args"]).sum()
        missed.rename("missed_duration_total", inplace=True)
        result = pd.concat([outgoing, incoming, missed], axis=1)
        result.fillna(0, inplace=True)
        result = reset_groups(result)
    return result
    

def call_duration_mean(df, config={}):
    """ This function returns the average duration of each call type, within the 
    specified timeframe. The call types are incoming, outgoing, and missed. If 
    there is no specified timeframe, the function sets a 30 min default time 
    window. The function aggregates this number by user, by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    config: dict
        Dictionary keys containing optional arguments for the computation of features.
        Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(config, dict), "config is not a dictionary"
    
    col_name = config.get("communication_column_name", "call_duration")
    call_type_column = config.get("call_type_column", "call_type")
    config["resample_args"] = config.get("resample_args", {"rule":"30min"}) 
    
    if col_name not in df.columns:
        return pd.DataFrame()
    if call_type_column not in df.columns:
        return pd.DataFrame()
        
    df[col_name]=pd.to_numeric(df[col_name])
    
    if len(df)>0:
        outgoing = group_data(df[df[call_type_column]=="outgoing"])[col_name].resample(**config["resample_args"]).mean()
        outgoing.rename("outgoing_duration_mean", inplace=True)
        incoming = group_data(df[df[call_type_column]=="incoming"])[col_name].resample(**config["resample_args"]).mean()
        incoming.rename("incoming_duration_mean", inplace=True)
        missed = group_data(df[df[call_type_column]=="missed"])[col_name].resample(**config["resample_args"]).mean()
        missed.rename("missed_duration_mean", inplace=True)
        result = pd.concat([outgoing, incoming, missed], axis=1)
        result.fillna(0, inplace=True)
        result = reset_groups(result)
    return result


def call_duration_median(df, config={}):
    """ This function returns the median duration of each call type, within the 
    specified timeframe. The call types are incoming, outgoing, and missed. If 
    there is no specified timeframe, the function sets a 30 min default time 
    window. The function aggregates this number by user, by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information
    config: dict
        Dictionary keys containing optional arguments for the computation of features.
        Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(config, dict), "config is not a dictionary"
    
    col_name = config.get("communication_column_name", "call_duration")
    call_type_column = config.get("call_type_column", "call_type")
    config["resample_args"] = config.get("resample_args", {"rule":"30min"}) 
    
    if col_name not in df.columns:
        return pd.DataFrame()
    if call_type_column not in df.columns:
        return pd.DataFrame()
        
    df[col_name]=pd.to_numeric(df[col_name])
    
    if len(df)>0:
        outgoing = group_data(df[df[call_type_column]=="outgoing"])[col_name].resample(**config["resample_args"]).median()
        outgoing.rename("outgoing_duration_median", inplace=True)
        incoming = group_data(df[df[call_type_column]=="incoming"])[col_name].resample(**config["resample_args"]).median()
        incoming.rename("incoming_duration_median", inplace=True)
        missed = group_data(df[df[call_type_column]=="missed"])[col_name].resample(**config["resample_args"]).median()
        missed.rename("missed_duration_median", inplace=True)
        result = pd.concat([outgoing, incoming, missed], axis=1)
        result.fillna(0, inplace=True)
        result = reset_groups(result)
    return result


def call_duration_std(df, config={}):
    """ This function returns the standard deviation of the duration of each 
    call type, within the specified timeframe. The call types are incoming, 
    outgoing, and missed. If there is no specified timeframe, the function sets 
    a 30 min default time window. The function aggregates this number by user, 
    by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    config: dict
        Dictionary keys containing optional arguments for the computation of features.
        Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(config, dict), "config is not a dictionary"
    
    col_name = config.get("communication_column_name", "call_duration")
    call_type_column = config.get("call_type_column", "call_type")
    config["resample_args"] = config.get("resample_args", {"rule":"30min"}) 
    
    if col_name not in df.columns:
        return pd.DataFrame()
    if call_type_column not in df.columns:
        return pd.DataFrame()
        
    df[col_name]=pd.to_numeric(df[col_name])
    
    if len(df)>0:
        outgoing = group_data(df[df[call_type_column]=="outgoing"])[col_name].resample(**config["resample_args"]).std()
        outgoing.rename("outgoing_duration_std", inplace=True)
        incoming = group_data(df[df[call_type_column]=="incoming"])[col_name].resample(**config["resample_args"]).std()
        incoming.rename("incoming_duration_std", inplace=True)
        missed = group_data(df[df[call_type_column]=="missed"])[col_name].resample(**config["resample_args"]).std()
        missed.rename("missed_duration_std", inplace=True)
        result = pd.concat([outgoing, incoming, missed], axis=1)
        result.fillna(0, inplace=True)
        result = reset_groups(result)
    return result


def call_count(df, config={}):
    """ This function returns the number of times, within the specified timeframe, 
    when a call has been received, missed, or initiated. If there is no specified 
    timeframe, the function sets a 30 min default time window. The function 
    aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    config: dict
        Dictionary keys containing optional arguments for the computation of features.
        Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(config, dict), "config is not a dictionary"
    
    col_name = config.get("communication_column_name", "call_duration")
    call_type_column = config.get("call_type_column", "call_type")
    config["resample_args"] = config.get("resample_args", {"rule":"30min"}) 
    
    if col_name not in df.columns:
        return pd.DataFrame()
    if call_type_column not in df.columns:
        return pd.DataFrame()
            
    if len(df)>0:
        outgoing = group_data(df[df[call_type_column]=="outgoing"])[col_name].resample(**config["resample_args"]).count()
        outgoing.rename("outgoing_count", inplace=True)
        incoming = group_data(df[df[call_type_column]=="incoming"])[col_name].resample(**config["resample_args"]).count()
        incoming.rename("incoming_count", inplace=True)
        missed = group_data(df[df[call_type_column]=="missed"])[col_name].resample(**config["resample_args"]).count()
        missed.rename("missed_count", inplace=True)
        result = pd.concat([outgoing, incoming, missed], axis=1)
        result.fillna(0, inplace=True)
        result = reset_groups(result)
    return result


def call_outgoing_incoming_ratio(df, config={}):
    """ This function returns the ratio of outgoing calls over incoming calls, 
    within the specified timeframe. If there is no specified timeframe,
    the function sets a 30 min default time window. The function aggregates this number 
    by user, by timewindow.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    config: dict
        Dictionary keys containing optional arguments for the computation of features.
        Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(config, dict), "config is not a dictionary"
    
    col_name = config.get("communication_column_name", "call_type")
    call_type_column = config.get("call_type_column", "call_type")
    config["resample_args"] = config.get("resample_args", {"rule":"30min"}) 
    
    if col_name not in df.columns:
        return pd.DataFrame()
    if call_type_column not in df.columns:
        return pd.DataFrame()
        
    df2 = call_count(df, config)
    df2 = df2.set_index(list(group_by_columns & set(df2.columns)), append=True)
    df2["outgoing_incoming_ratio"] = df2["outgoing_count"]/df2["incoming_count"]
    df2 = df2["outgoing_incoming_ratio"]
    df2.fillna(0, inplace=True)
    result = df2.to_frame(name='outgoing_incoming_ratio')
    result = reset_groups(result)
    return result


def call_distribution(df, config={}):
    """ Calculates the distribution of calls sent and received over a time
    interval. The function first aggregates the number of calls over a
    shorter time interval, the bins, and then calculates the distribution of
    the message count over a longer interval, the time window.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame

    config: dict
        Dictionary keys containing optional arguments for the computation of features.
        Keys can be column names, other dictionaries, etc.

        This function accepts col_name (default "call_type"), a time interval
        (default 1d) and a bin interval (default 1h).

    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(config, dict), "config is not a dictionary"

    col_name = config.get("col_name", "call_type")
    time_interval = config.get("time interval", "1d")
    bin_interval = config.get("bin interval", "1h")

    if col_name not in df.columns:
        return pd.DataFrame()

    df = group_data(df).apply(
        lambda x: _distribution(x, col_name, time_interval, bin_interval),
        include_groups=False
    )
    df = reset_groups(df)

    return df


def message_count(df, config={}):
    """ This function returns the number of times, within the specified timeframe, 
    when an SMS has been sent/received. If there is no specified timeframe,
    the function sets a 30 min default time window. The function aggregates this number 
    by user, by timewindow.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    config: dict
        Dictionary keys containing optional arguments for the computation of features.
        Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about 
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(config, dict), "config is not a dictionary"
    
    col_name = config.get("communication_column_name", "message_type")
    message_type = config.get("message_type_column", "message_type")
    config["resample_args"] = config.get("resample_args", {"rule":"30min"}) 
    
    if col_name not in df.columns:
        return pd.DataFrame()
    if message_type not in df.columns:
        return pd.DataFrame()

    if len(df)>0:
        outgoing = group_data(df[df[message_type]=="outgoing"])[col_name].resample(**config["resample_args"]).count()
        outgoing.rename("outgoing_count", inplace=True)
        incoming = group_data(df[df[message_type]=="incoming"])[col_name].resample(**config["resample_args"]).count()
        incoming.rename("incoming_count", inplace=True)
        result = pd.concat([outgoing, incoming], axis=1)
        result.fillna(0, inplace=True)
        result = reset_groups(result)
        return result
    return pd.DataFrame()


def message_outgoing_incoming_ratio(df, config={}):
    """ This function returns the ratio of outgoing messages over incoming
    messages, within the specified timeframe. If there is no specified timeframe,
    the function sets a 30 min default time window. The function aggregates this number
    by user, by timewindow.

    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    config: dict
        Dictionary keys containing optional arguments for the computation of features.
        Keys can be column names, other dictionaries, etc. The functions
        needs the column name where the data is stored; if none is given, the default
        name employed by Aware Framework will be used. To include information about
        the resampling window, please include the selected parameters from
        pandas.DataFrame.resample in a dictionary called resample_args.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(config, dict), "config is not a dictionary"

    col_name = config.get("communication_column_name", "message_type")
    message_type = config.get("message_type_column", "message_type")
    config["resample_args"] = config.get("resample_args", {"rule":"30min"})
    
    if col_name not in df.columns:
        return pd.DataFrame()
    if message_type not in df.columns:
        return pd.DataFrame()

    df2 = message_count(df, config)
    df2 = df2.set_index(list(group_by_columns & set(df2.columns)), append=True)
    df2["outgoing_incoming_ratio"] = df2["outgoing_count"]/df2["incoming_count"]
    df2 = df2["outgoing_incoming_ratio"]
    df2.fillna(0, inplace=True)
    result = df2.to_frame(name='outgoing_incoming_ratio')
    result = reset_groups(result)

    return result


def message_distribution(df, config={}):
    """ Calculates the distribution of messages sent and received over a time
    interval. The function first aggregates the number of messages over a
    shorter time interval, the bins, and then calculates the distribution of
    the message count over a longer interval, the time window.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame

    config: dict
        Dictionary keys containing optional arguments for the computation of features.
        Keys can be column names, other dictionaries, etc.

        This function accepts col_name, a time interval
        (default 1d) and a bin interval (default 1h).

        if col_name is given, the data is first filtered to remove NaN values in that
        column.

    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(config, dict), "config is not a dictionary"

    col_name = config.get("col_name", "message_type")
    time_interval = config.get("time interval", "1d")
    bin_interval = config.get("bin interval", "1h")

    if col_name not in df.columns:
        return pd.DataFrame()

    df = group_data(df).apply(
        lambda x: _distribution(x, col_name, time_interval, bin_interval),
        include_groups=False
    )
    df = reset_groups(df)
    return df


CALL_FEATURES = [globals()[name] for name in globals() if name.startswith('call_')]
CALL_FEATURES = {x: {} for x in CALL_FEATURES}

MESSAGE_FEATURES = [globals()[name] for name in globals() if name.startswith('message_')]
MESSAGE_FEATURES = {x: {} for x in MESSAGE_FEATURES}


def extract_features_comms(df, features=None):
    """ This function computes and organizes the selected features for calls 
    and SMS events. The function aggregates the features by user, by time window. 
    If no time window is specified, it will automatically aggregate the features 
    in 30 mins non-overlapping windows. 
    
    The complete list of features that can be calculated are: call_duration_total,
    call_duration_mean, call_duration_median, call_duration_std, call_count,
    call_outgoing_incoming_ratio, sms_count
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    features: dict, optional
        Dictionary keys contain the names of the features to compute. 
        If none is given, all features will be computed.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    
    if features is None:
        features = dict(CALL_FEATURES)
        for k, i in MESSAGE_FEATURES.items():
            features[k] = i
    else:
        assert isinstance(features, dict), "Please input the features as a dictionary"
    
    computed_features = []
    for feature, feature_arg in features.items():
        print(f'computing {feature}...')
        computed_feature = feature(df, feature_arg)
        index_by = list(group_by_columns & set(computed_feature.columns))
        computed_feature = computed_feature.set_index(index_by, append=True)
        computed_features.append(computed_feature)
        
    computed_features = pd.concat(computed_features, axis=1)
    computed_features = reset_groups(computed_features)
    return computed_features
