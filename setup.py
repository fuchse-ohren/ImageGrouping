from distutils.core import setup
import py2exe, os, sys
 
setup(
options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
console = [{'script': 'C:\\\\Users\\admin\\Desktop\\ImageGrouping\\ImageGrouping.py'}],
zipfile = None,
)