# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 14:42:18 2021

@author: arsii
"""

import pandas as pd
import plotly.express as px

def get_counts(df,aggregation):
    """Calculate datapoint counts by group or by user
    
    Parameters
    ----------
    
    df : Pandas DataFrame
    
    aggregation : str
    
    Returns
    -------
    
    n_events : Pandas DataFrame
    """
    
    assert isinstance(df,pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(aggregation,str), "aggregation is not a string"
    
    if aggregation == 'group':
            n_events = df[['group', 'user']].groupby(['group']).size().to_frame()
            n_events.columns = ['values']
            n_events = n_events.reset_index()
            
    elif aggregation == 'user':
            n_events = df[['user']].groupby(['user']).size().to_frame()
            n_events.columns = ['values']
            n_events = n_events.reset_index()
    
    return n_events

def calculate_bins(df,binning):
    """Calculate time index based bins for each observation in the dataframe.
    
    Parameters
    ----------
    df : Pandas DataFrame
    
    binning : str
    
    to_string : bool
    
    Returns
    -------
    
    bins : pandas period index
    
    """  
    
    assert isinstance(df,pd.DataFrame), "df is not a pandas dataframe."
    assert isinstance(binning,str), "binning is not a string"
    #assert isinstance(to_string,bool), "to_string is not a bool"
    
    bins = df.index.to_period(binning)
    bins = bins.to_series().astype(str)
    
    return bins
    


def boxplot_(df, fig_title, points = 'outliers', y = 'values', xlabel="Group", ylabel="Count",binning=False):
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
    assert ((isinstance(binning,str)) or (binning,bool)), "binning."

    #TODO! check if this is necessary!
    #df[y] = df[y].astype(np.float64)
        
    if binning is not False:
        df['bin'] = calculate_bins(df,binning).values
        fig = px.box(df,
                     x = "bin", 
                     y = y,
                     color = "group",
                     )
    else:
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
    
    return fig

def barplot_(df, fig_title, xlabel, ylabel):
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
    
    return fig 

def countplot(df, fig_title, plot_type = 'count', points = 'outliers',aggregation = 'group', user = None, column=None, binning=False):
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
    
    # Plot counts
    if plot_type == 'count':
        if aggregation == 'group':
                       
            n_events = get_counts(df,aggregation)
                      
            fig = boxplot_(n_events,
                               fig_title,
                               points,
                               y = 'values',
                               xlabel="Group",
                               ylabel="Count",
                               binning=binning
                               )
        
        elif aggregation == 'user':
                       
            n_events = get_counts(df,aggregation)
            
            fig = barplot_(n_events, 
                               fig_title, 
                               xlabel="User",
                               ylabel="Count")
        
        else:
            pass
        
    # Plot values
    elif plot_type == 'value':
        if aggregation == 'group':
            fig = boxplot_(df,
                               fig_title,
                               points,
                               y=column,
                               xlabel="Group",
                               ylabel="Value",
                               binning=binning
                               )
        
    else:
        pass
    
    return fig
    