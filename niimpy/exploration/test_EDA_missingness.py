import pytest
from niimpy.EDA import setup_dataframe 
from niimpy.EDA import EDA_missingness


class TestEDAMissingness(object):
    
    def test_EDA_bar0(self):
        """
        Test EDA_missingness.bar function. The test fails when arguments:
            - data is not a pandas dataframe
    
        Returns
        -------
        None.
    
        """
         
        df = setup_dataframe.create_missing_dataframe()
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_missingness.bar(df.to_numpy())
            
        expected_error_msg = "df is not a pandas dataframe."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
    def test_EDA_bar(self):
        """
        Test EDA_missingness.bar function. The test fails when arguments:
            - data is not a pandas dataframe
    
        Returns
        -------
        None.
    
        """
         
        df = setup_dataframe.create_missing_dataframe()
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_missingness.bar(df.to_numpy())
            
        expected_error_msg = "df is not a pandas dataframe."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
    def test_EDA_matrix(self):
        """
        Test EDA_missingness.matrix function. The test fails when arguments:
            - data is not a pandas dataframe

        Returns
        -------
        None.

        """
        
        df = setup_dataframe.create_missing_dataframe()

        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_missingness.matrix(df.to_numpy())
        expected_error_msg = "df is not a pandas dataframe."
        
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
            