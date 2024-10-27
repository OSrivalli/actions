"""
Check file to see if it contaons a copyright header, and extract its position
"""

# Imports
import re
from typing import List, Tuple, Union

from content_updates.utils import YEAR_RANGE_REGEX
from language_support import Language, get_commented_blocks

# Globals

# A commented line matching this regex in the input file will be considered a "copyright header".
# The structure is

# 1. Any amount of white space
# 2. 0-5 non-whitespace, accounting for the comment marker
# 3. Any amount of whitespace
# 4. Optionally a '(c)' marker
# 5. The word "Copyright"
# 6. A year range or a single year
# 7. A company name ("XYZ", "ABC" or "Advanced ABC")
# Any text until the end of the line (usually " Inc. All rights reserved.")
# The regex is not case sensitive
# Note the use of a raw f-string (rf) forcing us to use {{}} in the beginning
EXISTING_HEADER_REGEX = re.compile(
	#pylint: disable-next=line-too-long
	#rf"^\s*\S{{0,5}}\s*(?:\(C\))? Copyright (?P<year_range>{YEAR_RANGE_REGEX}) (?:XYZ|ABC|Advanced ABC).*$",
	#flags=re.IGNORECASE,
	rf"^\s*\S{{0,5}}\s* Copyright (?:\(c\))? (?P<year_range>{YEAR_RANGE_REGEX}) (?:XYZ|ABC|Advanced ABC).*$"
	flags=re.IGNORECASE,
)

	
def locate_header(
	text_lines: List[str], text_language: Language
) -> Union[None, Tuple[int, int, bool]]:
	"""
	Returns the start and end lines of the copyright header if it exists.
	It might be part of a multiline comment block - then the third element of the tuple will be True.
	If no header exists, return None.
	"""
	commented_blocks = get_commented_blocks(text_lines, text_language)
	header_block_cords = []
	
	for block in commented_blocks:
		block_start, _, block_text, block_is_multiline = block
		
		# The header might be part of a larger block which contains other things
		# (For example it might be attached to the disclaimer or shebang)
		# Try to extract a header from a block
		# If the header is non continguous, they will get extracted as 2 distinct headers.
		# This will raise an error lower in the function.
		
		buff: List[int] = []
		for i, line in enumerate(block_text):
			if re.match(EXISTING_HEADER_REGEX, line):
				buff.append(i)
				continue
			
			# If the line does not match, flush the buffer if it is full
			if buff:
				header_block_cords.append(
					(block_start + buff[0], block_start + buff[-1], block_is_multiline)
				)
				buff = []
				
		# Buffer might still be full
		if buff:
			header_block_cords.append(
				(block_start + buff[0], block_start + buff[-1], block_is_multiline)
			)	
			
	if not header_block_cords:
		# No header was found
		return None
		
	if len(header_block_cords) > 1:
		# More than 1 header was found	
		raise ValueError("Multiple headers found in the file ~")
		
	header_start, header_end, in_multiple_block = header_block_cords[0]
	return header_start, header_end, in_multiple_block
		
