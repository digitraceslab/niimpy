import os
import pytest
import pandas as pd
import numpy as np
import niimpy
from niimpy.exploration import setup_dataframe 

DATA = niimpy.sampledata.DATA

@pytest.mark.skip(reason="ignoring extensions for now")
def test_install_extensions(capsys):
    """Test the compiling of the extensions"""
    niimpy.util.install_extensions()
    assert os.path.exists(niimpy.util.SQLITE3_EXTENSIONS_FILENAME)
    outputs = capsys.readouterr()

    niimpy.open(DATA)
    outputs = capsys.readouterr()
    assert 'not available' not in outputs.err
    assert 'not available' not in outputs.out
    niimpy.util.uninstall_extensions()


#@pytest.mark.skip(reason="Don't excessively download, they may not like that")
@pytest.mark.skip(reason="ignoring extensions for now")
def test_install_extensions_notpresent(capsys):
    """Test the compiling of the extensions"""
    niimpy.util.uninstall_extensions()
    # Test that it's really not there
    niimpy.open(DATA)
    outputs = capsys.readouterr()
    assert 'not available' in outputs.err, "Extensions did not uninstall"

    niimpy.util.install_extensions()
    assert os.path.exists(niimpy.util.SQLITE3_EXTENSIONS_FILENAME), "Extension is missing after niimpy.util.install_extensions()"
    outputs = capsys.readouterr()
    assert not outputs.err
    assert 'not available' not in outputs.err, "We have the warning when trying to install extensions"
    niimpy.util.uninstall_extensions()

# TODO: add test for util.aggregate
def test_aggregate_correct_frequency():
    
    df = setup_dataframe.create_timeindex_dataframe(nrows=120, ncols=6, freq='min')
    df['user'] = 1234
    res_df = niimpy.util.aggregate(df, method_categorical='mode', freq='h')
    
    m = res_df.loc[[pd.Timestamp('2022-01-01 00:00:00'), pd.Timestamp('2022-01-01 01:00:00')]].index
    np.testing.assert_array_equal(res_df.index , m)
