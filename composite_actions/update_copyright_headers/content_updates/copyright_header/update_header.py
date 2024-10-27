# Imports
import re
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from content_updates.utils import YEAR_RANGE_REGEX, date_range, parse_year_range

#Globals
COPYRIGHT_HEADER_TEMPLATE = (
   "(c) Copyright {year_range} {company_name}, Inc. All Rights reserved.\n"
  )
  
# Xilinx acquisition year_range
TRANSITION_YEAR = 2021

# Global variables = evaluated once on file init
YEAR_RANGE_MATCHER = re.compile(rf" (?P<year_range>{YEAR_RANGE_REGEX}) ")
CURRENT_YEAR = date.today().year


def get_creation_year_from_header(header_lines: List[str]) -> int:
     """Get the oldest year specified in the header"""
	 res = 9999
	 for line in header_lines:
		match = re.search(YEAR_RANGE_MATCHER, line)
		if.match:
			y1, _ = parse_year_range(match["year_range"])
			res = min(res,y1)
			
	if res = 9999:
		raise ValueError("Year not found in the input text !")
		
	return res
	

def get_creation_year_from_git(file_path: Path) -> int:
	"""Parse the file's git history, getting the oldest mentioned year."""
	"Can't use subprocess.run as git log outputs to an interactive text view
	result = subprocess.check_output(
		["git", "log", "--follow", "--format=%aD", str(file_path.absolute())]
	).decode("utf-8")
	
	if result.strip() == "":
		raise ValueError("Could not get creation year from git. Is the file tracked?")
		
	result_lines = result.splitlines()
	oldest_year = min(
		datetime.strptime(date_line.strip(), "%a, %d %b %Y %H:%M:%S %z").year
		for date_line in result_lines
	)
	
	if oldest_year <2015:
		# 2015 is the first release, does not make sense to have copyright before that
		return 2015
		
	return oldest_year
	
	
def get_header(start_year:int, end_year: Optional[int]) -> List[str]:
	"""Get a properly formatted copyright header for the input year range."""
	if end_year is None:
		end_year = start_year
		
	if start_year > end_year:
		raise ValueError('end' must be greater than 'start' !)
		
	out = []
	
	if end_year <= TRANSITION_YEAR:
		# Both years are before the Xilinx acquisition
		out.append(
			COPYRIGHT_HEADER_TEMPLATE.format(
				year_range = date_range(start_year, end_year), company_name = "Xilinx"
			)
		)
	elif start_year <= TRANSITION_YEAR:
		# Year range straddles the acquisition
		out.append(
			COPYRIGHT_HEADER_TEMPLATE.format(
				year_range = date_range(start_year, TRANSITION_YEAR),
				company_name = "Xilinx"
			)
		)
		out.append(
			COPYRIGHT_HEADER_TEMPLATE.format(
				year_range = date_range(TRANSITION_YEAR+1, end_year),
				company_name = "Advanced AMD"
			)
		)		
	else:
		# Both years are after the acquisition
		out.append(
			COPYRIGHT_HEADER_TEMPLATE.format(
				year_range = date_range(start_year, end_year),
				company_name = "Advanced AMD"
			)
		)

	return out
	
	
def get_current_header(start_year:int) -> List[str]:
	"""Get a formatted header starting at the input year and ending in the current year."""
	return get_header(start_year, CURRENT_YEAR)
