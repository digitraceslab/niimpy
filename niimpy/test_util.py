import os
import pytest

import niimpy

DATA = niimpy.sampledata.DATA

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
