# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 11:15:00 2021

@author: arsii
"""


import pytest
from niimpy.EDA import setup_dataframe
from niimpy.EDA import EDA_categorical

class TestEDAcategorical(object):
    
    def test_EDA_questionnaire_summary(self):
        """
        Test EDA_questionnaire_summary function. The test fails when arguments:
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
                                                  user = None,
                                                  group = None)
            
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
                                                  user = None,
                                                  group = None)
            
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
                                                  user = None,
                                                  group = None)
            
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
                                                  user = None,
                                                  group = None)
            
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
                                                  user = None,
                                                  group = None)
            
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
                                                  user = None,
                                                  group = None)
            
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
                                                  user = 1,
                                                  group = None)
            
        expected_error_msg = "user is not a boolean or string."
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
                                                  user = None,
                                                  group = 1)
            
        expected_error_msg = "group is not a boolean or string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
