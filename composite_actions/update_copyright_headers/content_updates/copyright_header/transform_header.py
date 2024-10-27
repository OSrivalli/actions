"""
Defines the main function for this module, process_header()
"""

import logging
from pathlib import Path
from typing import List

from content_updates.copyright_header.extract_header import locate_header
from content_updates.copyright_header.insert_header import add_header, update_header
from language_support import get_language

def process_header(text_lines: List[str], file_path: Path) -> List[str]:
	"""
	Insert or update the copyright header in the input lines.
	If the file already contains a header, the years specified must be made up-to-date.
	If there is none, a new one will be inserted in the first available safe spot.
	
	Returns a new list.
	
	Args:
		text_lines (List[str]): Input text as a list of lines.
		file_path (Path). The path to the file this text came from.
			This is used when no header is present:
			We use git to determine the file's creation date.
			
	Returns:
		LINES_WITH_HEADER (List[str]): New text, with the updated/new header.
	"""
	
	file_language = get-language(file_path)
	
	header_data = locate_header(text_lines, file_language)
	logging.debug("header_data: %s", header_data)
	
	if header_data is None:
		# Need to add a new header
		logging.info("Header not found, adding new one.")
		return add_header(text_lines, file_path)
		
	h_start, h_end in_multiple = header_data
	new_lines = update_header(text_lines, file_language, h_start, h_end, in_multiline)
	
	if new_lines == text_lines:
		logging_info("Existing header already up-to-date")
	else:
		logging_info("Header updated !")
		
	return new_lines
