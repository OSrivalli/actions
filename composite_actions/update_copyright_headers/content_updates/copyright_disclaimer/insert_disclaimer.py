"""
Insert a new disclaimer into the file, replacing the one already present if it exists.
"""
# pylint: disable-locally-disabled, unspecified-encoding, global-statement

from pathlib import Path
# Imports
from typing import List, Optional, Union
from content_updates.config import do_whitespace_surround
from content_updates.copyright _header.extract_header import locate_header
from content_updates.utils import whitespace_surround
from language_support import Language

# Globals
DISCLAIMER_LINES: Union[None, List[str]] = None


def get_disclaimer_text(
	disclaimer_file_path: Optional[Union[str, Path]] = None,
) -> List[str]:
	"""
	Load the copyright disclaimer text from the specified file.
	The file is only read on the first call to this function, the value is then cached.
	The return value is a list of all lines in the file.
	
	Args:
		disclaimer_file_path (Union[str, Path], optional): Path to a disclaimer file to load.
			Needs to be specified at least on the first call to the function.
			
	Returns:
		DISCLAIMER_LINES (List[str]): Lines from the disclaimer file.
	"""
	global DISCLAIMER_LINES
	if DISCLAIMER_LINES is not None:
		return DISCLAIMER_LINES
		
	if disclaimer_file_path is None:
		raise ValueError(
			"Disclaimer text is not loaded yet ! Please specify a 'disclaimer_file_path'."
		)
		
	with open(disclaimer_file_path) as disclaimer_file:
		DISCLAIMER_LINES = disclaimer_file.readlines()
		
	return DISCLAIMER_LINES
	
	
def get_disclaimer_insert_line(text_lines: List[str], file_language: Language) -> int:
	"""
	Get the smallest line index into which it is safe to insert a new disclaimer.
	The file needs to already have a copyright header: we always insert the disclaimer right after.
	"""
	
	header_pos = locate_header(text_lines, file_language)
	
	if header_pos is None:
		raise ValueError(
			"Please insert a copyright header before trying to insert the disclaimer !"
		)
		
	_, header_end, _=header_pos
	
	return header_end + 1
	
	
def add_disclaimer(text_lines: List[str], file_language: Language) -> List[str]:
	"""Insert a "new" disclaimer into the lines. Returns a new list."""
	
	insert_pos = get_disclaimer_insert_line(text_lines, file_language)
	
	disclaimer_lines = get_disclaimer_text()
	commented_disclaimer_lines = file_language.comment_text_lines(disclaimer_lines)
	
	before = text_lines[:insert_pos]
	after = text_lines[insert_pos:]
	
	out = before + commented_disclaimer_lines + after
	
	if do_whitespace_surround():
		whitespace_surround(
			out,
			block_start=insert_pos,
			block_end=insert_pos + len(commented_disclaimer_lines) -1,
		)
		
	return out
	
	
def update_disclaimer(
	text_lines: List[str], file_language: Language, start_line: int, end_line: int
) -> List[str]:
	"""Replace the text between start_line and end_line with a disclaimer. Return a new list."""
	out = text_lines.copy()
	
	disclaimer_lines = get_disclaimer_text()
	commented_disclaimer_lines = file_language.comment_text_lines(disclaimer_lines)
	
	out[start_line : end_line + 1] = commented_disclaimer_lines
	
	# The value of end_line is not correct anymore as the disclaimer might be a different size
	end_line = start_line + len(commented_disclaimer_lines) - 1
	
	if do_whitespace_surround():
		whitespace_surround(out, start_line, end_line)
		
	return out
