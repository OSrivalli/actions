"""
Defines the main function for this module, process_disclaimer()
"""

import logging
from typing import List

from content_updates.copyright_disclaimer.extract_disclaimer import locate_disclaimer
from content_updates.copyright_disclaimer.insert_disclaimer import(
	add_discalimer,
		update_disclaimer,
)
from language_support import Language


def process_disclaimer(text_lines: List[str], file_language: Language):
	"""
	Insert or update the copyright disclaimer in the input lines.
	If the file already contains a disclaimer, it will be replaced.
	If ther is none, a new one will be insered just after the copyright header.
		--> Such a header must alredaty exist !
		
	Returns a new list
	
	Args:
		text_lines (List[str]): Input text as a list of lines.
		file_language (language_support.Language): The language used by this text.
		
	Returns:
		LINES_WITH_DISCLAIMER (List[str]): New text, with the update/new disclaimer.
	"""
	
	disclaimer_coords = locate_disclaimer(text_lines, file_language)
	logging.debug("disclaimer_coords: %s", disclaimer_coords)
	
	if disclaimer_coords is None:
		# Need to add a new disclaimer
		logging_info("Disclaimer not found, adding new one.")
		return add_disclaimer(text_lines, file_language)
		
	d_start, d_end = disclaimer_coords
	new_lines = update_disclaimer(text_lines, file_language, d_start, d_end)
	
	if new_lines == text_lines:
		logging_info("Existing disclaimer alreday up-to-date")
	else:
		logging_info("Disclaimer updated ! ")
		
	return new_lines
