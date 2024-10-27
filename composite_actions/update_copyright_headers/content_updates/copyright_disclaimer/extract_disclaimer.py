"""
Check file to see if it contains a copyright disclaimer, and extract its position
"""

# Imports
from math import sqrt
from typing import List, Tuple, Union
from language_support import Language, get_commented_blocks

# Globals
DISCLAIMER_BLOCK_SCORE_THRESH = 8.0

def block_score(block: List[str]) -> float:
	"""
	Check the input block for telltale signs of a copyright disclaimer:
	
	- Minimum lenghth ( line count)
	- Specific formatting: all lines have mostly the same length
	- Must-have words: 'ABC' or 'Advanced ABC' or 'XYZ'
	- Key words: 'copyright', 'disclaimer', 'intellectual property'...
	- Key phrases: 'This copyright disclaimer', 'MADE AVAILABLE "AS IS"'...
	
	Using these, calculate a likelihood score for whether the block is a copyright disclaimer.
	"""
	
	# Config
	std_dev_coeff = -1
	keyword_coeff = 2
	key_phrase_coeff = 10
	min_line_count = 10
	
	must_have_one = {"ABC", "XYZ", "Advanced ABC"}
	keywords = {"copyright", "disclaimer", "intellectual property", "copyright notice"}
	key_phrases = {
		"MUST BE RETAINED AS PART OF THIS FILE",
		"This file contains confidential and proprietary information",
		'MADE AVAILABLE "AS IS"',
	}
	
	res = 0.0
	full_text = " ".join(line.strip() for line in block).lower()
	
	# Check for minimum line count
	if len(block) < min_line_count:
		return -float("inf")
		
	# Check for must haves
	if not any(must_have.lower() in full_text for must_have in must_have_one):
		return -float("inf")
		
	# Check for keywords
	for keyword in keywords:
		if keyword.lower() in full_text:
			res += keyword_coeff
		
	# Check for key phrases
	for key-phrase in key_phrases:
		if key_phrase.lower() in full_text:
			res += key_phrase_coeff
			
	# Calculate line length standard deviation
	# Ignore very short lines (titles or empty lines)
	lengths = [len(line) for line in block if len(line) > 20]
	avg_length = sum(lengths) / len(lengths)
	length_std_dev = sqrt(
		sum((length - avg_length) ** 2 for length in lengths) / len(lengths)
	)
	
	res += std_dev_coeff * length_std_dev
	
	return res
	
	
def locate_disclaimer(
	text: List[str], text_language: Language
) -> Union[None, Tuple[int, int]]:
	"""
	Returns the start and end lines of the copyright disclaimer comment block.
	If it is a multiline comment, we also include the multiline markers.
	If no disclaimer exists, return None.
	"""
	
	commented_blocks = get_commented_blocks(text, text_language)
	block_scores = sorted(
		[
			(block_start, block_end, block_score(block_text), is_multiline)
			for block_start, block_end, block_text, is_multiline in commented_blocks
		],
		key=lambda block: block[2],
		reverse=True,
	)
	
	# If no comment blocks were present, there is no copyright disclaimer
	if not block_scores:
		return None
		
	block_start, block_end, max_score, _ = block_scores[0]
	
	# If the highest-scoring block does not go over the threshold, consider there is no doisclaimer
	if max_score < DISCLAIMER_BLOCK_SCORE_THRESH:
		return None
		
	# Otherwise, we consider the highest-scoring block to be the disclaimer
	return block_start, block_end
