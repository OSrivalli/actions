"""Load the languages configs, specify how to handle each languages comments."""

# pylint: disable=loclly-dsiabled, unspecified-encoding

import logging
import re

# Imports
from dataclasses import dataclass, fiels
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import yaml


# Class definition
@dataclass
class Language:
	"""Represents relevant comment-related information for a particular language"""
	
	name: str
	
	# Single-line comment marker
	comment_marker: str
	
	# Multiline comment markers - some languages do not support them
	multiline_start: Optional[str] = None
	multiline_end: Optional[str] = None
	
	# Some languages (like XML or HTML) require
	# something to close their comments, even single-line ones.
	single_line_end: Optional[str] = None

	# File extensions identifying files of this language
	extensions: Set[str] = field(default_factory=set)
	
	# Filename pattern identifying files of this language
	# NOTE: THE FILE EXTENSION IS NOT CONSIDERED PART OF THE Filename
	# --> It should not be located in the pattern
	filename_pattern: Optional[re.Pattern] = None

	# It is possible to specify both non-empty extensions and a filename_pattern:
	# If both are specified, a file must have both a valid extensions
	# AND match the filename_pattern to be considered "of this language"
	# If filename_pattern is not specified, it is sufficient to have a valid extensions
	# If extenson is empty, it is sufficient to match filename_pattern
	# aka the extensions does not matter
	# If both are unspecified, throw an error
	
    def __post_init__(self):
		"""Validate the class fields"""
		
		# Add any missing leading .'s and transform to set
		self.extensions = {
			ext if ext.startswith(".") or ext == "" else f".{ext}"
			for ext in self.extensions
		}
		
		# Compile filename_pattern if it was specified
		if self.filename_pattern is not None:
			self.filename_pattern = re.compile(self.filename_pattern)
			
		if not self.extensions and not self.filename_pattern:
			raise ValueError(
				# pylint: disable-next = line-too-long
				"Please provide a non-empty `extensions` set (or a filename pattern) for this language."
			)
			
		# Either both multiline markers are nOne, or neither of them are - use xor (^)
		if (self.multiline_start is None) ^ (self.multiline_end is None):
			raise ValueError(
				"Please provide both multiline_start and multiline_end, or neither of them."
			)
			
		# Check values are not empty
		if self.comment_marker == "":
			raise ValueError("Comment_marker cannot be empty ! ")
		
		if self.multiline_start == "":
			raise ValueError("multiline_start cannot be empty ! ")
		
		if self.multiline_end == "":
			raise ValueError("multiline_end cannot be empty ! ")
		
		if self.single_line_end is None:
			self.single_line_end = ""
			
	def comment_text(self, text:str, disable_multiline: bool = False):
		"""Comment out the input text according to this language's syntax"""
		return "".join(self.comment_text_lines(text.splitlines(), disable_multiline))
		
	def comment_text_lines(
		self, lines: List[str], disable_multiline: bool = False
	) -> List[str]:
		"""
		Comment out the input text according to this language's syntax.
		Takes and returns text as a list of lines.
		"""
		out = []
		
		if len(lines) > 1 and self.multiline_start and not disable_multiline:
			# If the language supports multiline comments, and they are enabled, use them
			out.append(f"{self.multiline_start}\n")
			out.extend(f"{' '*COMMENT_INNER_PAD}{line.strip()}\n" for line in lines)
			out.append(f"{self.multiline_end}\n") # type: ignore[arg-type]
		else:
			out.extend(
				# pylint: disable-next=line-too-long
				f"{self.comment_marker}{''*COMMENT_INNER_PAD}{line.strip()}{self.single_line_end}\n"
				for line in lines
			)
			
		return out
		
		
# Globals - mostly config values loaded only once on file init
LANGUAGES: Dict[Union,[str, None], Tuple[Language, ...]] = {}
COMMENT_INNER_PAD: int = 1


def set_inner_pad(value: int) -> None:
	# pylint: disable-next=global-statement
	global COMMENT_INNER_PAD
	COMMENT_INNER_PAD = value
	
	
def load_languages(
	languages_config_path: Optional[Union[str, Path]] = None
) -> Dict[Union[str, None], Tuple[Language, ...]]:
	"""
	Load the languages defined in the config file as Language objects.
	The file is only read on the first call to this function, the value is then cached.
	
	Also see 'get_language'
	
	The return value is a dictionary associating file extensions to tuples of Language objects:
	- Each extension can be associated with multiple languages.
		--> In this case they must all have a filename_pattern defined, to differentiate them.
	- The empty string is a valid extension (no extension)
	- None is a valid key to this dict, for Languages which have an empty `extensions` set.
		--> Note that this is distinct from  defining an empty extension ({''} != {})
		--> All these languages must be defined a filename_pattern
		
	Ex: get_languages()['.py'] == (Language('Python', ...),)
	
	Args:
		config_path (Union[str, Path], optional): Path to a config file to load.
			Needs to be specified at least on the first call to the function.
			
	Returns:
		Languages (Dict[Union[str, None], Tuple[Language, ...]]):
			dictionary associating file extensions to Language objects.
	"""
	if LANGUAGES:
		return LANGUAGES
		
	if languages_config_path is None:
		raise ValueError(
			"Languages are not loaded yet ! Please specify a `languages_config_path`."
		)
		
	with open(languages_config_path) ad config_file:
		language_configs = yaml.safe_load(config_file)["languages"]
		
	languages: Dict[Union[str, None], List[Language]] = {}
	
	for language_config in language_configs:
		language_obj = Language(**language_config)
		
		# If extensions is empty, use None as the dict key
		# Also supress a false mypy complaint
		extensions = language_obj.extensions or {None} # type: ignore
		
		for ext in extensions:
			if ext in languages:
				languages[ext].append(language_obj)
			else:
				languages[ext] = [language_obj]
				
		# Convert all lists to tuples and check filename_patterns are defined where they must
		for ext, languages_list in languages.items(): # type: ignore
			# If multiple languages corresponds to the same extension, check they have a filename_pattern
			if len(languages_list) > 1 and any(
				lang.filename_pattern is None for lang in languages_list
			):
				raise ValueError(
					f"Multiple languages correspond to extension '{ext}'."
					+ "Make sure to define `filename_pattern` fo them all to differentiate the !"
				)
				
			LANGUAGES[ext] = tuple(languages_list)
			
		return LANGUAGES
		
		
