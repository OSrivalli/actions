"""
Helper functions reused throughout the module
"""
# Imports
from typing import List, Optional, Tuple

# Globals
# Matches either a single year or a year range
YEAR_RANGE_REGEX = r"[0-9]{4}(?: ?- ?[0-9]{4})?"


# Helper functions
def whitespace_surround(
	text_lines: List[str], block_start: int, block_end: int
) -> None:
	"""
	Surround the lines between block_start and block_end by newlines.
	Modifies the input in-place.
	"""
	if block_start > 0:
		if text_lines[block_start -1].strip() != "":
			text_lines.insert(block_start, "\n")
			
			# We have just added a line to text_lines before the block:
			# need to increment block_end (and block_start but is unused)
			block_end += 1
			
	if block_end < len(text_lines) -1:
		if text_lines[block_end +1].strip() != "":
			text_lines.insert(block_end +1, "\n")
			
			
def has_shebang(text_lines: List[str]) -> bool:
	"""Returns True if the input lines starts with a shebang line."""
	if not text_lines:
		# Edge case for empty input
		return False
	return text_lines[0].startswith("#!")
	
	
def date_range(start_year: int, end_year: Optional[int] = None) -> str:
	"""Format years as a range (ex: 2022-2023). If both are equal, return it on its own ("2022")."""
	if end_year is None or start_year == end_year:
		return str(start_year)
		
	if start_year > end_year:
		raise ValueError("'end' must be greater than 'start' !")
		
	return f"{start_year} - {end_year}"
	
	
def parse_year_range(range_str: str) -> Tuple[int,int]:
	"""Parse a year range (or single year) and return its endpoints."""
	splits = range_str.split("-")
	if len(splits) == 1:
		out = int(splits[0].strip())
		return out, out
		
	if len(splits) > 2:
		raise ValueError("Could not parse date range")
		
	return int(splits[0].strip()), int(splits[1].strip())
