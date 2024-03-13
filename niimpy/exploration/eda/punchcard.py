# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 16:14:47 2021

@author: arsii
"""
import pandas as pd
import numpy as np
import plotly.express as px

def get_timerange_(df,resample):
    """get first and last timepoint from the dataframe, 
    and return a resampled datetimeindex.
    
    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing the data
    ressample : str
        Resample parameter e.g., 'D' for resampling by day

    Returns
    -------
    date_index : pd.DatatimeIndex
        Resampled DatetimeIndex
    """
    resample_options = ['D','h']
    
    assert isinstance(df,pd.DataFrame), "df is not a pandas dataframe"
    assert isinstance(resample,str), "resample is not a string"
    assert (resample in resample_options), f"resample option: {resample} is not valid. Available options: {resample_options}."
    
    start = df.index.min()
    end = df.index.max()
    
    if resample == 'D':
        date_index = pd.date_range(start = start.strftime('%Y-%m-%d'), end = end.strftime('%Y-%m-%d'),freq='D')
    if resample == 'h':
        date_index = pd.date_range(start = start.strftime('%Y-%m-%d-%H'), end = end.strftime('%Y-%m-%d-%H'),freq='h')
            
    return date_index

def combine_dataframe_(df,user_list,columns,res,date_index,agg_func="mean"):
    """resample values from multiple users into new dataframe
    
    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing the data
    user_list : list
        List containing user names/id's (str)
    columns : list
        List of column names (str) to be plotted
    res : str
        Resample parameter e.g., 'D' for resampling by day
    date_index : pd.date_range
        Date range used as an index
    agg_func : numpy function
        Aggregation function used with resample. The default is "mean"

    Returns
    -------
    df_comb : pd.DataFrame
        Resampled and combined dataframe
    """
    assert isinstance(df,pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(user_list,list), "user_list is not a list."
    assert isinstance(columns, list), "columns is not a list"
    assert isinstance(res,str), "res is not a string."
    assert isinstance(date_index,pd.core.indexes.datetimes.DatetimeIndex), "date_index is not a DatetimeIndex."
    
    df_comb = pd.DataFrame(index=date_index)
    df_comb.index = pd.to_datetime(df_comb.index)

    for u in user_list:
        df_temp = df[df['user'] == u][columns].resample(res).agg(agg_func)
        df_temp.index = df_temp.index.strftime('%Y-%m-%d')
        df_temp.index = pd.to_datetime(df_temp.index)
        df_temp = df_temp.reindex(date_index)
        df_comb[u] = df_temp
        
    return df_comb

def punchcard_(df,title,n_xticks,xtitle,ytitle):
    """ create a punchcard plot
    
    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing the data
    title : str
        Plot title. 
    n_xticks : int or None
        Number of xaxis ticks. If None, scaled automatically.
    xtitle : str
        Plot xaxis title
    ytitle : str
        Plot yaxis title
    
    Returns
    -------
    fig : plotly.graph_objs._figure.Figure
        Punchcard plot
    """
    assert isinstance(df,pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(title,str), "title is not a string."
    assert isinstance(n_xticks, (int,type(None))), "n_ticks is not an integer or None"
    assert isinstance(xtitle,str), "xtitle is not a string."
    assert isinstance(ytitle,str), "ytitle is not a string."
        
    fig = px.imshow(df,aspect='auto',labels={'x':xtitle,'y':ytitle,'color':'Value'})
    
    if n_xticks:
        fig.update_layout(title=title,
                          xaxis_nticks=n_xticks,
                          xaxis_title=xtitle,
                          yaxis_title=ytitle)
        
        
    else:
        fig.update_layout(title=title,
                          xaxis_title=xtitle,
                          yaxis_title=ytitle)
        
    fig.update_yaxes(tickson="labels")
    fig.update_yaxes(type='category')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    
    return fig

def punchcard_plot(df, user_list = None, columns = None, title = "Punchcard Plot", resample = 'D', normalize = False, agg_func = "mean", timerange = False):
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
        Indicator for resampling frequency. The default is 'D' (day).
    agg_func : numpy function
        Aggregation function used with resample. The default is np.mean
    normalize : boolean, optional
        If true, data is normalized using min-max-scaling. The default is False.
    timerange : boolean or tuple, optional
        If false, timerange is not filtered. 
        If tuple containing timestamps, timerange is filtered.
        The default is False.

    Returns
    -------
    fig : plotly.graph_objs._figure.Figure
        Punchcard plot
    
    """
    
    assert isinstance(df,pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(user_list,(list,type(None))), "user_list is not a list or None."
    assert isinstance(columns, (list,type(None))), "columns is not a list or None"
    assert isinstance(title,str), "title is not a string."
    assert isinstance(resample,str), "resample is not a string."
    assert isinstance(normalize,bool), "normalize is not a boolean."
    assert isinstance(timerange,(bool,tuple)), "timerange is not a boolean or tuple."
    
    # The aggregation function can be a string referring to an internal Pandas function
    # assert callable(agg_func), "agg_function is not a callable."
        
    # one user
    if len(user_list) == 1:
        # one colums
        if len(columns) == 1:
            df_sel = df[df['user'] == user_list[0]][[columns[0]]].resample(resample).agg(agg_func)
            
            if normalize:
                df_sel[columns] = (df_sel[columns] - df_sel[columns].min()) / (df_sel[columns].max() - df_sel[columns].min())
                
            fp = pd.pivot_table(df_sel, index=df_sel.index.month, values = columns[0], columns=df_sel.index.day)
            fig = punchcard_(fp,title,n_xticks=31, xtitle='Day',ytitle='Month')
            
        # multiple columns
        else:
            bools = df['user'].isin(user_list)
            selected = []
            for col in columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    selected.append(df[bools][col].resample(resample).agg(agg_func))
                else:
                    selected.append(df[bools][col].resample(resample).first())
            df_sel = pd.concat(selected, axis=1)
            
            if normalize:
                df_sel[columns] = (df_sel[columns] - df_sel[columns].min()) / (df_sel[columns].max() - df_sel[columns].min())
            
            fig = punchcard_(df_sel,title,n_xticks=None, xtitle='Column',ytitle='Date')

    # multiple users, one column
    else:
        date_index = get_timerange_(df,resample)
        df_comb = combine_dataframe_(df,user_list,columns,resample,date_index,agg_func)
        
        if normalize:
            df_comb =(df_comb-df_comb.min())/(df_comb.max()-df_comb.min())
                
        if timerange:
            fig = punchcard_(df_comb.loc[timerange[0]:timerange[1]].transpose(),title,n_xticks=None, xtitle='Date',ytitle='User')
        else:
            fig = punchcard_(df_comb.transpose(),title,n_xticks=None, xtitle='Date',ytitle='User')
        
    return fig
