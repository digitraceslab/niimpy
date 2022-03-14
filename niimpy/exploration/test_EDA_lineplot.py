"""
Created on Tue Nov  2 13:57:00 2021

@author: arsii
"""
import pytest
import plotly
from niimpy.EDA import setup_dataframe 
from niimpy.EDA import EDA_lineplot

def test_timeplot_single_ts():
    df = setup_dataframe.create_dataframe()
    
    fig = EDA_lineplot.timeplot(df,
                                users=['user_1'],
                                columns=['col_1'],
                                title='Test title',
                                xlabel='Xlabel',
                                ylabel='Ylabel',
                                resample='H',
                                interpolate=True,
                                window=1,
                                reset_index=False,
                                by=False
    )
    
    assert (type(fig) == plotly.graph_objs._figure.Figure)

def test_timeplot_two_ts():
    df = setup_dataframe.create_dataframe()
    
    fig = EDA_lineplot.timeplot(df,
                                users=['user_1','user_2'],
                                columns=['col_1'],
                                title='Test title',
                                xlabel='Xlabel',
                                ylabel='Ylabel',
                                resample='D',
                                interpolate=True,
                                window=1,
                                reset_index=True,
                                by=False
    )
    
    assert (type(fig) == plotly.graph_objs._figure.Figure)
    

def test_timeplot_two_users():
    df = setup_dataframe.create_dataframe()
    
    fig = EDA_lineplot.timeplot(df,
                                users=['user_1','user_2'],
                                columns=['col_1'],
                                title='Test title',
                                xlabel='Xlabel',
                                ylabel='Ylabel',
                                resample='H',
                                interpolate=True,
                                window=1,
                                reset_index=False,
                                by=False
    )
    
    assert (type(fig) == plotly.graph_objs._figure.Figure)
    

def test_timeplot_two_users_and_columns():
    df = setup_dataframe.create_dataframe()
    
    fig = EDA_lineplot.timeplot(df,
                                users='Group',
                                columns=['col_1'],
                                title='Test title',
                                xlabel='Xlabel',
                                ylabel='Ylabel',
                                resample='H',
                                interpolate=True,
                                window=1,
                                reset_index=False,
                                by='hour'
    )
    
    assert (type(fig) == plotly.graph_objs._figure.Figure)

def test_group_averages():
    df = setup_dataframe.create_dataframe()
    
    fig = EDA_lineplot.timeplot(df,
                                users='Group',
                                columns=['col_1'],
                                title='Test title',
                                xlabel='Xlabel',
                                ylabel='Ylabel',
                                resample='D',
                                interpolate=True,
                                window=1,
                                reset_index=False,
                                by='weekday'
    )
    
    assert (type(fig) == plotly.graph_objs._figure.Figure)