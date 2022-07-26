import pandas as pd

def call_duration_total(df, feature_functions=None):  
    """ This function returns the total duration of each call type, within the 
    specified timeframe. The call types are incoming, outgoing, and missed. If 
    there is no specified timeframe, the function sets a 30 min default time 
    window. The function aggregates this number by user, by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    feature_functions: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "communication_column_name" in feature_functions:
        col_name = "call_duration"
    else:
        col_name = feature_functions["communication_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
        
    df[col_name]=pd.to_numeric(df[col_name])
    
    if len(df)>0:
        outgoing = df[df.call_type=="outgoing"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).sum()
        outgoing.rename("outgoing_duration_total", inplace=True)
        incoming = df[df.call_type=="incoming"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).sum()
        incoming.rename("incoming_duration_total", inplace=True)
        missed = df[df.call_type=="missed"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).sum()
        missed.rename("missed_duration_total", inplace=True)
        result = pd.concat([outgoing, incoming, missed], axis=1)
        result.fillna(0, inplace=True)
    return result
    
def call_duration_mean(df, feature_functions=None):
    """ This function returns the average duration of each call type, within the 
    specified timeframe. The call types are incoming, outgoing, and missed. If 
    there is no specified timeframe, the function sets a 30 min default time 
    window. The function aggregates this number by user, by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    feature_functions: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "communication_column_name" in feature_functions:
        col_name = "call_duration"
    else:
        col_name = feature_functions["communication_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
        
    df[col_name]=pd.to_numeric(df[col_name])
    
    if len(df)>0:
        outgoing = df[df.call_type=="outgoing"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).mean()
        outgoing.rename("outgoing_duration_mean", inplace=True)
        incoming = df[df.call_type=="incoming"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).mean()
        incoming.rename("incoming_duration_mean", inplace=True)
        missed = df[df.call_type=="missed"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).mean()
        missed.rename("missed_duration_mean", inplace=True)
        result = pd.concat([outgoing, incoming, missed], axis=1)
        result.fillna(0, inplace=True)
    return result

def call_duration_median(df, feature_functions=None):
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
    feature_functions: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "communication_column_name" in feature_functions:
        col_name = "call_duration"
    else:
        col_name = feature_functions["communication_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
        
    df[col_name]=pd.to_numeric(df[col_name])
    
    if len(df)>0:
        outgoing = df[df.call_type=="outgoing"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).median()
        outgoing.rename("outgoing_duration_median", inplace=True)
        incoming = df[df.call_type=="incoming"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).median()
        incoming.rename("incoming_duration_median", inplace=True)
        missed = df[df.call_type=="missed"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).median()
        missed.rename("missed_duration_median", inplace=True)
        result = pd.concat([outgoing, incoming, missed], axis=1)
        result.fillna(0, inplace=True)
    return result

def call_duration_std(df, feature_functions=None):
    """ This function returns the standard deviation of the duration of each 
    call type, within the specified timeframe. The call types are incoming, 
    outgoing, and missed. If there is no specified timeframe, the function sets 
    a 30 min default time window. The function aggregates this number by user, 
    by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    feature_functions: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "communication_column_name" in feature_functions:
        col_name = "call_duration"
    else:
        col_name = feature_functions["communication_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
        
    df[col_name]=pd.to_numeric(df[col_name])
    
    if len(df)>0:
        outgoing = df[df.call_type=="outgoing"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).std()
        outgoing.rename("outgoing_duration_std", inplace=True)
        incoming = df[df.call_type=="incoming"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).std()
        incoming.rename("incoming_duration_std", inplace=True)
        missed = df[df.call_type=="missed"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).std()
        missed.rename("missed_duration_std", inplace=True)
        result = pd.concat([outgoing, incoming, missed], axis=1)
        result.fillna(0, inplace=True)
    return result

def call_count(df, feature_functions=None):
    """ This function returns the number of times, within the specified timeframe, 
    when a call has been received, missed, or initiated. If there is no specified 
    timeframe, the function sets a 30 min default time window. The function 
    aggregates this number by user, by timewindow.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    feature_functions: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "communication_column_name" in feature_functions:
        col_name = "call_duration"
    else:
        col_name = feature_functions["communication_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
        
    df[col_name]=pd.to_numeric(df[col_name])
    
    if len(df)>0:
        outgoing = df[df.call_type=="outgoing"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).count()
        outgoing.rename("outgoing_count", inplace=True)
        incoming = df[df.call_type=="incoming"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).count()
        incoming.rename("incoming_count", inplace=True)
        missed = df[df.call_type=="missed"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).count()
        missed.rename("missed_count", inplace=True)
        result = pd.concat([outgoing, incoming, missed], axis=1)
        result.fillna(0, inplace=True)
    return result

def call_outgoing_incoming_ratio(df, feature_functions=None):
    """ This function returns the ratio of outgoing calls over incoming calls, 
    within the specified timeframe. If there is no specified timeframe,
    the function sets a 30 min default time window. The function aggregates this number 
    by user, by timewindow.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    feature_functions: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "communication_column_name" in feature_functions:
        col_name = "call_duration"
    else:
        col_name = feature_functions["communication_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
        
    df2 = call_count(df, feature_functions)
    df2["outgoing_incoming_ratio"] = df2["outgoing_count"]/df2["incoming_count"]
    df2 = df2["outgoing_incoming_ratio"]
    df2.fillna(0, inplace=True)
    result = df2.to_frame(name='outgoing_incoming_ratio')
    
    return result

def sms_count(df, feature_functions=None):
    """ This function returns the number of times, within the specified timeframe, 
    when an SMS has been sent/received. If there is no specified timeframe,
    the function sets a 30 min default time window. The function aggregates this number 
    by user, by timewindow.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    feature_functions: dict
        Dictionary keys containing optional arguments for the computation of scrren
        information. Keys can be column names, other dictionaries, etc. The functions
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
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "communication_column_name" in feature_functions:
        col_name = "message_type"
    else:
        col_name = feature_functions["communication_column_name"]
    if not "resample_args" in feature_functions.keys():
        feature_functions["resample_args"] = {"rule":"30T"}
        
    outgoing = df[df.message_type=="outgoing"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).count()
    outgoing.rename("outgoing_count", inplace=True)
    incoming = df[df.message_type=="incoming"].groupby("user")[col_name].resample(**feature_functions["resample_args"]).count()
    incoming.rename("incoming_count", inplace=True)
    result = pd.concat([outgoing, incoming], axis=1)
    result.fillna(0, inplace=True)
    
    return result

ALL_FEATURE_FUNCTIONS = [globals()[name] for name in globals() if name.startswith('call_')]
ALL_FEATURE_FUNCTIONS = {x: {} for x in ALL_FEATURE_FUNCTIONS}

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
        features = ALL_FEATURE_FUNCTIONS
    else:
        assert isinstance(features, dict), "Please input the features as a dictionary"
    
    computed_features = []
    for feature, feature_arg in features.items():
        print(f'computing {feature}...')
        computed_feature = feature(df, feature_arg)
        computed_features.append(computed_feature)
        
    computed_features = pd.concat(computed_features, axis=1)
    return computed_features
