import pytest
from niimpy.EDA import setup_dataframe
from niimpy.EDA import EDA_punchcard


class TestEDApunchcard(object):
    
    def test_EDA_punchcard(self):
        """   
        Returns
        -------
        None.
    
        """
        df = setup_dataframe.create_dataframe()
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_punchcard.punchcard_plot(df.to_numpy(),
                                         user_list = ['user_1'],
                                         columns = ['col_1'],
                                         title = 'title',
                                         resample = 'D',
                                         normalize = False,
                                         timerange = ('20190125','20190701'))
                                                  
        expected_error_msg = "df is not a pandas dataframe."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_punchcard.punchcard_plot(df,
                                         user_list = 1,
                                         columns = ['col_1'],
                                         title = 'title',
                                         resample = 'D',
                                         normalize = False,
                                         timerange = ('20190125','20190701'))
                                                  
        expected_error_msg = "user_list is not a list or None."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_punchcard.punchcard_plot(df,
                                         user_list = ['user_1'],
                                         columns = 1,
                                         title = 'title',
                                         resample = 'D',
                                         normalize = False,
                                         timerange = ('20190125','20190701'))
                                                  
        expected_error_msg = "columns is not a list or None"
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_punchcard.punchcard_plot(df,
                                         user_list = ['user_1'],
                                         columns = ['col_1'],
                                         title = 1,
                                         resample = 'D',
                                         normalize = False,
                                         timerange = ('20190125','20190701'))
                                                  
        expected_error_msg = "title is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_punchcard.punchcard_plot(df,
                                         user_list = ['user_1'],
                                         columns = ['col_1'],
                                         title = 'title',
                                         resample = 1,
                                         normalize = False,
                                         timerange = ('20190125','20190701'))
                                                  
        expected_error_msg = "resample is not a string."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_punchcard.punchcard_plot(df,
                                         user_list = ['user_1'],
                                         columns = ['col_1'],
                                         title = 'title',
                                         resample = 'D',
                                         normalize = 'False',
                                         timerange = ('20190125','20190701'))
                                                  
        expected_error_msg = "normalize is not a boolean."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
        
        # Store information about raised ValueError in exc_info
        with pytest.raises(AssertionError) as exc_info:
            EDA_punchcard.punchcard_plot(df,
                                         user_list = ['user_1'],
                                         columns = ['col_1'],
                                         title = 'title',
                                         resample = 'D',
                                         normalize = False,
                                         timerange = ['20190125','20190701'])
                                                  
        expected_error_msg = "timerange is not a boolean or tuple."
        # Check if the raised ValueError contains the correct message
        assert exc_info.match(expected_error_msg)
