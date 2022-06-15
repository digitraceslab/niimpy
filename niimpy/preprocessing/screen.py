import numpy as np
import pandas as pd

import niimpy
from niimpy.preprocessing import battery as b

def screen_util(df, bat):
    """ This function is a helper function for all other screen preprocessing.
    The function has the option to merge information from the battery sensors to
    include data when the phone is shut down. The function also detects the missing 
    datapoints (i.e. not allowed transitions like ON to ON). 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information
    
    Returns
    -------
    df: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    
    df["screen_status"]=pd.to_numeric(df["screen_status"]) #convert to numeric in case it is not

    #Include the missing points that are due to shutting down the phone
    if not bat.empty:
        shutdown = b.shutdown_info(bat)
        shutdown = shutdown.replace([-1,-2],0)
        
        if not shutdown.empty:
            df = pd.concat([df, shutdown])
            df.fillna(0, inplace=True)
            df.drop(['battery_level', 'battery_status', 'battery_health', 'battery_adaptor'], axis=1, inplace=True)

    #Sort the dataframe
    df.sort_values(by=["user","device","datetime"], inplace=True)
    
    #Detect missing data points
    df['missing']=0
    df['next']=df['screen_status'].shift(-1)
    df['dummy']=df['screen_status']-df['next']
    df['missing'] = np.where(df['dummy']==0, 1, 0) #Check the missing points and label them as 1
    df['missing'] = df['missing'].shift(1)
    df.drop(['dummy','next'], axis=1, inplace=True)
    df.fillna(0, inplace=True)
   
    df = df[df.missing == 0] #Discard missing values
    df = df.groupby("user", as_index=False).apply(lambda x: x.iloc[:-1])#Discard transitions between subjects
    df.drop(["missing"], axis=1, inplace=True)
    df = df.droplevel(0)
    return df

def screen_event_classification(df):
    """ This function is a helper function for other screen preprocessing.
    The function classifies the screen events into four transition types: on, 
    off, in use, and undefined, based on the screen events recorded. For example,
    if two consecutive events are 0 and 3, there has been a transition from off
    to unlocked, i.e. the phone has been unlocked and the events will be 
    classified into the "use" transition. 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    
    Returns
    -------
    df: dataframe
        Resulting dataframe
    """    
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    
    #Classify the event 
    df['next'] = df['screen_status'].shift(-1)
    df['next'] = df['screen_status'].astype(int).astype(str)+df['screen_status'].shift(-1).fillna(0).astype(int).astype(str)   
    df = df.groupby("user", as_index=False).apply(lambda x: x.iloc[:-1])#Discard transitions between subjects
    df = df.droplevel(0)
    df["use"] =  df["on"] = df["na"] = df["off"] = 0
    
    df["use"][(df.next=='30') | (df.next=='31') | (df.next=='32')]=1 #in use
    df["on"][(df.next=='10') | (df.next=='12') | (df.next=='13') | (df.next=='20')]=1 #on
    df["na"][(df.next=='21') | (df.next=='23')]=1 #irrelevant. It seems like from 2 to 1 is from off to on (i.e. the screen goes to off and then it locks)
    df["off"][(df.next=='01') | (df.next=='02') | (df.next=='03') | (df.next=='21')]=1 #off
    
    df.drop(columns=["next","screen_status"], inplace=True)   
    
    #Discard the first and last row because they do not have all info. We do not
    #know what happened before or after these points. 
    df = df.groupby("user", as_index=False).apply(lambda x: x.iloc[1:])
    df = df.groupby("user", as_index=False).apply(lambda x: x.iloc[:-1])
    df = df.droplevel(0)
    df = df.droplevel(0)
    return df

def extract_features_screen(df, features=None):
    """ This function computes and organizes the selected features for screen events
    that have been recorded using Aware Framework. The function aggregates the features
    by user, by time window. If no time window is specified, it will automatically aggregate
    the features in 30 mins non-overlapping windows. 
    
    The complete list of features that can be calculated are: screen_off, screen_count,
    screen_duration, screen_duration_min, screen_duration_max, screen_duration_median,
    screen_duration_mean, screen_duration_std, and screen_first_unlock.
    
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
        features = [key for key in globals().keys() if key.startswith('screen_')]
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

