import pytest
import plotly
from niimpy.EDA import setup_dataframe
from niimpy.EDA import EDA_punchcard

def test_punchcard_one_user():
    df = setup_dataframe.create_dataframe()
    user_list = ['user_1']
    columns = ['col_1']
    title = 'test_title'
    resample = "D"

    fig = EDA_punchcard.punchcard_plot(df,user_list,columns,title, resample)
    assert (type(fig) == plotly.graph_objs._figure.Figure)
    
def test_punchcard_one_user_two_columns():
    df = setup_dataframe.create_dataframe()
    user_list = ['user_1']
    columns = ['col_1','col_2']
    title = 'test_title'
    resample = "D"
    normalize = True

    fig = EDA_punchcard.punchcard_plot(df,user_list,columns,title, resample,normalize)
    assert (type(fig) == plotly.graph_objs._figure.Figure)
    
def test_punchcard_two_users():
    df = setup_dataframe.create_dataframe()
    user_list = ['user_1','user_2']
    columns = ['col_1']
    title = 'test_title'
    resample = "D"

    fig = EDA_punchcard.punchcard_plot(df,user_list,columns,title, resample)
    assert (type(fig) == plotly.graph_objs._figure.Figure)

def test_punchcard_two_users_timerange():
    df = setup_dataframe.create_dataframe()
    user_list = ['user_1','user_2']
    columns = ['col_1']
    title = 'test_title'
    resample = "D"
    normalize = False
    timerange = ('20171231','20180101')
    
    fig = EDA_punchcard.punchcard_plot(df,user_list,columns,title, resample,normalize,timerange)
    assert (type(fig) == plotly.graph_objs._figure.Figure)    
