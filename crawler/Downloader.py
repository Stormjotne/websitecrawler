from crawler import IO, Identifier
import requests
import time

downloader_log = []
fetched_links = []
output_files = []
output_directory = "output/"
global number_of_subpages
number_of_subpages = 0


def log_event(input_string):
	"""
	Append log-string to the downloader log.
	:param input_string: log-string such as a timer or an error.
	:return:
	"""
	downloader_log.append(input_string)


def book_keeping(input_list):
	"""
	Keep track of links that have been downloaded, so as to not download the same subpage twice.
	:param input_list:
	:return:
	"""
	for link in input_list:
		fetched_links.append(link) if link not in fetched_links else fetched_links


def download_page(input_url, input_depth, input_subpages):
	"""
	A method which sends an HTTP request to the specified URL.
	Uses helper method to write the body to the output file.
	:param input_url: User specified URL
	:param input_depth: The depth of recursion.
	:param input_subpages:
	:return:
	"""
	t_start = time.time()
	filename_base = IO.filename_from_url(input_url)
	filename = filename_base + str(0) + ".txt"
	output_files.append(filename_base + str(0) + ".txt")
	response = requests.get(input_url)
	IO.write_file("output/" + filename, response)
	IO.write_file("output/html/" + filename_base + ".html", response)
	IO.touch_files(filename_base, input_depth)
	download_subpage(input_url, input_depth, input_subpages)
	t_end = time.time()
	log_event("Fetching {} took {} seconds.".format(input_url, t_end - t_start))
	return downloader_log
	
	
def download_subpage(input_url, input_depth, input_subpages, input_step=1):
	"""
	A method which sends an HTTP request to the specified URL.
	Uses helper method to append the body to the output file.
	:param input_url: User specified URL
	:param input_depth: The depth of recursion.
	:param input_subpages:
	:param input_step: The current step.
	:return:
	"""
	global number_of_subpages
	if input_depth > 0:
		filename_base = IO.filename_from_url(input_url)
		filename = filename_base + str(input_step) + ".txt"
		last_filename = filename_base + str(input_step-1) + ".txt"
		#  Identify links in downloaded HTML
		links = Identifier.identify_links(IO.open_file(output_directory, last_filename), input_url)
		#  Filter out links that have been downloaded
		new_links = [link for link in links if link not in fetched_links]
		#  Keep track of downloaded links
		book_keeping(new_links)
		for link in new_links:
			#  Check if maximum amount of subpages has been reached.
			if number_of_subpages < input_subpages:
				t_start = time.time()
				request_session = requests.Session()
				request_session.max_redirects = 3
				try:
					response = request_session.get(input_url + link, timeout=1.3)
				except requests.Timeout as err:
					log_event("Fetching {} resulted in an error:\n {}.".format(link, err))
				except requests.TooManyRedirects as err:
					log_event("Fetching {} resulted in an error:\n {}.".format(link, err))
				except requests.ConnectionError as err:
					log_event("Fetching {} resulted in an error:\n {}.".format(link, err))
				else:
					IO.append_file("output/" + filename, response)
					IO.write_file("output/html/" + filename_base + IO.filename_from_url(link) + ".html", response)
					number_of_subpages += 1
				request_session.close()
				t_end = time.time()
				download_subpage(input_url, input_depth - 1, input_step + 1)
				log_event("Fetching {} took {} seconds.".format(link, t_end - t_start))
