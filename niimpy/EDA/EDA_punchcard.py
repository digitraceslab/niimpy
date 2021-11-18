# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 16:14:47 2021

@author: arsii
"""
import pandas as pd
import plotly.express as px

def punchcard_plot(df, user_list = None, columns = None, title = "Punchcard Plot", resample = 'D', normalize = False, timerange = False):
    """Punchcard plot for given users and column with optional resampling
    
    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing the data
    user_list : list, optional
        List containing user id's as string. The default is None.
    columns : list, optional
        List containing columns as strings. The default is None.
    title : str, optional
        Plot title. The default is "Punchcard Plot".
    resample : str, optional
        Indicator for resampling. The default is 'D'.
    normalize : boolean, optional
        If true, data is normalized using min-max-scaling. The default is False.
    timerange : boolean or tuple, optional
        If false, timerange is not filtered. 
        If tuple containing timestamps, timerange is filtered.
        The default is False.

    Returns
    -------
    None.
    
    """
    
    assert isinstance(df,pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(user_list,(list,type(None))), "user_list is not a list or None."
    assert isinstance(columns, (list,type(None))), "columns is not a list or None"
    assert isinstance(title,str), "title is not a string."
    assert isinstance(resample,str), "resample is not a string."
    assert isinstance(normalize,bool), "normalize is not a boolean."
    assert isinstance(timerange,(bool,tuple)), "timerange is not a boolean or tuple."
        
    # if one user
    if len(user_list) == 1:
        # one colums
        if len(columns) == 1:
            df_sel = df[df['user'] == 'lMmhJTDCgm3t'][['battery_level']].resample('D').mean()

            fp = pd.pivot_table(df_sel, index=df_sel.index.month, values = 'battery_level', columns=df_sel.index.day)# aggfunc=np.sum, fill_value=0)

            fig = px.imshow(fp)
            fig.update_layout(title=title,
                      xaxis_nticks=31,
                      xaxis_title = 'Day',
                      yaxis_title = 'Month')
            
        # multiple columns
        else:
            bools = df['user'].isin(user_list)
            df_sel = df[bools][columns].resample(resample).mean()
            
            if normalize:
                df_sel[columns] = (df_sel[columns] - df_sel[columns].min()) / (df_sel[columns].max() - df_sel[columns].min())
            
            fig = px.imshow(df_sel.transpose())
            fig.update_layout(title=title,
                      xaxis_title = 'Date',
                      yaxis_title = 'Columns')

    # multiple users just one column
    else:
        start = df.index.min()
        end = df.index.max()
        date_index = pd.date_range(start = start.strftime('%Y-%m-%d'), end = end.strftime('%Y-%m-%d'),freq='D')

        df_comb = pd.DataFrame(index=date_index)
        df_comb.index = pd.to_datetime(df_comb.index)

        for u in user_list:    
            start = df.index.min()
            end = df.index.max()
            date_index = pd.date_range(start = start.strftime('%Y-%m-%d'), end = end.strftime('%Y-%m-%d'),freq='D')
            df_temp = df[df['user'] == u][columns].resample('D').mean()
            df_temp.index = df_temp.index.strftime('%Y-%m-%d')
            df_temp.index = pd.to_datetime(df_temp.index)
            df_temp = df_temp.reindex(date_index)
            df_comb[u] = df_temp
        
        if timerange:
            fig = px.imshow(df_comb.loc[timerange[0]:timerange[1]].transpose())
        else:
            fig = px.imshow(df_comb.transpose())
        fig.update_layout(title=title,
                          xaxis_title = 'Date',
                          yaxis_title = 'User')

    fig.show()
