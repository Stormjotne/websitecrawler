from pathlib import Path
import time
import re

#  Initialize output directory
from crawler import Crawler

Path("output").mkdir(parents=True, exist_ok=True)
#  Initialize html directory
Path("output/html").mkdir(parents=True, exist_ok=True)
#  Initialize log directory
Path("logs").mkdir(parents=True, exist_ok=True)
#  Chunk size for writing bytes to file
chunk_size = 100


def write_log(input_name, log_list):
	"""
	A function which writes a log file with the current date-time as part of its file name.
	:param input_name: String
	:param log_list: List
	:return:
	"""
	with open("logs/" + time.strftime("%Y%m%d-%H%M%S") + "-" + input_name + ".log", 'w') as fd:
		for element in log_list:
			fd.write("{}\n".format(element))
	

def filename_from_url(url):
	"""
	The function uses regex to remove illegal file name characters from the input URL.
	:param url: String
	:return: String
	"""
	output = re.sub("[\"\'\[\](){}<>:/\\\|?*]", "", url)
	return output


def touch_files(input_name, input_depth):
	"""
	The function creates empty txt files corresponding with the specified lever of recursion.
	The txt files are used for link identification in the crawler, for further subpage downloads.
	:param input_name: String
	:param input_depth: Integer
	:return:
	"""
	output_files = []
	for i in range(input_depth):
		Path("output/" + input_name + str(i + 1) + ".txt").write_text("")
		output_files.append(input_name + str(i + 1) + ".txt")
	return output_files


def write_file(input_name, content):
	"""
	A function which overwrites existing file with an input stream.
	:param input_name:
	:param content:
	:return:
	"""
	with open(input_name, 'wb') as fd:
		for chunk in content.iter_content(chunk_size):
			fd.write(chunk)


def append_file(input_name, content):
	"""
	A function which appends the input stream to an existing file.
	:param input_name: The path/name of the output file.
	:param content: The input stream of an HTTP body.
	:return:
	"""
	with open(input_name, 'ab+') as fd:
		for chunk in content.iter_content(chunk_size):
			fd.write(chunk)


def open_file(input_directory, input_name):
	"""
	A function which opens file with open(), utf-8 or default encoding,
	and returns the contents as a String.
	:param input_directory: String
	:param input_name: String
	:return: String
	"""
	try:
		with open(input_directory + input_name, 'r', encoding="utf-8") as fd:
			contents = fd.read()
		return contents
	except UnicodeDecodeError as err:
		Crawler.log_event("Opening {} resulted in an error:\n {}.\nAttempting default encoding.".format(input_name, err))
		with open(input_directory + input_name, 'r') as fd:
			contents = fd.read()
		return contents


def file_name_list(input_directory, input_file_name_base):
	"""
	Returns a list of html file names that correspond with the base URL.
	:param input_directory: String
	:param input_file_name_base: String
	:return: List
	"""
	output = Path(input_directory).glob(input_file_name_base + '*.html')
	output = [str(x.name) for x in output]
	return output
