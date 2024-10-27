"""
Update or insert new header into the file
"""
# Imports
import logging
from pathlib import Path
from typing import List

from content_updates.config import do_whitespace_surround
from content_updates.copyright_header.update_header import (
	get_creation_year_from_git,
	get_creation_year_from_header,
	get_current_header,
)
from content_updates.utils import has_shebang, whitespace_surround
from language_support import Language, get_language

def get_header_insert_line(text_lines: List[str], text_language: Language) -> int:
	"""
	Get the first line number in whose place it is safe to insert a new copyright header.
	
	- If the file has a shebang, it needs to go first.
	- If the file is in an xml-like language, the format declaration line needs to go first.
	"""
	
	res = 0
	if has_shebang(text_lines):
		res+=1
		
	if ".xml" in text_language.extensions:
		# if it is an xml like language, it absolutely needs to be after the format declaration line
		format_dec_line = -1
		for i, line in enumerate(text_lines):
			if "?>" in line or "?->" in line:
				format_dec_line = i
				break
				
		res = max(res, format_dec_line+1)
		
	if ".yml" in text_language.extensions:
		# for YAML, comments need to go after the document start marker ("---")
		format_dec_line = -1
		for i, line in enumerate(text_lines):
			if line.strip() == "---":
				format_dec_line = i
				break
				
		res = max(res, format_dec_line+1)
		
	return res
	
	
def add_header(text_lines: List[str], file_path: Path) -> List[str]:
	""" Insert a "new" header into the lines. Returns a new list."""
	creation_year = get_creation_year_from_git(file_path)
	header_lines = get_current_header(creation_year)
	
	file_language = get_language(file_path)
	insert_pos = get_header_insert_line(text_lines, file_language)
	
	commented_header_lines = file_language.comment_text_lines(
		header_lines, disable_multiline=True
	)
	
	before = text_lines[:insert_pos]
	after = text_lines[insert_pos:]
	
	out = before + commented_header_lines + after
	if do_whitespace_surround():
		logging.debug("Surrounding header with whitespace")
		whitespace_surround(
			out,
			block_start=insert_pos,
			block_end = insert_pos + len(commented_header_lines) -1,
		)
		
	return out
	
	
def update_header(
	text_lines: List[str],
	file_language: Language,
	start_line: int,
	end_line: int,
	in_multiline: bool,
) -> List[str]:
	"""
	Replace the text between start and end line with a copyright header
	Returns a new list.
	"""
	existing_header = text_lines[start_line: end_line + 1]
	logging.debug("Existing header : %s", existing_header)
	creation_year = get_creation_year_from_header(existing_header)
	
	header_lines = get_current_header(creation_year)
	
	if not in_multiline:
		commented_header_lines = file_language.comment_text_lines(
			# Don't create a multiline comment for header (at most 2 lines long)
			header_lines,
			disable_multiline=True,
		)
	else:
		commented_header_lines=header_lines
		
	# Sanity check in case of multiline comment
	# We need to make sure to re-add the multiline markers if they were included on the header lines
	# In that case they would have been deleted during the header update_header
	if in_multiline:
		#(in_multiline implies multiline_start !=None, so supress mypy warnings)
		if (
			existing_header[0]
			.strip()
			.startswith(file_language.multiline_start) # type : ignore
		):
			header_lines.insert(0, f"{file_language.multiline_start}\n")
		if (
			existing_header[-1]
			.strip()
			.startswith(file_language.multiline_end) # type : ignore
		):
			header_lines.append(f"{file_language.multiline_end}\n")
			
	out = text_lines.copy()
	
	out[start_line : end_line +1] = commented_header_lines
	
	# The value of end_line is not correct anumore as the header might be a different size
	end_line = start_line + len(commented_header_lines) -1
	
	if do_whitespace_surround():
		logging.debug("Surrounding header with whitespace")
		whitespace_surround(out, start_line, end_line)
		
	return out
