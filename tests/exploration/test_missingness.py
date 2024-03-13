import pytest
from niimpy.exploration import setup_dataframe 
from niimpy.exploration.eda import missingness

class TestEDAMissingness(object):
    
        
    def test_bar(self):
        """
        Test missingness.bar function. The test fails when arguments:
            - data is not a pandas dataframe
    
        Returns
        -------
        None.
    
        """
         
        df = setup_dataframe.create_missing_dataframe(nrows=60*24*30, ncols=5, density=0.2, index_type='dt', freq='min')
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            missingness.bar(df.to_numpy())
            
        expected_error_msg = "df is not a pandas dataframe."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
    def test_matrix(self):
        """
        Test missingness.matrix function. The test fails when arguments:
            - data is not a pandas dataframe

        Returns
        -------
        None.

        """
        
        df = setup_dataframe.create_missing_dataframe(nrows=60*24*30, ncols=5, density=0.2, index_type='dt', freq='min')

        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            missingness.matrix(df.to_numpy())
        expected_error_msg = "df is not a pandas dataframe."
        
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
            
    def test_bar_count_correct_ticks(self):
        """
        Test missingness.bar_count function. The test fails when arguments:
            - xticks is not defined correctly

        Returns
        -------
        None.

        """
        
        df = setup_dataframe.create_missing_dataframe(nrows=60*24*30, ncols=5, density=0.2, index_type='dt', freq='min')

        fig = missingness.bar_count(df, sampling_freq='h')
        
        ticktext = ("00:00:00", "01:00:00", "02:00:00", "03:00:00",
                     "04:00:00", "05:00:00", "06:00:00", "07:00:00",
                     "08:00:00", "09:00:00", "10:00:00", "11:00:00",
                     "12:00:00", "13:00:00", "14:00:00", "15:00:00",
                     "16:00:00", "17:00:00", "18:00:00", "19:00:00",
                     "20:00:00", "21:00:00", "22:00:00", "23:00:00")
        
        # Check if the raised ValueError contains the correct message
        assert fig.layout.xaxis.ticktext == ticktext