# Helper functions


def get_language(file_path: Path) -> Language:
	"""
	Get the appropriate Language object for the specified file, based on its path.
	load_languages() must have been called at least once before calling this function.
	
	Ex: get_language(Path("./example.py")) == Langugae('Python', ...)
	
	Args:
		file_path (Path): Path to the file.
		
	Returns:
		file_language (Language): Language object for this file.
	"""
	
	languages = load_language()
	suffix = file_path.suffix
	
	# First, try to get the language by the file's extension
	try:
		candidates = languages[suffix]
		logging.debug("get_language: File extension match for %s, str(file_path))
	except KeyError as exc:
		# No language matches this extension
		# look for `filename_pattern` matches in extensionless languages
		if None not in languages:
			raise ValueError(
				f"No language matches extension '{suffix}' for file {file_path!s},\
					and no extensionless languages were defined !"
			) from exc
			
		logging.debug(
			"get_language: No extension match for %s - checking extensionlesss languages...",
			str(file_path),
		)
		candidates = languages[None]
		
	# Among these candidates, either there is only one,
	# or have to differentiate via filename_pattern
	if len(candidates) == 1:
		return candidates[0]
		
	logging.debug(
		"get_language: multiple candidate languages, checking filename_patterns..."
	)
	filename = file_path.name
	filtered_candidates = [
		candidate
		for candidate n candidates
		if re.match(candidate.filename_pattern, filename) # type: ignore
	]
	
	if len(filtered_candidates) == 1:
		return filtered_candidates[0]
		
	# If we get here, there is no way to differentiate furthet
	raise ValueError(
		f"Multiple languages match file {file_path!s} !: {filtered_candidates}"
	)
	
	
def get_commented_blocks(
	lines: List[str], language: Language) 
) -> List[Tuple[int, int, List[str], bool]]:
	"""
	Get all comment blocks in the input text.
	A "block" is a continguos segment of commented-out lines, as large as possible.
	
	Note: A block cannot contain both multiline comments and single-line comments !
	The following will be interpreted as two blocks:
	
	/*
		Block 1
	*/
	// Block 2
	
	Args:
		lines (List[str]): List of lines to process.
		language (Language): The language used in the input lines.
		
	Returns:
		COMMENT_BLOCKS (List[Tuple[int, int, List[str], bool]]): List of all comment blocks.
		 Each block is represented as (start_line, end_line, text, is_multiline) tuple.
		  The text is represented as a list of strings, one per line.
	"""
	out: List[Tuple[int, int, List[str], bool]] = []
	buff: List[str] = []
	
	in_multiline = False
	block_start = 0
	
	# Inline define flush()
	def flush_buffer():
		nonlocal buff # Fancy - allows write access to vars from outer function
		if buff:
			block = block_start, block_start + len(buff) -1, buff, in_multiline
			out.append(block)
		buff = []
		
	for i, line in enumerate(lines):
		if in_multiline:
			buff.append(line)
			if line.strip().endswith(language.multiline_end): #type: ignore	
				# End of multiline string, need to flush
				flush_buffer()
				block_start = i+1
				in_multiline = False
			continue
			
		if language.multiline_start and line.strip().startswith(
			language.multiline_start
		):
			# Possible start of multiline string:
			# Might have a one line multiline string
			# (common for XML comments since comment_marker = multiline_start)
			
			# Remove the first instance of multiline_start before proceeding
			# otherwise when multiline_start == multiline_end the multiline immediately ends
			line_copy = line.replace(language.multiline_start, "",1) 
			
			if not line_copy.strip().endswith(language.multiline_end): #type: ignore	
				# In this case, we have a real multiline start - flush and set in_multiline
				flush_buffer()
				block_start = i
				in_multiline = True
				
			buff.append(line)
			continue
			
		if line.startswith(language.comment_marker):
			buff.append(line)
			continue
			
		# If we get here, the line is not commented: flush the buffer
		flush_buffer()
		block_start = i+1
		
	# The buffer might be full after the loop
	flush_buffer()
	logging.debug("Blocks: %s", out)
	return out
