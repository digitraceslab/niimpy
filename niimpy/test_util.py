import os
import pytest

import niimpy
from .test_basic import DATA

def test_install_extensions(capsys):
    """Test the compiling of the extensions"""
    niimpy.util.install_extensions()
    assert os.path.exists(niimpy.util.SQLITE3_EXTENSIONS_FILENAME)
    outputs = capsys.readouterr()

    niimpy.open(DATA)
    outputs = capsys.readouterr()
    assert 'not available' not in outputs.err
    assert 'not available' not in outputs.out


#@pytest.mark.skip(reason="Don't excessively download, they may not like that")
def test_install_extensions_notpresent(capsys):
    """Test the compiling of the extensions"""
    def unlink_if_exists(x):
        if os.path.exists(x):
            os.unlink(x)
    unlink_if_exists(niimpy.util.SQLITE3_EXTENSIONS_FILENAME)
    unlink_if_exists(niimpy.util.SQLITE3_EXTENSIONS_FILENAME)
    # Test that it's really not there
    niimpy.open(DATA)
    outputs = capsys.readouterr()
    assert 'not available' in outputs.err


    niimpy.util.install_extensions()
    assert os.path.exists(niimpy.util.SQLITE3_EXTENSIONS_FILENAME), "Extension is missing after niimpy.util.install_extensions()"
    outputs = capsys.readouterr()
    assert not outputs.err
    assert 'not available' not in outputs.err, "We have the warning when trying to install extensions"

