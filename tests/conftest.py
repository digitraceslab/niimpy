import os
import pytest
import tempfile
import zipfile
from niimpy import config

def pytest_addoption(parser):
    parser.addoption("--run_sentiment", action="store_true", default=False)

def create_zip(zip_filename):
    """ Compress the google takeout folder into a zip file"""
    test_zip = zipfile.ZipFile(zip_filename, mode="w")

    for dirpath,dirs,files in os.walk(config.GOOGLE_TAKEOUT_DIR):
        for f in files:
            filename = os.path.join(dirpath, f)
            filename_in_zip = filename.replace(config.GOOGLE_TAKEOUT_DIR, "")
            test_zip.write(filename, filename_in_zip)

    test_zip.close()


@pytest.fixture
def google_takeout_zipped():
    with tempfile.TemporaryDirectory() as ddir:
        zip_filename = os.path.join(ddir, "test.zip")
        create_zip(zip_filename)
        yield zip_filename
