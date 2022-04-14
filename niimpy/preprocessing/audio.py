#use this paper for ideas: https://jinbo-bi.uconn.edu/wp-content/uploads/sites/2638/2018/12/Chase2016.pdf
#Ambient Noise

def extract_features_audio(silent, db, frequency, subject, features=None):
    assert isinstance(silent, pd.Series), "silent is not a pandas series"
    assert isinstance(db, pd.Series), "db is not a pandas series"
    assert isinstance(frequency, pd.Series), "frequency is not a pandas series"
    
    if features == None:
        features = ["audio_count_silent", "audio_count_speech", "audio_count_loud", "audio_min_freq",
                    "audio_max_freq", "audio_mean_freq", "audio_median_freq", "audio_std_freq",
                    "audio_min_db", "audio_max_db", "audio_mean_db", "audio_median_db", "audio_std_db"]
    feat_dict = {features[i]:features[i] for i in range(0,len(features))}
    
    df = pd.concat([silent.rename("silent"), db.rename("db"), frequency.rename("freq"), subject.rename("user")], axis=1)
    users = list(pd.unique(df.user))
    
    for feature in features:
        for user in users:
            df_u = df[df["user"]==user]
            df_u["silent"] = pd.to_numeric(df_u["silent"])
            
            func_to_call = feat_dict[feature]
            result = func_to_call(df_u,)
            
            if feature=="audio_count_silent":
                acs = audio_count_silent(df_u, agg, offset)
            
            
def audio_count_silent(df_u, agg, offset=None):
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = df_u["silent"].resample(agg, offset=offset).sum()
        result = result.to_frame()
    return result

def audio_count_speech(df_u, agg, offset=None):
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        df_s = df_u[df_u['freq'].between(65, 255)]
        df_s = df_s[df_s.silent==0] #check if there was a conversation. 0 is not silent, 1 is silent
        df_s.loc[:,"silent"] = 1
        result = df_s["silent"].resample(agg, offset=offset).sum()
        result = result.to_frame()
    return result

def audio_count_loud(df_u, agg, offset=None):
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        df_s = df_u[df_u.db>70] #check if environment was noisy
        df_s.loc[:,"silent"] = 1
        result = df_s["silent"].resample(agg, offset=offset).sum()
        result = result.to_frame()
    return result

def audio_min_freq(df_u, agg, offset=None):
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = df_u["freq"].resample(agg, offset=offset).min()
        result = result.to_frame()
    return result

def audio_max_freq(df_u, agg, offset=None):
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = df_u["freq"].resample(agg, offset=offset).max()
        result = result.to_frame()
    return result

def audio_mean_freq(df_u, agg, offset=None):
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = df_u["freq"].resample(agg, offset=offset).mean()
        result = result.to_frame()
    return result

def audio_median_freq(df_u, agg, offset=None):
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = df_u["freq"].resample(agg, offset=offset).median()
        result = result.to_frame()
    return result

def audio_std_freq(df_u, agg, offset=None):
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = df_u["freq"].resample(agg, offset=offset).std()
        result = result.to_frame()
    return result

def audio_min_db(df_u, agg, offset=None):
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = df_u["db"].resample(agg, offset=offset).min()
        result = result.to_frame()
    return result

def audio_max_db(df_u, agg, offset=None):
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = df_u["db"].resample(agg, offset=offset).max()
        result = result.to_frame()
    return result

def audio_mean_db(df_u, agg, offset=None):
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = df_u["db"].resample(agg, offset=offset).mean()
        result = result.to_frame()
    return result

def audio_median_db(df_u, agg, offset=None):
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = df_u["db"].resample(agg, offset=offset).median()
        result = result.to_frame()
    return result

def audio_std_db(df_u, agg, offset=None):
    assert isinstance(df_u, pd.DataFrame), "df_u is not a pandas dataframe"
    
    if len(df_u)>0:
        result = df_u["db"].resample(agg, offset=offset).std()
        result = result.to_frame()
    return result