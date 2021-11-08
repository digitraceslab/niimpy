"""
Created on Tue Nov  2 13:57:00 2021

@author: arsii
"""


import pytest
from setup_dataframe import create_dataframe
import EDA_lineplot

class TestEDAlineplot(object):
    
    def test_EDA_lineplot(self):
        """
        Test EDA_countplot function. The test fails when arguments:
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
         
        df = create_dataframe()
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_lineplot.timeplot(df.to_numpy(),
                         users = ['user_1'],
                         columns = ['col_1'],
                         title = 'title',
                         xlabel = 'xlabel',
                         ylabel = 'ylabel',
                         resample = False,
                         interpolate = False,
                         window = 3)
            
        expected_error_msg = "df is not a pandas dataframe."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        

        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_lineplot.timeplot(df,
                         users = int(1),
                         columns = ['col_1'],
                         title = 'title',
                         xlabel = 'xlabel',
                         ylabel = 'ylabel',
                         resample = False,
                         interpolate = False,
                         window = 3)
            
        expected_error_msg = "users is not a string or a list"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
       
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_lineplot.timeplot(df,
                         users = ['user_1'],
                         columns = int(1),
                         title = 'title',
                         xlabel = 'xlabel',
                         ylabel = 'ylabel',
                         resample = False,
                         interpolate = False,
                         window = 3)
            
        expected_error_msg = "column is not a string or a list"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_lineplot.timeplot(df,
                         users = ['col_1'],
                         columns = ['col_1'],
                         title = int(1),
                         xlabel = 'xlabel',
                         ylabel = 'ylabel',
                         resample = False,
                         interpolate = False,
                         window = 3)
            
        expected_error_msg = "title is not a string"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_lineplot.timeplot(df,
                         users = ['col_1'],
                         columns = ['col_1'],
                         title = 'title',
                         xlabel = int(1),
                         ylabel = 'ylabel',
                         resample = False,
                         interpolate = False,
                         window = 3)
            
        expected_error_msg = "xlabel is not a string"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_lineplot.timeplot(df,
                         users = ['col_1'],
                         columns = ['col_1'],
                         title = 'title',
                         xlabel = 'xlabel',
                         ylabel = int(1),
                         resample = False,
                         interpolate = False,
                         window = 3)
            
        expected_error_msg = "ylabel is not a string"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_lineplot.timeplot(df,
                         users = ['col_1'],
                         columns = ['col_1'],
                         title = 'title',
                         xlabel = 'xlabel',
                         ylabel = 'ylabel',
                         resample = int(1),
                         interpolate = False,
                         window = 3)
            
        expected_error_msg = "resample is not a string or a boolean"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_lineplot.timeplot(df,
                         users = ['col_1'],
                         columns = ['col_1'],
                         title = 'title',
                         xlabel = 'xlabel',
                         ylabel = 'ylabel',
                         resample = 'D',
                         interpolate = 'False',
                         window = 3)
            
        expected_error_msg = "interpolate is not a boolean"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)

        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_lineplot.timeplot(df,
                         users = ['col_1'],
                         columns = ['col_1'],
                         title = 'title',
                         xlabel = 'xlabel',
                         ylabel = 'ylabel',
                         resample = 'D',
                         interpolate = False,
                         window = '3')
            
        expected_error_msg = "window is not an int"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        
        with pytest.raises(AssertionError) as exc_info:
            EDA_lineplot.timeplot(df,
                         users = ['user_1'],
                         columns = ['col_1'],
                         title = 'title',
                         xlabel = 'xlabel',
                         ylabel = 'ylabel',
                         resample = False,
                         interpolate = False,
                         window = 3,
                         reset_index='False', 
                         by=False)
            
        expected_error_msg = "reset_index is not boolean"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        
        
        with pytest.raises(AssertionError) as exc_info:
            EDA_lineplot.timeplot(df,
                         users = ['user_1'],
                         columns = ['col_1'],
                         title = 'title',
                         xlabel = 'xlabel',
                         ylabel = 'ylabel',
                         resample = False,
                         interpolate = False,
                         window = 3,
                         reset_index = False, 
                         by = int(1))
            
        expected_error_msg = "by is not a string or a boolean"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        def test_EDA_plot_averages(self):
            """
            Test EDA_lineplot.plot_averages_ function. The test fails when arguments:
                - data is not a pandas dataframe
                - columns a is not a string or a list
                - by in not a string or a boolean

            Returns
            -------
            None.

            """
            
            df = create_dataframe()

            # Store information about raised ValueError in exc_info
            with pytest.raises(AssertionError) as exc_info:
                EDA_lineplot.plot_averages_(df.to_numpy(),
                                            columns = 'col_1',
                                            by = 'weekday')
            expected_error_msg = "df is not a pandas dataframe."
            # Check if the raised ValueError contains the correct message
            assert exc_info.match(expected_error_msg)
            
            # Store information about raised ValueError in exc_info
            with pytest.raises(AssertionError) as exc_info:
                EDA_lineplot.plot_averages_(df,
                                            columns = int(1),
                                            by = 'weekday')
            expected_error_msg = "column is not a string"
            # Check if the raised ValueError contains the correct message
            assert exc_info.match(expected_error_msg)
            
            # Store information about raised ValueError in exc_info
            with pytest.raises(AssertionError) as exc_info:
                EDA_lineplot.plot_averages_(df,
                                            columns = 'col_1',
                                            by = int(1))
            expected_error_msg = "by is not a string"
            # Check if the raised ValueError contains the correct message
            assert exc_info.match(expected_error_msg)

    def test_EDA_plot_timeseries(self):
            """
            Test EDA_lineplot.plot_averages_ function. The test fails when arguments:
                - data is not a pandas dataframe
                - columns a is not a string or a list
                - by in not a string or a boolean

            Returns
            -------
            None.

            """
                        
            df = create_dataframe()

            # Store information about raised ValueError in exc_info
            with pytest.raises(AssertionError) as exc_info:
                EDA_lineplot.plot_timeseries_(df.to_numpy(), 
                                              columns=['Col_1'],
                                              users=['user_1'],
                                              title='title',
                                              xlabel='xlabel',
                                              ylabel='ylabel',
                                              resample=False,
                                              interpolate=False,
                                              window_len=3,
                                              reset_index=False)

            expected_error_msg = "df is not a pandas dataframe."
            # Check if the raised ValueError contains the correct message
            assert exc_info.match(expected_error_msg)
            
            # Store information about raised ValueError in exc_info
            with pytest.raises(AssertionError) as exc_info:
                EDA_lineplot.plot_timeseries_(df.to_numpy(), 
                                              columns=['Col_1'],
                                              users=['user_1'],
                                              title='title',
                                              xlabel='xlabel',
                                              ylabel='ylabel',
                                              resample=False,
                                              interpolate=False,
                                              window_len=3,
                                              reset_index=False)

            expected_error_msg = "users is not a string or a list"
            # Check if the raised ValueError contains the correct message
            assert exc_info.match(expected_error_msg)
            
            # Store information about raised ValueError in exc_info
            with pytest.raises(AssertionError) as exc_info:
                EDA_lineplot.plot_timeseries_(df.to_numpy(), 
                                              columns=['Col_1'],
                                              users=['user_1'],
                                              title='title',
                                              xlabel='xlabel',
                                              ylabel='ylabel',
                                              resample=False,
                                              interpolate=False,
                                              window_len=3,
                                              reset_index=False)

            expected_error_msg = "column is not a string or a list"
            # Check if the raised ValueError contains the correct message
            assert exc_info.match(expected_error_msg)
            
            # Store information about raised ValueError in exc_info
            with pytest.raises(AssertionError) as exc_info:
                EDA_lineplot.plot_timeseries_(df.to_numpy(), 
                                              columns=['Col_1'],
                                              users=['user_1'],
                                              title='title',
                                              xlabel='xlabel',
                                              ylabel='ylabel',
                                              resample=False,
                                              interpolate=False,
                                              window_len=3,
                                              reset_index=False)

            expected_error_msg = "title is not a string"
            # Check if the raised ValueError contains the correct message
            assert exc_info.match(expected_error_msg)
            
            # Store information about raised ValueError in exc_info
            with pytest.raises(AssertionError) as exc_info:
                EDA_lineplot.plot_timeseries_(df.to_numpy(), 
                                              columns=['Col_1'],
                                              users=['user_1'],
                                              title='title',
                                              xlabel='xlabel',
                                              ylabel='ylabel',
                                              resample=False,
                                              interpolate=False,
                                              window_len=3,
                                              reset_index=False)

            expected_error_msg = "xlabel is not a string"
            # Check if the raised ValueError contains the correct message
            assert exc_info.match(expected_error_msg)
            
            # Store information about raised ValueError in exc_info
            with pytest.raises(AssertionError) as exc_info:
                EDA_lineplot.plot_timeseries_(df.to_numpy(), 
                                              columns=['Col_1'],
                                              users=['user_1'],
                                              title='title',
                                              xlabel='xlabel',
                                              ylabel='ylabel',
                                              resample=False,
                                              interpolate=False,
                                              window_len=3,
                                              reset_index=False)

            expected_error_msg = "ylabel is not a string"
            # Check if the raised ValueError contains the correct message
            assert exc_info.match(expected_error_msg)
            
            # Store information about raised ValueError in exc_info
            with pytest.raises(AssertionError) as exc_info:
                EDA_lineplot.plot_timeseries_(df.to_numpy(), 
                                              columns=['Col_1'],
                                              users=['user_1'],
                                              title='title',
                                              xlabel='xlabel',
                                              ylabel='ylabel',
                                              resample=False,
                                              interpolate=False,
                                              window_len=3,
                                              reset_index=False)

            expected_error_msg = "df is not a pandas dataframe."
            # Check if the raised ValueError contains the correct message
            assert exc_info.match(expected_error_msg)
            
            # Store information about raised ValueError in exc_info
            with pytest.raises(AssertionError) as exc_info:
                EDA_lineplot.plot_timeseries_(df.to_numpy(), 
                                              columns=['Col_1'],
                                              users=['user_1'],
                                              title='title',
                                              xlabel='xlabel',
                                              ylabel='ylabel',
                                              resample=False,
                                              interpolate=False,
                                              window_len=3,
                                              reset_index=False)

            expected_error_msg = "df is not a pandas dataframe."
            # Check if the raised ValueError contains the correct message
            assert exc_info.match(expected_error_msg)
            
            # Store information about raised ValueError in exc_info
            with pytest.raises(AssertionError) as exc_info:
                EDA_lineplot.plot_timeseries_(df.to_numpy(), 
                                              columns=['Col_1'],
                                              users=['user_1'],
                                              title='title',
                                              xlabel='xlabel',
                                              ylabel='ylabel',
                                              resample=False,
                                              interpolate=False,
                                              window_len=3,
                                              reset_index=False)

            expected_error_msg = "df is not a pandas dataframe."
            # Check if the raised ValueError contains the correct message
            assert exc_info.match(expected_error_msg)
            
            # Store information about raised ValueError in exc_info
            with pytest.raises(AssertionError) as exc_info:
                EDA_lineplot.plot_timeseries_(df.to_numpy(), 
                                              columns=['Col_1'],
                                              users=['user_1'],
                                              title='title',
                                              xlabel='xlabel',
                                              ylabel='ylabel',
                                              resample=False,
                                              interpolate=False,
                                              window_len=3,
                                              reset_index=False)

            expected_error_msg = "df is not a pandas dataframe."
            # Check if the raised ValueError contains the correct message
            assert exc_info.match(expected_error_msg)

