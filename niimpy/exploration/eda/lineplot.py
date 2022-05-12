"""
Created on Wed Oct 27 09:53:46 2021

@author: arsii
"""

import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

def timeplot(df, users, columns, title, xlabel, ylabel, resample=False,
             interpolate=False, window=False, reset_index=False, by=False):
    """
    Plot a time series plot. Plot selected users and columns or group level
    averages, aggregated by hour or weekday.

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing the data
    users : list or str 
        Users to plot.
    columns : list or str
        Columns to plot.
    title : str
        Plot title.
    xlabel : str
        Plot xlabel.
    ylabel : str
        Plot ylabel.
    resample : str, optional
        Data resampling frequency. The default is False.
        For details: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html
    interpolate : bool, optional
        If true, time series will be interpolated using splines. The default is False.
    window : int, optional
        Rolling window smoothing window size. The default is False.
    reset_index : bool, optional
        If true, dataframe index will be resetted. The default is False.
    by : str, optional
        Indicator for group level averaging. The default is False.
        If 'hour', hourly averages per group are presented.
        If 'weekday', daily averages per gruop are presented.
    Returns
    -------
    None.

    """    
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(users, str) or (isinstance(users, list)), "users is not a string or a list"
    assert isinstance(columns, str) or (isinstance(columns, list)), "column is not a string or a list"
    assert isinstance(title, str), "title is not a string"
    assert isinstance(xlabel, str), "xlabel is not a string"
    assert isinstance(ylabel ,str), "ylabel is not a string"
    assert isinstance(resample, (str, bool)), "resample is not a string or a boolean"
    assert isinstance(interpolate, bool), "interpolate is not a boolean"
    assert isinstance(window, int), "window is not an int"
    assert isinstance(reset_index, bool), "reset_index is not boolean"
    assert isinstance(by, (str,bool)), "by is not a string or a boolean"
    
    
    if users == 'Group':
        fig = plot_averages_(df,
                             columns[0],
                             by)

    else:
        fig = plot_timeseries_(df, 
                               columns,
                               users,
                               title,
                               xlabel,
                               ylabel,
                               resample,
                               interpolate,
                               window,
                               reset_index)
    return fig

def calculate_averages_(df,column, by):
    """calculate group averages by given timerange
    """
    
    if by == 'hour':
        averages = df[[column,'group']].groupby([df.index.hour,'group']).mean().reset_index()
    elif by == 'weekday':
        averages = df[[column, 'group']].groupby([df.index.weekday, 'group']).mean().reset_index()
    else:
        averages = 0
    
    averages.set_index(averages.columns[0],inplace=True)
    return averages

def plot_averages_(df, column, by='hour'):
    """Plot user group level averages by hour or by weekday.

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing the data
    column : str
        Columns to plot.
    by : str, optional
        Indicator for group level averaging. The default is False.
        If 'hour', hourly averages per group are presented.
        If 'weekday', daily averages per gruop are presented.

    Returns
    -------
    None.

    """
    assert isinstance(df,pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(column,str), "column is not a string"
    assert isinstance(by,str), "by is not a string"
    
    # GROUP AVERAGES BY HOUR
    if by == 'hour':
        averages = calculate_averages_(df,column,by)
        fig = px.line(averages,
                      x=averages.index,
                      y=column,
                      color="group",)

        #fig.update_traces(mode='markers+lines')

        fig.update_layout(title="{} hourly averages".format(column),
                          xaxis_title="Hour",
                          yaxis_title="Value",
                          xaxis=dict(tickmode='array',
                                     tickvals=[0, 3, 6, 9, 12, 15, 18, 21],
                                     ticktext=['0am', '3am', '6am', '9am', '12pm', '15pm', '18pm', '21pm']))

    # GROUP AVERAGES BY WEEKDAY
    elif by == 'weekday':
        averages = calculate_averages_(df,column,by)

        fig = px.line(averages,
                      x=averages.index,
                      y=column,
                      color="group",)

        #fig.update_traces(mode='markers+lines')

        fig.update_layout(title="{} weekday averages".format(column),
                          xaxis_title="Weekday",
                          yaxis_title="Value",
                          xaxis=dict(
                          tickmode='array',
                          tickvals=[0, 1, 2, 3, 4, 5, 6],
                          ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']))
        
    else:
        pass
    
    return fig
            

def resample_data_(df, resample, interpolate, window_len, reset_index):
    """resample dataframe for plotting
    """
    if resample:
        df = df.resample(resample).mean()
            
    if interpolate:
        df = df.interpolate(method='spline',order=2)
            
    if window_len:
        df = df.rolling(window_len, win_type='gaussian').mean(std=2)
                
    if reset_index:
        df = df.reset_index(drop=True)
            
    df.dropna(axis=0, how='any', inplace=True)
    
    return df

def plot_timeseries_(df, columns, users, title, xlabel, ylabel, resample=False,
                     interpolate=False, window_len=False, reset_index=False):
    """There goes the text.

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing the data
    columns : list or str
        Columns to plot.
    users : list or str 
        Users to plot.
    title : str
        Plot title.
    xlabel : str
        Plot xlabel.
    ylabel : str
        Plot ylabel.
    resample : str, optional
        Data resampling frequency. The default is False.
        For details: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html
    interpolate : bool, optional
        If true, time series will be interpolated using splines. The default is False.
    window : int, optional
        Rolling window smoothing window size. The default is False.
    reset_index : bool, optional
        If true, dataframe index will be resetted. The default is False.
        
    Returns
    -------
    None.

    """
    assert isinstance(df, pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(users, (str,list)), "users is not a string or a list"
    assert isinstance(columns, (str, list)), "column is not a string or a list"
    assert isinstance(title, str), "title is not a string"
    assert isinstance(xlabel, str), "xlabel is not a string"
    assert isinstance(ylabel ,str), "ylabel is not a string"
    assert isinstance(resample, (str,bool)), "resample is not a string or a boolean"
    assert isinstance(interpolate, bool), "interpolate is not a boolean"
    assert isinstance(window_len, int), "window is not an int"
    assert isinstance(reset_index, bool), "reset_index is not boolean"

    
    fig = go.Figure()
    
    for u in users:
        for c in columns:
            
            df_sel = df[df['user'] == u][c]
            
            df_sel = resample_data_(df_sel, resample, interpolate, window_len, reset_index)
                        
            fig.add_trace(go.Scatter(x=df_sel.index, 
                                     y=df_sel.values,
                                     name= u + ' / ' + c,
                                     showlegend=True))
    
    #fig.update_traces(mode='markers+lines')

    fig.update_layout(title=title,
                      xaxis_title=xlabel,
                      yaxis_title=ylabel,
                      width=1200,
                      height=600,)
    return fig




