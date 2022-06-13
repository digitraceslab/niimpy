import pandas as pd

def extract_features_audio(df, features=None):
    """ This function computes and organizes the selected features for audio snippets 
    that have been recorded using Aware Framework. The function aggregates the features
    by user, by time window. If no time window is specified, it will automatically aggregate
    the features in 30 mins non-overlapping windows. 
    
    The complete list of features that can be calculated are: audio_count_silent, 
    audio_count_speech, audio_count_loud, audio_min_freq, audio_max_freq, audio_mean_freq, 
    audio_median_freq, audio_std_freq, audio_min_db, audio_max_db, audio_mean_db, 
    audio_median_db, audio_std_db
    
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
            
def audio_count_silent(df_u, feature_functions=None): 
    """ This function returns the number of times, within the specified timeframe, 
    when there has been some sound in the environment. If there is no specified timeframe,
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
    df_u["is_silent"] = pd.to_numeric(df_u["is_silent"])
        
    if len(df_u)>0:
        result = df_u.groupby('user')["is_silent"].resample(**feature_functions).sum()
        result = result.to_frame(name='audio_count_silent')
    return result

def audio_count_speech(df_u, feature_functions=None): 
    """ This function returns the number of times, within the specified timeframe, 
    when there has been some sound between 65Hz and 255Hz in the environment that could
    be specified as speech. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
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
    df_u["is_silent"] = pd.to_numeric(df_u["is_silent"])
    
    if len(df_u)>0:
        df_s = df_u[df_u['double_frequency'].between(65, 255)]
        df_s = df_s[df_s.is_silent==0] #check if there was a conversation. 0 is not silent, 1 is silent
        df_s.loc[:,"is_silent"] = 1
        result = df_s.groupby('user')["is_silent"].resample(**feature_functions).sum()
        result = result.to_frame(name='audio_count_speech')
    return result

def audio_count_loud(df_u, feature_functions=None): 
    """ This function returns the number of times, within the specified timeframe, 
    when there has been some sound louder than 70dB in the environment. If there 
    is no specified timeframe, the function sets a 30 min default time window. 
    The function aggregates this number by user, by timewindow.
    
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
    df_u["is_silent"] = pd.to_numeric(df_u["is_silent"])
    
    if len(df_u)>0:
        df_s = df_u[df_u.double_decibels>70] #check if environment was noisy
        df_s.loc[:,"is_silent"] = 1
        result = df_s.groupby('user')["is_silent"].resample(**feature_functions).sum()
        result = result.to_frame(name='audio_count_loud')
    return result

def audio_min_freq(df_u, feature_functions=None): 
    """ This function returns the minimum frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
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
    
    if len(df_u)>0:
        result = df_u.groupby('user')["double_frequency"].resample(**feature_functions).min()
        result = result.to_frame(name='audio_min_freq')
    return result

def audio_max_freq(df_u, feature_functions=None): 
    """ This function returns the maximum frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
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
    
    if len(df_u)>0:
        result = df_u.groupby('user')["double_frequency"].resample(**feature_functions).max()
        result = result.to_frame(name='audio_max_freq')
    return result

def audio_mean_freq(df_u, feature_functions=None): 
    """ This function returns the mean frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
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
    
    if len(df_u)>0:
        result = df_u.groupby('user')["double_frequency"].resample(**feature_functions).mean()
        result = result.to_frame(name='audio_mean_freq')
    return result

def audio_median_freq(df_u, feature_functions=None):
    """ This function returns the median frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
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
    
    if len(df_u)>0:
        result = df_u.groupby('user')["double_frequency"].resample(**feature_functions).median()
        result = result.to_frame(name='audio_median_freq')
    return result

def audio_std_freq(df_u, feature_functions=None): 
    """ This function returns the standard deviation of the frequency of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
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
    
    if len(df_u)>0:
        result = df_u.groupby('user')["double_frequency"].resample(**feature_functions).std()
        result = result.to_frame(name='audio_std_freq')
    return result

def audio_min_db(df_u, feature_functions=None): 
    """ This function returns the minimum decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
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
    
    if len(df_u)>0:
        result = df_u.groupby('user')["double_decibels"].resample(**feature_functions).min()
        result = result.to_frame(name='audio_min_db')
    return result

def audio_max_db(df_u, feature_functions=None): 
    """ This function returns the maximum decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
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
    
    if len(df_u)>0:
        result = df_u.groupby('user')["double_decibels"].resample(**feature_functions).max()
        result = result.to_frame(name='audio_max_db')
    return result

def audio_mean_db(df_u, feature_functions=None): 
    """ This function returns the mean decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
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
    
    if len(df_u)>0:
        result = df_u.groupby('user')["double_decibels"].resample(**feature_functions).mean()
        result = result.to_frame(name='audio_mean_db')
    return result

def audio_median_db(df_u, feature_functions=None): 
    """ This function returns the median decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
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
    
    if len(df_u)>0:
        result = df_u.groupby('user')["double_decibels"].resample(**feature_functions).median()
        result = result.to_frame(name='audio_median_db')
    return result

def audio_std_db(df_u, feature_functions=None): 
    """ This function returns the standard deviation of the decibels of the recorded audio snippets, 
    within the specified timeframe. If there is no specified timeframe, the function sets a 
    30 min default time window. The function aggregates this number by user, by timewindow.
    
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
    
    if len(df_u)>0:
        result = df_u.groupby('user')["double_decibels"].resample(**feature_functions).std()
        result = result.to_frame(name='audio_std_db')
    return result