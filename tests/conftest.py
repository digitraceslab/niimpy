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


@pytest.fixture
def google_portability_zip():
    """Create a temporary zip file mimicking a Google Portability export."""
    portability_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "niimpy", "sampledata", "Google", "Portability"
    )
    base_dir = os.path.dirname(portability_dir)  # .../Google/
    with tempfile.TemporaryDirectory() as ddir:
        zip_path = os.path.join(ddir, "portability_test.zip")
        with zipfile.ZipFile(zip_path, mode="w") as zf:
            for dirpath, dirs, files in os.walk(portability_dir):
                for fname in files:
                    full_path = os.path.join(dirpath, fname)
                    arcname = os.path.relpath(full_path, base_dir)
                    zf.write(full_path, arcname)
        yield zip_path


@pytest.fixture
def google_portability_no_subtitles_zip():
    """Zip with YouTube data that has no subtitles field (all other data same)."""
    portability_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "niimpy", "sampledata", "Google", "Portability_no_subtitles"
    )
    base_dir = os.path.dirname(portability_dir)  # .../Google/
    with tempfile.TemporaryDirectory() as ddir:
        zip_path = os.path.join(ddir, "portability_no_subtitles.zip")
        with zipfile.ZipFile(zip_path, mode="w") as zf:
            for dirpath, dirs, files in os.walk(portability_dir):
                for fname in files:
                    full_path = os.path.join(dirpath, fname)
                    arcname = os.path.relpath(full_path, base_dir)
                    # Remap Portability_no_subtitles -> Portability in arcname
                    arcname = arcname.replace("Portability_no_subtitles", "Portability", 1)
                    zf.write(full_path, arcname)
        yield zip_path


@pytest.fixture
def empty_portability_zip():
    """Create an empty zip file for missing-data tests."""
    with tempfile.TemporaryDirectory() as ddir:
        zip_path = os.path.join(ddir, "empty.zip")
        zipfile.ZipFile(zip_path, mode="w").close()
        yield zip_path
