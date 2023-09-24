from distutils.core import setup
import py2exe, os, sys
 
setup(
options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
console = [{'script': 'ImageGrouping.py'}],
zipfile = None,
)