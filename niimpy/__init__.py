from ._version import __version__

from .database import open, Data1, ALL
from . import util
from . import sampledata
from .read import read_sqlite
from .read import read_csv