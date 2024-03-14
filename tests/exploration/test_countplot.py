import pytest

import pandas as pd
import numpy as np
import plotly

from niimpy.exploration import setup_dataframe
from niimpy.exploration.eda import countplot

def test_get_counts():
    df = setup_dataframe.create_dataframe()
    group_counts = countplot.get_counts(df,'group')
    user_counts = countplot.get_counts(df,'user')
    assert (group_counts['values'].values == np.array([3,3,3])).all()
    assert (user_counts['values'].values == np.ones(9)).all()
    

def test_calculate_bins():
    target = np.array(['2018-01-01 00:00', '2018-01-01 01:00', '2018-01-01 02:00',
       '2018-01-01 03:00', '2018-01-01 04:00', '2018-01-01 05:00',
       '2018-01-01 06:00', '2018-01-01 07:00', '2018-01-01 08:00'])
    df = setup_dataframe.create_dataframe()
    bins = countplot.calculate_bins(df,'h').values
    assert (bins == target).all()
    
def test_countplot_count():
    df = setup_dataframe.create_dataframe()
    fig = countplot.countplot(df, 
                                      fig_title = 'Battery event counts by group', 
                                      plot_type = 'count', 
                                      points = 'all',
                                      aggregation = 'group', 
                                      user = None, 
                                      column=None,
                                      binning=False)

    assert (type(fig) == plotly.graph_objs._figure.Figure)

def test_countplot_value():
    df = setup_dataframe.create_dataframe()
    fig = countplot.countplot(df, 
                                fig_title = 'Test_title', 
                                plot_type = 'value', 
                                points = 'all',
                                aggregation = 'group', 
                                user = None, 
                                column='col_1',
                                binning='h')
    
    assert (type(fig) == plotly.graph_objs._figure.Figure)
    
def test_countplot_subject():
    df = setup_dataframe.create_dataframe()
    fig = countplot.countplot(df, 
                                      fig_title = 'Test_title', 
                                      plot_type = 'count', 
                                      points = 'all',
                                      aggregation = 'user', 
                                      user = None, 
                                      column = None,
                                      binning=False)
    
    assert (type(fig) == plotly.graph_objs._figure.Figure)