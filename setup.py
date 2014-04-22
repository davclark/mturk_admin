from setuptools import setup

# The following functionality cribbed from:
# https://github.com/pypa/sampleproject/blob/master/setup.py
import re, codecs, os

here = os.path.abspath(os.path.dirname(__file__))

# Read the version number from a source file.
def find_version(*file_paths):
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    with codecs.open(os.path.join(here, *file_paths), 'r', 'latin1') as f:
        version_file = f.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(name = 'mturk_admin',
      version = find_version('mturk_admin', '__init__.py') )
