"""
Define the 'main' function for this module: process_file(().
This function handles all the header and disclaimer manipulation.
"""
# pylint: disable=locally-disabled, unspecified-encoding, global-statement

import logging
from pathlib import Path

from content_updates.copyright_disclaimer import process_disclaimer
from content_updates.copyright_header import process_header
from language_support import get_language


# Main function
def process_file(
	file_path: Path, do_disclaimer: bool = False, dry_run: bool = False
) -> None:
	"""
	Update the specified file:
	- Add/Update the copyright header ("(c) Copyright xxxx ACME, Inc. All Rights reserved.")
	- Optionally add/update the copyright disclaimer (Long disclaimer text). See do_disclaimer arg.
	
	
	If the file alreday contains a header, the years specified will be made up-to-date.
		--> We assume the earliest year in the header is the year for which the copyright applies.
		
	If there is none, a new header will be inserted in the first available safe spot.
		--> The creation year will be determined using the file's git history.
		
	If do_disclaimer is True, we also ass/update a long copyright disclaimer to the file.
	If the file lareday contains a disclaimer, it will be replaced.
	If there is none, a new one will be inserted just after the copyright header.
		--> Such a header must alreday exist !
		
	Modifies the specified file.
	
	Args:
		file_path (Path): The path to the file to update.
		do_disclaimer (bool, optional): Whether to update the copyright discliamer.
			Defaults to False.
		dry_run (bool, optional): Dry run: print all changes to be made, but do not write anything.
			Defaults to False.
	"""
	
	with open(file_path) as file:
		lines = file.readlines()
		
	logging.info("Processing header...")
	lines = process_header(lines, file_path)
	
	if do_disclaimer:
		file_language = get_language(file_path)
		logging.info("Processing disclaimer...")
		lines = process_disclaimer(lines, file_language)
		
	if not dry_run:
		with open(file_path, "w") as file:
			file.writelines(lines)
