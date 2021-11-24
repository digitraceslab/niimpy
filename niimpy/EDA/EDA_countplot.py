# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 14:42:18 2021

@author: arsii
"""

import pandas as pd
import plotly.express as px


def EDA_boxplot_(df, fig_title, points = 'outliers', y = 'values', xlabel="Group", ylabel="Count"):
    """Plot a boxplot
    
    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing the data
        
    fig_title : str
        Plot title
        
    points : str
        If 'all', show all observations next to boxplots
        If 'outliers', show only outlying points
        The default is 'outliers' 
        
    y: str
        A dataframe column to plot
        
    xlabel : str
        Plot xlabel
        
    ylabel : str
        Plot ylabel 
    
    Returns
    -------
        
    """
    
    assert isinstance(df,pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(points,str), "points is not a string"
    assert isinstance(y,str), "y is not a string"
    assert isinstance(fig_title,str), "Title is not a string."
    assert isinstance(xlabel,str), "Xlabel is not a string."
    assert isinstance(ylabel,str), "Ylabel is not a string."


    '''
    if binning:
    n_events = n_events.groupby('group').resample('H').size().reset_index()
    n_events = n_events.set_index("level_1")
    n_events.loc[n_events[0] >= 1,0] = 1'''
    
    
    
    fig = px.box(df,
                 x = "group", 
                 y = y,
                 color = "group",
                 points = points)

    fig.update_traces(quartilemethod='inclusive') # or "inclusive", or "linear" by default
    fig.update_layout(title = fig_title,
                      xaxis_title = xlabel,
                      yaxis_title = ylabel,
                      autotypenumbers='convert types') 
    
    fig.show()

def EDA_barplot_(df, fig_title, xlabel, ylabel):
    """Plot a barplot showing counts for each subjects
    
    A dataframe must have columns named 'user', containing the user id's,
    and 'values' containing the observation counts.
    
    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe containing the data
        
    fig_title : str
        Plot title
        
    xlabel : str
        Plot xlabel
        
    ylabel : str
        Plot ylabel 
    
    Returns
    -------
        
    """ 
    assert isinstance(df,pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(fig_title,str), "Title is not a string."
    assert isinstance(xlabel,str), "Xlabel is not a string."
    assert isinstance(ylabel,str), "Ylabel is not a string."
    
    fig = px.bar(df, 
                 x = "user",
                 y = "values",
                 color = "user")
    
    fig.update_layout(title = fig_title,
                      xaxis_title = xlabel,
                      yaxis_title = ylabel)
    
    fig.show()  

def EDA_countplot(df, fig_title, plot_type = 'count', points = 'outliers', aggregation = 'group', user = None, column=None):
    """Create boxplot comparing groups or individual users.
    
    Parameters
    ----------
    df : pandas DataFrame
        A DataFrame to be visuliazed
        
    fig_title : str
        The plot title.
    
    plot_type : str
        If 'count', plot observation count per group (boxplot) or by user (barplot)
        If 'value', plot observation values per group (boxplot)
        The default is 'count'
        
    aggregation : str
        If 'group', plot group level summary
        If 'user', plot user level summary
        The default is 'group'
    
    user : str
        if given ...  
        The default is None
    column : str, optional 
        if None, count number of rows.  If given, count only occurances of that column. 
        The default is None.
    
    Returns
    -------
    
    """
    assert isinstance(df,pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(fig_title,str), "Title is not a string."
    assert isinstance(plot_type, str), "plot_type is not a string."
    assert isinstance(points,str), "points is not a string"
    assert isinstance(aggregation,str), "aggregation is not a string"
    assert ((isinstance(user,str)) or (user is None)), "user is not a string or None type."
    assert ((isinstance(column,str)) or (column is None)), "column in not a string or None type."
    
    if plot_type == 'count':
        if aggregation == 'group':
            n_events = df[['group', 'user']].groupby(['user', 'group']).size().to_frame()
            n_events.columns = ['values']
            n_events = n_events.reset_index()
            EDA_boxplot_(n_events,
                         fig_title,
                         points, 
                         y = 'values',
                         xlabel="Group",
                         ylabel="Count")
        
        elif aggregation == 'user':
            n_events = df[['user']].groupby(['user']).size().to_frame()
            n_events.columns = ['values']
            n_events = n_events.reset_index()
            EDA_barplot_(n_events, 
                        fig_title, 
                        xlabel="User",
                        ylabel="Count")
        
        else:
            pass
        
    elif plot_type == 'value':
        if aggregation == 'group':
            EDA_boxplot_(df,
                        fig_title,
                        points,
                        y=column,
                        xlabel="Group",
                        ylabel="Value")
        
    else:
        pass