import pytest
import plotly
import numpy as np
import datetime
from niimpy.exploration import setup_dataframe
from niimpy.exploration.eda import punchcard

def test_punchcard_one_user():
    df = setup_dataframe.create_dataframe()
    user_list = ['user_1']
    columns = ['col_1']
    title = 'test_title'
    resample = "D"

    fig = punchcard.punchcard_plot(df,user_list,columns,title, resample)
    assert (type(fig) == plotly.graph_objs._figure.Figure)
    assert (type(fig) == plotly.graph_objs._figure.Figure)
    assert (fig.layout.xaxis.nticks == 31)
    assert (fig.layout.title.text == 'test_title')
    
def test_punchcard_one_user_two_columns():
    df = setup_dataframe.create_dataframe()
    user_list = ['user_1']
    columns = ['col_1','col_2']
    title = 'test_title'
    resample = "D"
    normalize = True

    fig = punchcard.punchcard_plot(df,user_list,columns,title, resample, normalize)
    assert (type(fig) == plotly.graph_objs._figure.Figure)
    assert(fig.layout.legend.x == None)
    assert(fig.layout.legend.y == None)
    
def test_punchcard_two_users():
    df = setup_dataframe.create_dataframe()
    user_list = ['user_1','user_2']
    columns = ['col_1']
    title = 'test_title'
    resample = "D"

    fig = punchcard.punchcard_plot(df,user_list,columns,title, resample)
    assert (type(fig) == plotly.graph_objs._figure.Figure)

def test_punchcard_two_users_timerange():
    df = setup_dataframe.create_dataframe()
    user_list = ['user_1','user_2']
    columns = ['col_1']
    title = 'test_title'
    resample = "D"
    normalize = False
    agg_function = "mean"
    timerange = ('20171231','20180101')
    
    fig = punchcard.punchcard_plot(df,user_list,columns,title, resample,normalize,agg_function,timerange)
    assert (type(fig) == plotly.graph_objs._figure.Figure)
    print(fig.data[0].x[0])
    assert(fig.data[0].x[0] == np.datetime64('2018-01-01T00:00:00.000000000'))
