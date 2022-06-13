import numpy as np
import pandas as pd

import niimpy
from niimpy.preprocessing import battery as b

def screen_util(df, bat, feature_functions=None):
    """ This function is a helper function for all other screen preprocessing.
    The function has the option to merge information from the battery sensors to
    include data when the phone is shut down. The function also detects the missing 
    datapoints (i.e. not allowed transitions like ON to ON). 
    
    Parameters
    ----------
    df: pandas.DataFrame
        Input data frame
    bet: pandas.DataFrame
        Dataframe with the battery information
    battery_shutdown: Boolean
        Optional feature to include or exclude the information from the battery 
        dataframe. 
    
    Returns
    -------
    df: dataframe
        Resulting dataframe
    """
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "battery_shutdown" in feature_functions.keys():
        feature_functions['battery_shutdown'] = None
    
    df["screen_status"]=pd.to_numeric(df["screen_status"]) #convert to numeric in case it is not

    #Include the missing points that are due to shutting down the phone
    if feature_functions['battery_shutdown'] is not None:
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

def screen_event_classification(df2):
    
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    
    #Classify the event 
    df2['next'] = df2['screen_status'].shift(-1)
    df2['next'] = df2['screen_status'].astype(int).astype(str)+df2['screen_status'].shift(-1).fillna(0).astype(int).astype(str)   
    df2 = df2.groupby("user", as_index=False).apply(lambda x: x.iloc[:-1])#Discard transitions between subjects
    df2 = df2.droplevel(0)
    df2["use"] =  df2["on"] = df2["na"] = df2["off"] = 0
    
    df2["use"][(df2.next=='30') | (df2.next=='31') | (df2.next=='32')]=1 #in use
    df2["on"][(df2.next=='10') | (df2.next=='12') | (df2.next=='13') | (df2.next=='20')]=1 #on
    df2["na"][(df2.next=='21') | (df2.next=='23')]=1 #irrelevant. It seems like from 2 to 1 is from off to on (i.e. the screen goes to off and then it locks)
    df2["off"][(df2.next=='01') | (df2.next=='02') | (df2.next=='03') | (df2.next=='21')]=1 #off
    
    df2.drop(columns=["next","screen_status"], inplace=True)   
    
    #Discard the first and last row because they do not have all info. We do not
    #know what happened before or after these points. 
    df2 = df2.groupby("user", as_index=False).apply(lambda x: x.iloc[1:])
    df2 = df2.groupby("user", as_index=False).apply(lambda x: x.iloc[:-1])
    df2 = df2.droplevel(0)
    df2 = df2.droplevel(0)
    return df2

def screen_off(df, bat, feature_functions=None):
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    df2 = screen_util(df, bat, feature_functions)
    df = df[df.screen_status == 0] #Select only those OFF events when no missing data is present
    return df

def screen_count(df, bat, feature_functions=None):
    
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T'
    if not "battery_shutdown" in feature_functions.keys():
        feature_functions['battery_shutdown'] = None
    
    df2 = screen_util(df, bat, feature_functions)
    df2 = screen_event_classification(df2)
    
    if len(df2)>0:
        on = df2.groupby("user")["on"].resample(**feature_functions).sum()
        off = df2.groupby("user")["off"].resample(**feature_functions).sum()
        use = df2.groupby("user")["use"].resample(**feature_functions).sum()
        result = pd.concat([on, off, use], axis=1)
    return result

def screen_duration(df, bat, feature_functions=None):
    
    assert isinstance(df, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(bat, pd.DataFrame), "Please input data as a pandas DataFrame type"
    assert isinstance(feature_functions, dict), "feature_functions is not a dictionary"
    
    if not "rule" in feature_functions.keys():
        feature_functions['rule'] = '30T'
    if not "battery_shutdown" in feature_functions.keys():
        feature_functions['battery_shutdown'] = None
    
    df2 = screen_util(df, bat, feature_functions)
    feature_functions.pop('battery_shutdown', None) #no need for this argumetn anymore
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