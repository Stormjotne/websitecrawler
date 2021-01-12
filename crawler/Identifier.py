import re
from crawler import Crawler

output_directory = "output/"


def validate_regex(input_list):
	"""
	Loop through list of regex and attempt to compile the patterns.
	Regex is valid if it's successfully compiled.
	:param input_list:
	:return: List of valid regex (not compiled).
	"""
	valid_regex = []
	for regex in input_list:
		try:
			re.compile(regex)
			valid_regex.append(regex)
		except re.error as err:
			Crawler.log_event("Compiling {} resulted in an error:\n {}.".format(regex, err))
	return valid_regex
	

def remove_duplicates(input_list):
	"""
	Remove duplicates from a list of matches.
	Create a dictionary, using this List items as keys.
	Convert the dictionary into a list.
	:param input_list: List with regex matches.
	:return: List without duplicates.
	"""
	return list(dict.fromkeys(input_list))


def identify_links(content, input_url):
	"""
	Identify HTML links to subpages.
	:param input_url: Base URL.
	:param content: Opened file.
	:return: Groups of matches.
	"""
	regex_string =\
		"<a (?:.*?)?href=[\'|\"](?:http[s]?://(?:www.)?sinful.no)?([/][\/\w\-\_\#\?\=\&\:\.]+)[\'|\"](?:.*?)>".format(input_url)
	matches = re.findall(regex_string, content)
	return remove_duplicates(matches)


def identify_email_addresses(content):
	"""
	Matches email addresses that adhere to the current specification for email-addresses (RFC 5322)
	Except addresses with slashes in the name address, which is quite uncommon anyway.
	:param content:
	:return:
	"""
	regex_string = "(?:[a-zA-Z0-9!#$%&'*+=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+=?^_`{|}~-]+)*|" \
	               "\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")" \
	               "@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|" \
	               "\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}" \
	               "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:" \
	               "(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
	matches = re.findall(regex_string, content)
	return remove_duplicates(matches)


def nordic_phone_numbers(content):
	"""
	Matches nordic phone numbers.
	:param content:
	:return:
	"""
	regex_string = "(?<![/a-z0-9])(?:\+(?:\d{2})[ ]?)?(?:\d{2})[ ]?(?:\d{2})[ ]?(?:\d{2})[ ]?(?:\d{2})(?![a-z0-9])"
	matches = re.findall(regex_string, content)
	return remove_duplicates(matches)


def international_numbers(content):
	"""
	Matches formatted and un-formatted 10-digit numbers, especially targetted at US numbers.
	:param content:
	:return:
	"""
	regex_string = "^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$"
	matches = re.findall(regex_string, content)
	return remove_duplicates(matches)


def identify_phone_numbers(content):
	"""
	Matches different types of phone numbers in input content.
	:param content:
	:return:
	"""
	matches = nordic_phone_numbers(content)
	matches += international_numbers(content)
	return remove_duplicates(matches)


def html_comments(content):
	"""
	Matches inline or multiline html comments using finditer.
	Loop through and locate matches by calculating offset in newlines.
	+ 1 to set start line as 1 instead of 0, which is the convention in text editors.
	:param content:
	:return: List of tuples, [(match, start_line, end_line), (...), ...]
	"""
	regex_string = "\s(<!--(?:\s|.)*?-->)"
	#  Precompile pattern to use finditer.
	compiled_pattern = re.compile(regex_string, re.MULTILINE | re.DOTALL)
	matches = compiled_pattern.finditer(content)
	located_matches = []
	for match in matches:
		start_of_match = content[0:match.start()].count("\n") + 1
		end_of_match = content[0:match.end()].count("\n") + 1
		located_matches.append((match.group(), start_of_match, end_of_match))
	return located_matches


def css_comments(content):
	"""
	Matches inline or multiline css comments using finditer.
	Loop through and locate matches by calculating offset in newlines.
	+ 1 to set start line as 1 instead of 0, which is the convention in text editors.
	:param content:
	:return: List of tuples, [(match, start_line, end_line), (...), ...]
	"""
	regex_string = "\s(/\*[\*]?(?:\s|.)*?\*/)"
	#  Precompile pattern to use finditer.
	compiled_pattern = re.compile(regex_string, re.MULTILINE | re.DOTALL)
	matches = compiled_pattern.finditer(content)
	located_matches = []
	for match in matches:
		start_of_match = content[0:match.start()].count("\n") + 1
		end_of_match = content[0:match.end()].count("\n") + 1
		located_matches.append((match.group(), start_of_match, end_of_match))
	return located_matches


def js_comments(content):
	"""
	Matches inline js comments using finditer.
	Loop through and locate matches by calculating offset in newlines.
	+ 1 to set start line as 1 instead of 0, which is the convention in text editors.
	:param content:
	:return: List of tuples, [(match, start_line, end_line), (...), ...]
	"""
	regex_string = "\s(//\s?.*?$)"
	#  Precompile pattern to use finditer.
	compiled_pattern = re.compile(regex_string, re.MULTILINE | re.DOTALL)
	matches = compiled_pattern.finditer(content)
	located_matches = []
	for match in matches:
		start_of_match = content[0:match.start()].count("\n") + 1
		end_of_match = content[0:match.end()].count("\n") + 1
		located_matches.append((match.group(), start_of_match, end_of_match))
	return located_matches


def identify_comments(content):
	"""
	Matches different types of comments in html files.
	:param content:
	:return:
	"""
	matches = html_comments(content)
	matches += css_comments(content)
	matches += js_comments(content)
	return matches


def identify_user_regex(content, input_regex):
	"""
	Matches any string data with user specified regex.
	:param content:
	:param input_regex:
	:return:
	"""
	matches = re.findall(input_regex, content)
	return remove_duplicates(matches)


def user_regex_loop(content, input_list):
	"""
	Loops through list of use specified regex.
	Matches with the html content using identify_user_regex()
	:param content:
	:param input_list:
	:return:
	"""
	matches = []
	for regex in input_list:
		matches += identify_user_regex(content, regex)
	return remove_duplicates(matches)
