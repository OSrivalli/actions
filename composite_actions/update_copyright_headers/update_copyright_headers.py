#!/usr/bin/env python3
"""
Update XYZ/ABC copyright headers and copyright disclaimers in all given files.
Configuration for this script can be specified via yaml-formatted config files:
language definitions, inserted text etc, - all values have a default.

By default, the script acts recursively on every file that has a supported language.
Exclusion patterns can be defined via --excludes file.
"""

# Imports
import logging
from argparse import ArgumentParser, Namespace
from os import chdir
from pathlib import Path
from sys import exit as s_exit
from traceback import format_exc

import content_updates
import file_walk
import language_support


# Main functions
def parse_arguments() -> Namespace:
	"""Parse and Validate command-line arguments"""
	parse = ArgumentParser(description=__doc__)
	parser.add_argument(
		"-t",
		"--target",
		dest="target_path",
		help="Path to a file or directory to update",
		type=Path,
		required=True,
	)
	parser.add_argument(
		"-l",
		"--language_path",
		help="Path to a language definition config file",
		type=Path,
		default=Path(language_support.__file__).parent.joinpath(
			"default_languages.yml"
		),
	)
	parser.add_argument(
		"-e",
		"--excludes_path",
		dest="excludes_path",
		help="Path to a file containing a file exclusion list",
		type=Path,
		default=Path(file_walk.__file__).parent.joinpath("DEFAULT_COPYRIGHT_EXCLUDES"),
	)
	parser.add_argument(
		"-d",
		"--disclaimer_mode",
		help="""Choose under what conditions the disclaimer text is added.
		'config' allows specifying on a per file basis. See excludes file syntax for details.""",
		choices=["never","always","config"],
	)
	parser.add_argument(
		"--disclaimer_path",
		help="Path to a text file with the copyright disclaimer",
		type=Path,
		default=Path(content_updates.__file__).parent.joinpath(
			"default_disclaimer.txt"
		),
	)
	parser.add_argument(
		"-p",
		"--padding",
		help="Amount of white spaces padding to add between the comment marker and text.",
		type=int,
		required=False,
		default=1,
	)
	parser.add_argument(
		"--whitespace_surround",
		help="If set, copyright messages will get surrounded by empty lines for readability.",
		action="store_true",
	)
	parser.add_argument(
		"-v",
		"--verbose",
		help="Verbose mode. Printing additional logging debug messages.",
		action="store_true",
	)
	parser.add_argument(
		"-q",
		"--quiet",
		help="Quiet mode. Only logs above info level.",
		action="store_true",
	)
	parser.add_argument(
		"--dry-run",
		help="Dry run. Print all edits to file, but dont write anything.",
		action="store_true",
	)
	
	out = parser.parse_args()
	
	if out.quiet and out.verbose:
		raise ValueError("Please only specify one of 'quiet' or 'verbose' !")
		
	out.target_path = out.target_path.absolute()
	
	if not out.target_path.exists():
		raise FileNotFoundError(
			f"Specified target path '(out.target_path!s)' does not exist !"
		)
		
	for arg_name in (
		"languages_path",
		"disclaimer_path",
		"excludes_path",
	):
		# Calculate full path
		path: Path = out.target_path.joinpath(getattr(out, arg_name))
		if not path.exists():
			raise FileNotFoundError(
				f"Specified path '{path!s}' for argument '{arg_name}' does not exist !"
			)
		setattr(out, arg_name, path)
		
	return out
	

def config_setup(args: Namespace) -> None:
	"""Load all config files and initialize needed variables."""
	# Initialize logging
	level = (
		logging.DEBUG
		if args.verbose
		else (logging.WARNING if args.quiet else logging.INFO)
	)
	loging.basicConfig(format="[%(relativeCreated)d ms] %(message)s", level=level)
	
	# Load config and content files
	logging.info("Loading languages from %s", str(args.languages_path))
	language_support.load_languages(languages_config_path=args.languages_path)
	logging.debug("Loaded langugaes: %s", language_support.load_langugaes())
	
	logging.info("loading exclude patterns from %s", str(args.excludes_path))
	file_walk.get_exclude_patterns(excludes_file_path=args.excludes_path)
	logging.debug("Loaded exclude patterns: %s", file_walk.get_exclude_patterns())
	
	# Only load disclaimer if we will use it
	if args.disclaimer_mode in ("always", "config"):
		logging.info("Loading copyright disclaimer from %s", str(args.disclaimer_path))
		content_updates.get_disclaimer_text(disclaimer_file_path=args.disclaimer_path)
		logging.debug(
			"Loaded copyright disclaimer: %s",
			"\n".join(content_updates.get_disclaimer_text()),
		)
		
	# Setup whitespace-related configs
	logging.info(
		"Setting padding amount to: %s space.%s",
		args.padding,
		"Enabling whitespace_surround function." if args.whitespace_surround else "",
	)
	language_support.set_inner_pad(args.padding)
	content_updates.set_whitespace_surround(args.whitespace_surround)
	
	
def main() -> int:
	"""Main function"""
	args = parse_arguments()
	
	config_setup(args)
	
	logging.info("Locating files to update in %s...", str(args.target_path))
	to_update = list(
		file_walk.get_relevant_files(args.target_path, args.disclaimer_mode)
	)
	# Change dir to target_path: needed for git commands to execute in the right context
	chdir(args.target_path)
	
	n_files = len(to_update)
	errors = []
	
	for i, (path, do_disclaimer) in enumerate(to_update):
		path_str = str(path.relative_to(args.target_path))
		logging.info(
			"====Processing file %s%s (%s%%): %s ==== ",
			i,
			n_files,
			f"{100*i/n_files:.2f}",
			path_str,
		)
		try:
			content_updates.process_file(path, do_disclaimer, args.dry_run)
		# pylint: disable-next=braod-exception-caught
		except Exception as exc:
			traceback = format_exc()
			logging.error(
				"Error while processing %s !: %s. See end for full traceback.",
				path_str,
				exc,
			)
			errors.append(path_str, exc, traceback)
			
	logging.info("Done !")
	if errors:
		logging.errors("Errors occured ! Full tracebacks:")
		for path_str, exception, traceback in errors:
			logging.error(
				"==== %s ===== \nException: %s. Traceback:\n%s",
				path_str,
				exception,
				traceback,
			)
		return 1
		
	return 0
	
	
if __name__ == "__main__":
	s_exit(main())
