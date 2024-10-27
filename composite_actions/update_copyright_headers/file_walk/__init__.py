"""
Recursively get all files to process. This takes into account:
- the file extensions for which Language objects are defined
- the patterns in the 'excludes' file.
"""
from file_walk.walk import get_exclude_patterns, get_relevant_files
