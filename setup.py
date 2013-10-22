
from distutils.core import setup
import py2exe

setup(
    options = {'py2exe': {'bundle_files': 1, 'compressed': 1,\
                          "dll_excludes": ["MSVCP90.dll"]}},
    zipfile = None,
    # replace console with windows for a GUI program
    # console = [{'script':'buttons.py'}]
    windows = [{'script':'buttons.py'}]
)

