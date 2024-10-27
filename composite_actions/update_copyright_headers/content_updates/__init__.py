"""
Contains all logic for updating the copyright headers / disclaimer on  a given file:
- Updating the date
- Adding the header without breaking the file
- Adding the disclaimer if  needed 

We always assume the copyright header is alone on its line (with the appropriate comment markers)
"""

from content_updates.config import set_whitespace_surround
from content_updates.copyright_disclaimer import get_disclaimer_text
from content_updates.process_file import process_file
