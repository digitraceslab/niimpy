# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 11:15:00 2021

@author: arsii
"""

import pytest

import pandas as pd
import numpy as np
import plotly

from niimpy.exploration import setup_dataframe
from niimpy.exploration.eda import categorical

def test_get_xticks():
    dictionary = {0 : 10, 1 : 20, 2 : 30}
    df = pd.Series(dictionary)
    vals,text = categorical.get_xticks_(df)
    assert np.allclose(vals.tolist(),[0,1,2])
    assert (text == ['0','1','2'])

def test_categorize_answers():
    df = setup_dataframe.create_categorical_dataframe()
    answers = categorical.categorize_answers(df, 'id_1')
    assert (answers.index.tolist() == ['', 'str_1', 'str_2', 'str_3'])
    assert np.allclose(answers.values,np.array([1,3,3,2]))

def test_plot_categories():
    df = setup_dataframe.create_categorical_dataframe()
    answers = categorical.categorize_answers(df, 'id_1')
    fig = categorical.plot_categories(answers, title=None, xlabel=None, \
                                          ylabel=None, width=900, height=900)
    assert (type(fig) == plotly.graph_objs._figure.Figure)

def test_questionnaire_summary():
    df = setup_dataframe.create_categorical_dataframe()
    fig = categorical.questionnaire_summary(df, 'id_1', title=None,\
                                                xlabel=None, ylabel=None, user=None,\
                                                width=900, height=900)
    assert (type(fig) == plotly.graph_objs._figure.Figure)
    
def test_questionnaire_summary_one_subject():
    df = setup_dataframe.create_categorical_dataframe()
    fig = categorical.questionnaire_summary(df, 'id_1', title=None,\
                                                xlabel=None, ylabel=None, user='user_1',\
                                                width=900, height=900)
    assert (type(fig) == plotly.graph_objs._figure.Figure)
    
def test_question_by_group():
    df = setup_dataframe.create_categorical_dataframe()
    grouped = categorical.question_by_group(df, question = 'id_1', group='group')
    #TODO! test contents of groupby object
    assert (type(grouped) == pd.core.frame.DataFrame)
    

    
def test_plot_grouped_categories():
    df = setup_dataframe.create_categorical_dataframe()
    grouped = categorical.question_by_group(df, question = 'id_1',   group='group')
    fig = categorical.plot_grouped_categories(grouped, group='group', title=None, xlabel=None, \
                                                  ylabel=None, width=900, height=900)
    assert (type(fig) == plotly.graph_objs._figure.Figure)
    
def test_questionnaire_grouped_summary():
    df = setup_dataframe.create_categorical_dataframe()
    fig = categorical.questionnaire_grouped_summary(df, question='id_1', group = 'group',title=None,\
                                                        xlabel=None,) 

    assert (type(fig) == plotly.graph_objs._figure.Figure)