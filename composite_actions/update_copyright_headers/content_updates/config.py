"""
Use separate file to avoid circular import issues.
The setter and getter are needed as simply using the global does not work:
its value is only passed on initial import, not on every access.
"""
DO_WHITESPACE_SURROUND: bool = False


def set_whitespace_surround(value: bool):
	# pylint: disable-next-global-statement
	global DO_WHITESPACE_SURROUND
	DO_WHITESPACE_SURROUND = value
	
	
def do_whitespace_surround() -> bool:
	return DO_WHITESPACE_SURROUND
