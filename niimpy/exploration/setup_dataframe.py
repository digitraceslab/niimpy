import pandas as pd
import numpy as np
from datetime import date, datetime

def create_dataframe():
    """Create a sample Pandas dataframe used by the test functions.
    
    Returns
    -------
    df : pandas.DataFrame
        Pandas dataframe containing sample data.
        
    """
    
    dti = pd.date_range("2018-01-01", periods=9, freq="h")
    
    d = {'user': ['user_1','user_2','user_3','user_4','user_5','user_6','user_7','user_8','user_9'], 
         'group': ['group_1','group_1','group_1','group_2','group_2','group_2','group_3','group_3','group_3'],
         'col_1': [1, 2, 3,4,5,6,7,8,9], 
         'col_2': [10, 11, 12, 13, 14, 15, 16, 17, 18]}
    
    df = pd.DataFrame(data=d,index=dti)
    
    return df

def create_categorical_dataframe():
    """Create a sample Pandas dataframe used by the test functions.
    
    Returns
    -------
    df : pandas.DataFrame
        Pandas dataframe containing sample data.
        
    """
    
    dti = pd.date_range("2018-01-01", periods=9, freq="h")
    
    d = {
        'user': ['user_1','user_2','user_3','user_4','user_5','user_6','user_7','user_8','user_9'],
        'group': ['group_1','group_1','group_1','group_2','group_2','group_2','group_3','group_3','group_3'],
        'id_1': ["str_1","str_2","str_3","str_1","str_2","str_3","str_1","str_2",""],
        'id_2': ["str_1","str_2","str_3","","str_2","str_3","str_1","str_2",""],
        'id_3': ["","","str_3","","str_2","str_3","str_1","str_2",""],
    }
    
    df = pd.DataFrame(data=d,index=dti)
    
    return df

def create_timeindex_dataframe(nrows, ncols, random_state=None, freq=None):
    """Create a datetime index Pandas dataframe 
    
    Parameters
    ----------
    nrows : int
        Number of rows
    ncols : int
        Number of columns
    random_state: float, optional
        Random seed. If not given, default to 33.
    freq: string, optional:
        Sampling frequency.
    Returns
    -------
    df : pandas.DataFrame
        Pandas dataframe containing sample data with random missing rows.    
    """
    
    # Create a nrows x ncols matrix
    data = np.random.uniform(100, size=(nrows, ncols))
    df = pd.DataFrame(data)
    
    if freq is None:
        freq='h'
    idx = _makeDatetimeIndex(nrows, freq=freq)
    df = df.set_index(idx)
    
    return df

'''
def create_missing_dataframe():
    """Create a Pandas dataframe with random missingness.
    
    Returns
    -------
    df : pandas.DataFrame
        Pandas dataframe containing sample data with random missing rows.
        
    """
    
    dti = pd.date_range("2018-01-01", periods=9, freq="h")
    
    d = {'user': ['user_1','user_2','user_3','user_4','user_5','user_6','user_7','user_8','user_9'], 
         'group': ['group_1','group_1','group_1','group_2','group_2','group_2','group_3','group_3','group_3'],
         'col_1': [1, 2, 3,4,5,6,7,8,9], 
         'col_2': [10, 11, 12, 13, 14, 15, 16, 17, 18]}
    
    df = pd.DataFrame(data=d,index=dti)
    
    # Randomly set some values to NaN
    for col in df.columns:
        df.loc[df.sample(frac=0.25).index, col] = pd.np.nan

    data = (np.random.random(1000).reshape((50, 20)) > 0.5).astype(bool)
    df = pd.DataFrame(data).replace({False: None})
    df = df.set_index(pd.period_range('1/1/2011', '2/1/2015', freq='M'))
    df.index = df.index.to_timestamp()

    return df
'''

def create_missing_dataframe(nrows, ncols, density=.9, random_state=None, index_type=None, freq=None):
    """Create a Pandas dataframe with random missingness.
    
    Parameters
    ----------
    nrows : int
        Number of rows
    ncols : int
        Number of columns
    density: float
        Amount of available data
    random_state: float, optional
        Random seed. If not given, default to 33.
    index_type: float, optional
        Accepts the following values: "dt" for timestamp, "int" for integer.
    freq: string, optional:
        Sampling frequency. This option is only available is index_type is "dt". 
        
    Returns
    -------
    df : pandas.DataFrame
        Pandas dataframe containing sample data with random missing rows.    
    """
    
    # Create a nrows x ncols matrix
    data = np.random.uniform(100, size=(nrows, ncols))
    df = pd.DataFrame(data)
    
    if index_type:
        if index_type == "dt":
            if freq is None:
                freq='h'
            idx = _makeDatetimeIndex(nrows, freq=freq)
            df = df.set_index(idx)
        elif index_type == "int":
            return
        else: 
            raise ValueError("Can't recognize index_type. Try the following values: 'dt', 'int'.")
            
    i_idx, j_idx = _create_missing_idx(nrows, ncols, density, random_state)
    df.values[i_idx, j_idx] = None
    return df

def _makeDatetimeIndex(k=10, freq='B', name=None):
    dt = datetime(2022, 1, 1)
    dr = pd.bdate_range(dt, periods=k, freq=freq, name=name)
    return pd.DatetimeIndex(dr, name=name)

def _create_missing_idx(nrows, ncols, density, random_state=None):
    if random_state is None:
        random_state = np.random
    else:
        random_state = np.random.RandomState(random_state)

    # below is cribbed from scipy.sparse
    size = int(np.round((1 - density) * nrows * ncols))
    # generate a few more to ensure unique values
    min_rows = 5
    fac = 1.02
    extra_size = min(size + min_rows, fac * size)

    def _gen_unique_rand(rng, _extra_size):
        ind = rng.rand(int(_extra_size))
        return np.unique(np.floor(ind * nrows * ncols))[:size]

    ind = _gen_unique_rand(random_state, extra_size)
    while ind.size < size:
        extra_size *= 1.05
        ind = _gen_unique_rand(random_state, extra_size)

    j = np.floor(ind * 1. / nrows).astype(int)
    i = (ind - j * nrows).astype(int)
    return i.tolist(), j.tolist()