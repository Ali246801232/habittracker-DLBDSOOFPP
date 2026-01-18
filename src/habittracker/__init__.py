# habittracker/__init__.py
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("habittracker")
except PackageNotFoundError:
    __version__ = "0.0.0"
