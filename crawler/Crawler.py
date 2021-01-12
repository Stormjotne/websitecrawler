from crawler import Analyzer, Downloader, IO, Identifier
import time

crawler_log = []


def log_event(input_string):
	"""
	Append log-string to the crawler log.
	:param input_string: log-string such as a timer or an error.
	:param input_string:
	:return:
	"""
	crawler_log.append(input_string)
	

class Crawler:
	"""
	The Crawler object uses input url, depth of recursion, maximum/total amount of subpages,
	a list of user-defined regular expressions (regex) to crawl a website, extract information and analyze it.
	The flags crawl and analyze can be set to True/False to turn crawl and analyze functionality on or off, respectively.
	This is useful if you wish to download and perform analysis separately in multiple sessions.
	The Crawler object should return a tuple containing the following:
		*  A list of e-mail addresses.
		*  A list of phone numbers.
		*  A dictionary containing lists with tuples,
			where the tuples contain comments and the line numbers they were found at,
			and the dictionary keys are the names of the files they were discovered in.
		*  A list of strings identified by user-defined regex.
		*  A list of the 100 most frequently used words on the website.
		*  A list of tuples, where the tuples contain the 100 most frequently used words on the website,
			and their frequency.
	"""
	def __init__(self, input_url, input_depth, input_total=100, input_regex=None, crawl=True, analyze=True):
		"""
		Initialize Crawler object using input parameters.
		:param input_url: URL specified by the user, on the form address.domain (e.g. google.com).
		:param input_depth:  The depth of recursion when downloading subpages.
		A depth of 0 will result in only the main page being downloaded,
		and a depth of 1 will result in all the links discovered in the main page being subject to downloads.
		A maximum depth of 3 is recommended, but not enforced.
		:param input_total:  Total number of subpages to be downloaded.
		Defaults to 100 with a minimum of 1 and a maximum of 1000.
		If the number provided by the user is out of bounds, the default value is used.
		:param input_regex: List of user-defined regex.
		For help with regex syntax, visit https://docs.python.org/3/howto/regex.html
		"""
		#  Remove trailing slash / if present
		self.start_url = "https://www." + input_url.rstrip("/")
		self.crawl_depth = input_depth
		self.total_subpages = input_total if 0 < input_total <= 1000 else 100
		self.regex_list = Identifier.validate_regex(input_regex)
		self.crawl_flag = crawl
		self.analyze_flag = analyze

	def crawl(self):
		"""
		Download website.
		First downloads main page, then proceeds to look for links in the downloaded file.
		The subpages are then downloaded and appended to a larger file for further link extraction.
		Depending on the settings, the crawler will crawl deeper into the subpages.
		The crawler has finished when either the maximum/total amount of subpages or has been reached,
		or there are no new links discovered at the specified depth.
		:return:
		"""
		if self.crawl_flag:
			t_start = time.time()
			log = Downloader.download_page(self.start_url, self.crawl_depth, self.total_subpages)
			t_now = time.time()
			t_crawl = t_now - t_start
			log_event("Crawl took {} seconds.".format(t_crawl))
			IO.write_log(input_name="crawl", log_list=log)

	def analyze(self):
		"""
		Analyzes downloaded website.
		Loops through all the downloaded html from the specified URL, and extracts the following information:
		*  E-mail addresses.
		*  Phone numbers.
		*  Comments in the source code.
		*  Strings identified by the user-defined regex.
		*  The 100 most frequently used words on the website.
		:return: Output object containing the information described above.
		"""
		if self.analyze_flag:
			t_start = time.time()
			log, output = Analyzer.analyze_page(
				input_file_name_base=IO.filename_from_url(self.start_url),
				input_total=self.total_subpages + 1, input_regex=self.regex_list)
			t_now = time.time()
			t_analyze = t_now - t_start
			log_event("Analyze took {} seconds.".format(t_analyze))
			IO.write_log(input_name="analyze", log_list=log)
			IO.write_log(input_name="misc", log_list=crawler_log)
			return output