def screen_off(df, bat):
    """ This function returns the timestamps, within the specified timeframe, 
    when the screen has turned off. If there is no specified timeframe,
    the function sets a 30 min default time window. The function aggregates this number 
    by user, by timewindow. 
    
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
    df: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    
    df = screen_util(df, bat)
    df = df[df.screen_status == 0] #Select only those OFF events when no missing data is present
    return df

def screen_count(df, bat, feature_functions=None):
    """ This function returns the number of times, within the specified timeframe, 
    when the screen has turned off, turned on, and been in use. If there is no 
    specified timeframe, the function sets a 30 min default time window. The 
    function aggregates this number by user, by timewindow. 
    
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
    df: dataframe
        Resulting dataframe
    """    
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T'
    
    df2 = screen_util(df, bat)
    df2 = screen_event_classification(df2)
    
    if len(df2)>0:
        on = df2.groupby("user")["on"].resample(**feature_functions).sum()
        off = df2.groupby("user")["off"].resample(**feature_functions).sum()
        use = df2.groupby("user")["use"].resample(**feature_functions).sum()
        result = pd.concat([on, off, use], axis=1)
    return result

def screen_duration(df, bat, feature_functions=None):
    """ This function returns the duration of each transition, within the 
    specified timeframe. The transitions are off, on, and in use. If there is no 
    specified timeframe, the function sets a 30 min default time window. The 
    function aggregates this number by user, by timewindow. 
    
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
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T'
    
    df2 = screen_util(df, bat)
    df2 = screen_event_classification(df2)           
    
    df2['duration']=np.nan
    df2['duration']=df2['datetime'].diff()
    df2['duration'] = df2['duration'].shift(-1)
    
    #Discard any datapoints whose duration in “ON” and "IN USE" states are 
    #longer than 10 hours becaus they may be artifacts
    thr = pd.Timedelta('10 hours')
    df2 = df2[~((df2.on==1) & (df2.duration>thr))]
    df2 = df2[~((df2.use==1) & (df2.duration>thr))]
    
    if len(df2)>0:
        on = df2[df2.on==1].groupby("user")["duration"].resample(**feature_functions).sum()
        off = df2[df2.off==1].groupby("user")["duration"].resample(**feature_functions).sum()
        use = df2[df2.use==1].groupby("user")["duration"].resample(**feature_functions).sum()
        result = pd.concat([on, off, use], axis=1)
    return result

def screen_duration_min(df, bat, feature_functions=None):
    """ This function returns the minimum duration of each transition, within the 
    specified timeframe. The transitions are off, on, and in use. If there is no 
    specified timeframe, the function sets a 30 min default time window. The 
    function aggregates this number by user, by timewindow. 
    
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
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T'
    
    df2 = screen_util(df, bat)
    df2 = screen_event_classification(df2)           
    
    df2['duration']=np.nan
    df2['duration']=df2['datetime'].diff()
    df2['duration'] = df2['duration'].shift(-1)
    
    #Discard any datapoints whose duration in “ON” and "IN USE" states are 
    #longer than 10 hours becaus they may be artifacts
    thr = pd.Timedelta('10 hours')
    df2 = df2[~((df2.on==1) & (df2.duration>thr))]
    df2 = df2[~((df2.use==1) & (df2.duration>thr))]
    
    if len(df2)>0:
        on = df2[df2.on==1].groupby("user")["duration"].resample(**feature_functions).min()
        off = df2[df2.off==1].groupby("user")["duration"].resample(**feature_functions).min()
        use = df2[df2.use==1].groupby("user")["duration"].resample(**feature_functions).min()
        result = pd.concat([on, off, use], axis=1)
    return result

def screen_duration_max(df, bat, feature_functions=None):
    """ This function returns the maximum duration of each transition, within the 
    specified timeframe. The transitions are off, on, and in use. If there is no 
    specified timeframe, the function sets a 30 min default time window. The 
    function aggregates this number by user, by timewindow. 
    
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
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T'
    
    df2 = screen_util(df, bat)
    df2 = screen_event_classification(df2)           
    
    df2['duration']=np.nan
    df2['duration']=df2['datetime'].diff()
    df2['duration'] = df2['duration'].shift(-1)
    
    #Discard any datapoints whose duration in “ON” and "IN USE" states are 
    #longer than 10 hours becaus they may be artifacts
    thr = pd.Timedelta('10 hours')
    df2 = df2[~((df2.on==1) & (df2.duration>thr))]
    df2 = df2[~((df2.use==1) & (df2.duration>thr))]
    
    if len(df2)>0:
        on = df2[df2.on==1].groupby("user")["duration"].resample(**feature_functions).max()
        off = df2[df2.off==1].groupby("user")["duration"].resample(**feature_functions).max()
        use = df2[df2.use==1].groupby("user")["duration"].resample(**feature_functions).max()
        result = pd.concat([on, off, use], axis=1)
    return result

