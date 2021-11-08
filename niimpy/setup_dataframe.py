import pandas as pd

def create_dataframe():
    """Create a sample Pandas dataframe used by the test functions.
    
    Returns
    -------
    df : pandas.DataFrame
        Pandas dataframe containing sample data.
        
    """
    
    dti = pd.date_range("2018-01-01", periods=9, freq="H")
    
    d = {'user': ['user_1','user_2','user_3','user_4','user_5','user_6','user_7','user_8','user_9'], 
         'group': ['group_1','group_1','group_1','group_2','group_2','group_2','group_3','group_3','group_3'],
         'col_1': [1, 2, 3,4,5,6,7,8,9], 
         'col_2': [10, 11, 12, 13, 14, 15, 16, 17, 18]}
    
    df = pd.DataFrame(data=d,index=dti)
    
    return df
