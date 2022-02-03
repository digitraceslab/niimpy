# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 11:15:00 2021

@author: arsii
"""

import pytest

import pandas as pd
import numpy as np
import plotly

from niimpy.EDA import setup_dataframe
from niimpy.EDA import EDA_categorical

def test_get_xticks():
    dictionary = {0 : 10, 1 : 20, 2 : 30}
    df = pd.Series(dictionary)
    vals,text = EDA_categorical.get_xticks_(df)
    assert np.allclose(vals.tolist(),[0,1,2])
    assert (text == ['0','1','2'])

def test_categorize_answers():
    df = setup_dataframe.create_categorical_dataframe()
    answers = EDA_categorical.categorize_answers(df, 'id', 'answer')
    #TODO! fix this
    #assert (answers.index.tolist() == ['str_1'])
    assert np.allclose(answers.values,np.array([3]))

def test_plot_categories():
    df = setup_dataframe.create_categorical_dataframe()
    answers = EDA_categorical.categorize_answers(df, 'id', 'answer')
    fig = EDA_categorical.plot_categories(answers, title=None, xlabel=None, \
                                          ylabel=None, width=900, height=900)
    assert (type(fig) == plotly.graph_objs._figure.Figure)

def test_questionnaire_summary():
    df = setup_dataframe.create_categorical_dataframe()
    fig = EDA_categorical.questionnaire_summary(df, 'id_1', 'answer', title=None,\
                                                xlabel=None, ylabel=None, user=None,\
                                                width=900, height=900)
    assert (type(fig) == plotly.graph_objs._figure.Figure)
    
# 5) def question_by_group(df, question, id_column = 'id', answer_column = 'answer', group='group'):

# 6) def plot_grouped_categories(df, group, title=None, xlabel=None, ylabel=None, width=900, height=900):

# 7) def questionnaire_grouped_summary(
#    df, question, id_column ='id', answer_column = 'answer', group = 'group', title=None, xlabel=None, 
# ylabel=None, width=900, height=900
#):

# Read some mock dataframe and test the functions then
'''
class TestEDAcategorical(object):

    def test_EDA_questionnaire_summary(self):
        """
        Test EDA questionnaire summary functions. The test fails when arguments:
            - data is not a pandas dataframe
            - columns a is not a string or a list
            - title is not a string
            - xlabel is not a string
            - ylabel is not a string
            - resample is not a string or boolean
            - interpolate is not a boolean
            - window is not an integer
            - reset_index is not a boolean
            - by in not a string or a boolean

        Returns
        -------
        None.

        """
        df = setup_dataframe.create_categorical_dataframe()

        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_categorical.questionnaire_summary(df.to_numpy(),
                                                  question = 'question',
                                                  column = 'answer',
                                                  title = 'title',
                                                  xlabel = 'xlabel',
                                                  ylabel = 'ylabel',
                                                  user = None)

        expected_error_msg = "df is not a pandas dataframe."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)

        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_categorical.questionnaire_summary(df,
                                                  question = 1,
                                                  column = 'answer',
                                                  title = 'title',
                                                  xlabel = 'xlabel',
                                                  ylabel = 'ylabel',
                                                  user = None)

        expected_error_msg = "question is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)

        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_categorical.questionnaire_summary(df,
                                                  question = 'question',
                                                  column = 1,
                                                  title = 'title',
                                                  xlabel = 'xlabel',
                                                  ylabel = 'ylabel',
                                                  user = None)

        expected_error_msg = "column is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)

        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_categorical.questionnaire_summary(df,
                                                  question = 'question',
                                                  column = 'answer',
                                                  title = 1,
                                                  xlabel = 'xlabel',
                                                  ylabel = 'ylabel',
                                                  user = None)

        expected_error_msg = "title is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)

        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_categorical.questionnaire_summary(df,
                                                  question = 'question',
                                                  column = 'answer',
                                                  title = 'title',
                                                  xlabel = 1,
                                                  ylabel = 'ylabel',
                                                  user = None)

        expected_error_msg = "xlabel is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)

        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_categorical.questionnaire_summary(df,
                                                  question = 'question',
                                                  column = 'answer',
                                                  title = 'title',
                                                  xlabel = 'xlabel',
                                                  ylabel = 1,
                                                  user = None)

        expected_error_msg = "ylabel is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)

        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_categorical.questionnaire_summary(df,
                                                  question = 'question',
                                                  column = 'answer',
                                                  title = 'title',
                                                  xlabel = 'xlabel',
                                                  ylabel = 'ylabel',
                                                  user = 1)

        expected_error_msg = "user is not a boolean or string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)

        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_categorical.questionnaire_grouped_summary(df,
                                                  question = 'question',
                                                  column = 'answer',
                                                  title = 'title',
                                                  xlabel = 'xlabel',
                                                  ylabel = 'ylabel',
                                                  group = 1)

        expected_error_msg = "group is not a boolean or string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
'''