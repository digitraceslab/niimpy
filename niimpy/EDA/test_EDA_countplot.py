import pytest
import numpy as np
import pandas as pd

from niimpy import setup_dataframe
from niimpy import EDA_countplot


class TestEDAcountplot(object):
    
    def test_EDA_countplot(self):
        """
        Test EDA_countplot. The test fails when arguments:
            - data is not a pandas dataframe
            - title is not a string
            - plot_type is not a string
            - points is not a string
            - aggregation is not a string
            - user is not a string or None type
            - column in not a string or None type
    
        Returns
        -------
        None.
    
        """
        df = setup_dataframe.create_dataframe()
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_countplot(df.to_numpy(), 
                          fig_title = 'Event counts plot', 
                          plot_type = 'count', 
                          points = 'all',
                          aggregation = 'group', 
                          user = None, 
                          column = None)
        expected_error_msg = "df is not a pandas dataframe."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_countplot(df, 
                          fig_title = int(1), 
                          plot_type = 'count', 
                          points = 'all',
                          aggregation = 'group', 
                          user = None, 
                          column = None)
        expected_error_msg = "Title is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_countplot(df, 
                          fig_title = 'Event counts plot', 
                          plot_type = int(1), 
                          points = 'all',
                          aggregation = 'group', 
                          user = None, 
                          column = None)
        expected_error_msg = "plot_type is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_countplot(df, 
                          fig_title = 'Event counts plot', 
                          plot_type = 'count', 
                          points = int(100),
                          aggregation = 'group', 
                          user = None, 
                          column = None)
        expected_error_msg = "points is not a string"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_countplot(df, 
                          fig_title = 'Event counts plot', 
                          plot_type = 'count', 
                          points = 'all',
                          aggregation = int(1), 
                          user = None, 
                          column = None)
        expected_error_msg = "aggregation is not a string"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)

        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_countplot(df, 
                          fig_title = 'Event counts plot', 
                          plot_type = 'count', 
                          points = 'all',
                          aggregation = 'group', 
                          user = int(1), 
                          column = None)
        expected_error_msg = "user is not a string or None type."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_countplot(df, 
                          fig_title = 'Event counts plot', 
                          plot_type = 'count', 
                          points = 'all',
                          aggregation = 'group', 
                          user = None, 
                          column = int(1))
        expected_error_msg = "column in not a string or None type."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
      
    def test_EDA_boxplot(self):
        """
        Test EDA_boxplot function. The test fails when arguments:
            - df is not a pandas dataframe
            - points is not a string
            - y is not a string
            - Title is not a string
            - Xlabel is not a string
            - Ylabel is not a string
    
        Returns
        -------
        None.
    
        """
        df = setup_dataframe.create_dataframe()
        n_events = df[['group', 'user']].groupby(['user', 'group']).size()
        n_events = n_events.to_frame()
        n_events.columns = ['values']
        n_events = n_events.reset_index()
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_boxplot_(n_events.to_numpy(),
                                       fig_title = 'test_title',
                                       points = 'all',
                                       y = 'values',
                                       xlabel="Group",
                                       ylabel="Count")
            
        expected_error_msg = "df is not a pandas dataframe."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_boxplot_(n_events,
                                       fig_title = 'test_title',
                                       points = int(1),
                                       y = 'values',
                                       xlabel="Group",
                                       ylabel="Count")
            
        expected_error_msg = "points is not a string"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_boxplot_(n_events,
                                       fig_title = 'test_title',
                                       points = 'all',
                                       y = int(1),
                                       xlabel="Group",
                                       ylabel="Count")
            
        expected_error_msg = "y is not a string"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_boxplot_(n_events,
                                       fig_title = int(1),
                                       points = 'all',
                                       y = 'values',
                                       xlabel="Group",
                                       ylabel="Count")
            
        expected_error_msg = "Title is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_boxplot_(n_events,
                                       fig_title = 'test_title',
                                       points = 'all',
                                       y = 'values',
                                       xlabel = int(1),
                                       ylabel = "Count")
            
        expected_error_msg = "Xlabel is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_boxplot_(n_events,
                                       fig_title = 'test_title',
                                       points = 'all',
                                       y = 'values',
                                       xlabel = "Group",
                                       ylabel = int(1))
            
        expected_error_msg = "Ylabel is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
       
    def test_EDA_barplot(self):
        """
        Test EDA_boxplot function. The test fails when arguments:
            - df is not a pandas dataframe
            - Title is not a string
            - Xlabel is not a string
            - Ylabel is not a string
    
        Returns
        -------
        None.
    
        """
        df = setup_dataframe.create_dataframe()
        n_events = df[['user']].groupby(['user']).size()
        n_events = n_events.to_frame()
        n_events.columns = ['values']
        n_events = n_events.reset_index()
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_barplot_(n_events.to_numpy(), 
                         fig_title = 'test_title', 
                         xlabel="User",
                         ylabel="Count")
        expected_error_msg = "df is not a pandas dataframe."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_barplot_(n_events, 
                         fig_title = int(1), 
                         xlabel="User",
                         ylabel="Count")
        expected_error_msg = "Title is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_barplot_(n_events, 
                         fig_title = 'test_title', 
                         xlabel = int(1),
                         ylabel = "Count")
        expected_error_msg = "Xlabel is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_countplot.EDA_barplot_(n_events, 
                         fig_title = 'test_title', 
                         xlabel = "User",
                         ylabel = int(1))
        expected_error_msg = "Ylabel is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
