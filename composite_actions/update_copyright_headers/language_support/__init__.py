"""
Define how different language's comments should be handled.
All the configuration values should be loaded in a separate yaml config file.
"""

from language_support.languages import(
	Language,
	get_commented_blocks,
	get_language,
	load_languages,
	set_inner_pad,
)