def screen_duration_mean(df, bat, feature_functions=None):
    """ This function returns the mean duration of each transition, within the 
    specified timeframe. The transitions are off, on, and in use. If there is no 
    specified timeframe, the function sets a 30 min default time window. The 
    function aggregates this number by user, by timewindow. 
    
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
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T'
    
    df2 = screen_util(df, bat)
    df2 = screen_event_classification(df2)           
    
    df2['duration']=np.nan
    df2['duration']=df2['datetime'].diff()
    df2['duration'] = df2['duration'].shift(-1)
    
    #Discard any datapoints whose duration in “ON” and "IN USE" states are 
    #longer than 10 hours becaus they may be artifacts
    thr = pd.Timedelta('10 hours')
    df2 = df2[~((df2.on==1) & (df2.duration>thr))]
    df2 = df2[~((df2.use==1) & (df2.duration>thr))]
    
    if len(df2)>0:
        on = df2[df2.on==1].groupby("user")["duration"].resample(**feature_functions).mean()
        off = df2[df2.off==1].groupby("user")["duration"].resample(**feature_functions).mean()
        use = df2[df2.use==1].groupby("user")["duration"].resample(**feature_functions).mean()
        result = pd.concat([on, off, use], axis=1)
    return result

def screen_duration_median(df, bat, feature_functions=None):
    """ This function returns the median duration of each transition, within the 
    specified timeframe. The transitions are off, on, and in use. If there is no 
    specified timeframe, the function sets a 30 min default time window. The 
    function aggregates this number by user, by timewindow. 
    
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
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T'
    
    df2 = screen_util(df, bat)
    df2 = screen_event_classification(df2)           
    
    df2['duration']=np.nan
    df2['duration']=df2['datetime'].diff()
    df2['duration'] = df2['duration'].shift(-1)
    
    #Discard any datapoints whose duration in “ON” and "IN USE" states are 
    #longer than 10 hours becaus they may be artifacts
    thr = pd.Timedelta('10 hours')
    df2 = df2[~((df2.on==1) & (df2.duration>thr))]
    df2 = df2[~((df2.use==1) & (df2.duration>thr))]
    
    if len(df2)>0:
        on = df2[df2.on==1].groupby("user")["duration"].resample(**feature_functions).median()
        off = df2[df2.off==1].groupby("user")["duration"].resample(**feature_functions).median()
        use = df2[df2.use==1].groupby("user")["duration"].resample(**feature_functions).median()
        result = pd.concat([on, off, use], axis=1)
    return result

def screen_duration_std(df, bat, feature_functions=None):
    """ This function returns the standard deviation of the duration of each 
    transition, within the specified timeframe. The transitions are off, on, 
    and in use. If there is no specified timeframe, the function sets a 30 min 
    default time window. The function aggregates this number by user, by timewindow. 
    
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
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T'
    
    df2 = screen_util(df, bat)
    df2 = screen_event_classification(df2)           
    
    df2['duration']=np.nan
    df2['duration']=df2['datetime'].diff()
    df2['duration'] = df2['duration'].shift(-1)
    
    #Discard any datapoints whose duration in “ON” and "IN USE" states are 
    #longer than 10 hours becaus they may be artifacts
    thr = pd.Timedelta('10 hours')
    df2 = df2[~((df2.on==1) & (df2.duration>thr))]
    df2 = df2[~((df2.use==1) & (df2.duration>thr))]
    
    if len(df2)>0:
        on = df2[df2.on==1].groupby("user")["duration"].resample(**feature_functions).std()
        off = df2[df2.off==1].groupby("user")["duration"].resample(**feature_functions).std()
        use = df2[df2.use==1].groupby("user")["duration"].resample(**feature_functions).std()
        result = pd.concat([on, off, use], axis=1)
    return result

def screen_first_unlock(df, bat):
    """ This function returns the first time the phone was unlocked each day. 
    The data is aggregated by user, by day.
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bat: pandas.DataFrame
        Dataframe with the battery information
    
    Returns
    -------
    result: dataframe
        Resulting dataframe
    """ 
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    
    df2 = screen_util(df, bat)
    df2 = screen_event_classification(df2)
    
    result = df2[df2.on==1].groupby("user").resample(rule='1D').min()
    result.drop(['on','off','na','use'], axis=1, inplace=True)
    return result