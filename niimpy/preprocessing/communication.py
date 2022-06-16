import pandas as pd

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
        features = [key for key in globals().keys() if key.startswith('audio_')]
        features = {x: {} for x in features}
    else:
        assert isinstance(features, dict), "Please input the features as a dictionary"
    
    computed_features = []
    for feature, feature_arg in features.items():
        print(f'computing {feature}...')
        command = f'{feature}(df,feature_functions=feature_arg)'
        computed_feature = eval(command)
        computed_features.append(computed_feature)
        
    computed_features = pd.concat(computed_features, axis=1)
    return computed_features

def call_duration_total(df, feature_functions=None):  
    """ This function returns the total duration of each call type, within the 
    specified timeframe. The call types are incoming, outgoing, and missed. If 
    there is no specified timeframe, the function sets a 30 min default time 
    window. The function aggregates this number by user, by timewindow. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information
    feature_functions: dict, optional
        The feature functions can be set according to the pandas.DataFrame.resample
        function.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T' #Set the default value of aggregation to 30 mins
        
    df['call_duration']=pd.to_numeric(df['call_duration'])
    
    if len(df)>0:
        outgoing = df[df.call_type=="outgoing"].groupby("user")["call_duration"].resample(**feature_functions).sum()
        outgoing.rename("outgoing_duration", inplace=True)
        incoming = df[df.call_type=="incoming"].groupby("user")["call_duration"].resample(**feature_functions).sum()
        incoming.rename("incoming_duration", inplace=True)
        missed = df[df.call_type=="missed"].groupby("user")["call_duration"].resample(**feature_functions).sum()
        missed.rename("missed_duration", inplace=True)
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
    bat: pandas.DataFrame
        Dataframe with the battery information
    feature_functions: dict, optional
        The feature functions can be set according to the pandas.DataFrame.resample
        function.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T' #Set the default value of aggregation to 30 mins
        
    df['call_duration']=pd.to_numeric(df['call_duration'])
    
    if len(df)>0:
        outgoing = df[df.call_type=="outgoing"].groupby("user")["call_duration"].resample(**feature_functions).mean()
        outgoing.rename("outgoing_duration", inplace=True)
        incoming = df[df.call_type=="incoming"].groupby("user")["call_duration"].resample(**feature_functions).mean()
        incoming.rename("incoming_duration", inplace=True)
        missed = df[df.call_type=="missed"].groupby("user")["call_duration"].resample(**feature_functions).mean()
        missed.rename("missed_duration", inplace=True)
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
    feature_functions: dict, optional
        The feature functions can be set according to the pandas.DataFrame.resample
        function.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T' #Set the default value of aggregation to 30 mins
        
    df['call_duration']=pd.to_numeric(df['call_duration'])
    
    if len(df)>0:
        outgoing = df[df.call_type=="outgoing"].groupby("user")["call_duration"].resample(**feature_functions).median()
        outgoing.rename("outgoing_duration", inplace=True)
        incoming = df[df.call_type=="incoming"].groupby("user")["call_duration"].resample(**feature_functions).median()
        incoming.rename("incoming_duration", inplace=True)
        missed = df[df.call_type=="missed"].groupby("user")["call_duration"].resample(**feature_functions).median()
        missed.rename("missed_duration", inplace=True)
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
    bat: pandas.DataFrame
        Dataframe with the battery information
    feature_functions: dict, optional
        The feature functions can be set according to the pandas.DataFrame.resample
        function.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T' #Set the default value of aggregation to 30 mins
        
    df['call_duration']=pd.to_numeric(df['call_duration'])
    
    if len(df)>0:
        outgoing = df[df.call_type=="outgoing"].groupby("user")["call_duration"].resample(**feature_functions).std()
        outgoing.rename("outgoing_duration", inplace=True)
        incoming = df[df.call_type=="incoming"].groupby("user")["call_duration"].resample(**feature_functions).std()
        incoming.rename("incoming_duration", inplace=True)
        missed = df[df.call_type=="missed"].groupby("user")["call_duration"].resample(**feature_functions).std()
        missed.rename("missed_duration", inplace=True)
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
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict, optional
        The feature functions can be set according to the pandas.DataFrame.resample
        function.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T' #Set the default value of aggregation to 30 mins
        
    df['call_duration']=pd.to_numeric(df['call_duration'])
    
    if len(df)>0:
        outgoing = df[df.call_type=="outgoing"].groupby("user")["call_duration"].resample(**feature_functions).count()
        outgoing.rename("outgoing_count", inplace=True)
        incoming = df[df.call_type=="incoming"].groupby("user")["call_duration"].resample(**feature_functions).count()
        incoming.rename("incoming_count", inplace=True)
        missed = df[df.call_type=="missed"].groupby("user")["call_duration"].resample(**feature_functions).count()
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
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict, optional
        The feature functions can be set according to the pandas.DataFrame.resample
        function.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T' #Set the default value of aggregation to 30 mins
        
    df2 = call_count(df, feature_functions=None)
    df2["outgoing_incoming_ratio"] = df2["outgoing_count"]/df2["incoming_count"]
    df2.drop(["outgoing_count", "incoming_count", "missed_count"], axis=1, inplace=True)
    df2.fillna(0, inplace=True)
    
    return result

def sms_count(df, feature_functions=None):
    """ This function returns the number of times, within the specified timeframe, 
    when an SMS has been sent/received. If there is no specified timeframe,
    the function sets a 30 min default time window. The function aggregates this number 
    by user, by timewindow.
    
    Parameters
    ----------
    df_u: pandas.DataFrame
        Input data frame
    feature_functions: dict, optional
        The feature functions can be set according to the pandas.DataFrame.resample
        function.
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T' #Set the default value of aggregation to 30 mins
        
    outgoing = df[df.message_type=="outgoing"].groupby("user")["message_type"].resample(**feature_functions).count()
    outgoing.rename("outgoing_count", inplace=True)
    incoming = df[df.message_type=="incoming"].groupby("user")["message_type"].resample(**feature_functions).count()
    incoming.rename("incoming_count", inplace=True)
    result = pd.concat([outgoing, incoming], axis=1)
    result.fillna(0, inplace=True)
    
    return result