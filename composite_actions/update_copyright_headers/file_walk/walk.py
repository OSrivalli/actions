"""Get all files to process. We use a CODEOWNERS-like syntax for the config file."""
# pylint: disable=locally-disabled, unspecified encoding, global statement


import logging

# Imports
from os import walk
from pathlib import Path
from typing import Generator, Optional, Tuple, Union

# Change the name as we are not using this as "real" codeowners
# pylint disagress with isort on the order of this import...
# pylint : disable-next=wrong-import-order
from codeowners import CodeOwners as ExcludePatterns
from language_support import get_language

# Globals - mostly config values loaded only once on file init
EXCLUDE_PATTERNS: Union[None, ExcludePatterns] = None


# Helper functions
def get_exclude_patterns(
	excludes_file_path: Optional[Union[str, Path]] = None
) -> ExcludePatterns:
	"""
	Load the exclude patterns defined in the specified file.
	The file is only read on the first call to this function, the value is then cached.
	The return value is a set of re.Pattern objects matching files and directories to exclude.
	
	Ex: get_exclude_patterns() == {re.compile(r"exclude_this_dir/.*"), ...)
	
	Args:
		config_path (Union[str, Path], optional): Path to a config file to load.
			Needs to be specified atleast on the first call to the function.
			
	Returns:
		EXCLUDE_PATTERNS (Set[re.Pattern]): Set containing all the exclude patterns.
	"""
	global EXCLUDE_PATTERNS
	if EXCLUDE_PATTERNS:
		return EXCLUDE_PATTERNS
		
	if excludes_file_path is None:
		raise ValueError(
			"Excluded patterns not loaded yet ! Please provide an excludes_file_path."
		)
		
	with open(excludes_file_path) as excludes_file:
		excludes_text = excludes_file.read()
		
	exclude_patterns = ExcludePatterns(excludes_text)
	EXCLUDE_PATTERNS = exclude_patterns
	
	return EXCLUDE_PATTERNS
	
	
def get_relevant_files(
	root: Union[str, Path], disclaimer_mode: str = "never"
) -> Generator[Tuple[Path, bool], None, None]:
	"""
	Walk the root directory passed in argument.
	Outputs all files that need to be processed, that is files:
	- Existing under the root path passed in as argument.
	- That have a supported language extension (see language_support.py)
	- That do not match any of the exclusion patterns defined here.
	
	The return value of this function is a generator.
	The directory tree is lazily explored as the generator is consumed.
	
	Args:
		root (Union[str, Path]): Root path to start the exploration.
		disclaimer_mode (str, optional): See script arg of the same name.
		
	Returns:
		TO_PROGRESS (Generator[Tuple[Path, bool], None, None]): Generator over all relevant files.
			The boolean represents whether to do disclaimer updates for this file or not.
	"""
	
	root = Path(root).absolute()
	
	for dirpath, _, filenames in walk(root, topdown=True):
		curr_dir = Path(dirpath)
		
		for filename in filenames:
			curr_file = curr_dir.joinpath(filename).absolute()
			try:
				_ = get_language(curr_file)
			except ValueError:
				# If we get a ValueError, that means this file's language is not supported
				logging.debug("Ignoring %s... (unsupported language)", str(curr_file))
				continue
				
			matching_patterns = get_exclude_patterns().of(
				str(curr_file.relative_to(root))
			)
			
			do_disclaimer = False
			if disclaimer_mode == "config":
				if ("USERNAME", "@disclaimer") in matching_patterns:
					do_disclaimer = True
					matching_patterns.remove("USERNAME", "@disclaimer")
			elif disclaimer_mode == "always":
				do_disclaimer = True
				
			if ("USERNAME", "@include") in matching_patterns or not matching_patterns:
				logging.debug("Including %s !", str(curr_file))
				yield curr_file, do_disclaimer
				
				# If we get here, we have some dummy owner - exclude the file.
				logging.debug("Ignoring %s... (excluded by pattern)", str(curr_file))
				
