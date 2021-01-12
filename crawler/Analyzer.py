import unicodedata
from collections import Counter
from crawler import IO, Identifier
from lxml import html
from lxml.html.clean import Cleaner
import re
import time
import cssselect

analyzer_log = []
html_directory = "output/html/"
global number_of_analyzed_pages
number_of_analyzed_pages = 0
cleaner = Cleaner()
#   Activate the javascript filter
cleaner.javascript = True
#   Activate the styles & stylesheet filter
cleaner.style = True


def log_event(input_string):
    """
    Append log-string to the analyzer log.
    :param input_string: log-string such as a timer or an error.
    :return:
    """
    analyzer_log.append(input_string)


def parse_html(input_directory, input_file_name):
    """
    Use lxml.html to parse an html file.
    The function is used to extract textual content.
    :param input_directory: String
    :param input_file_name: String
    :return: String
    """
    output = html.parse(input_directory + input_file_name).getroot()
    output = cleaner.clean_html(output)
    return output.cssselect('body')[0].text_content()


def open_html(input_directory, input_file_name):
    """
    Open html files without parsing.
    The function is used to extract content from the source code, such as comments.
    :param input_directory: String
    :param input_file_name: String
    :return: String
    """
    output = IO.open_file(input_directory, input_file_name)
    return output


def count_words(input_content):
    """
    Count every word present in the input content.
    :param input_content: String
    :return: A dictionary with word, count pairs.
    """
    #   A dictionary to store the number of times each word is used
    word_count = {}
    content = input_content
    #   Normalize unicode string to avoid different encodings in the post-regex
    content = unicodedata.normalize("NFKD", content)
    #   Check for common symbols and whitespace characters and replace with a space.
    content = re.sub("[\s*/()\[\]{}.,&\'\":;!?=<>%$€£@+\-–`´\-_|«»©®℗§™❤😉😊😍😂😘😁🎉👍👌]", " ", content)
    #   Split words by single space
    words = content.split(" ")
    #   Casefold words
    words = [word.casefold() for word in words]
    #   A set to store the counted words in
    counted_words = set()
    #   Loop through all the words in the file
    for word in words:
        #   Check if word is blank
        if word == "":
            continue
        #   Check if string is a number
        if re.search("[0-9]+", word):
            continue
        #   Check if the word has been counted, if so skip
        if word in counted_words:
            continue
        if word in word_count:
            #   Count the frequency of the word and store it in the dictionary
            word_count[word] += words.count(word)
        else:
            #   Count the frequency of the word and store it in the dictionary
            word_count[word] = words.count(word)
        #   Add the word to the set of counted words
        counted_words.add(word)
    return word_count


def html_loop(input_file_name_base, input_total, input_regex_list):
    """
    Iterates over the html files corresponding with the base URL.
    Identifies specific information present on the website.
    :param input_file_name_base: String
    :param input_total: Integer
    :param input_regex_list: List of regular expressions (String).
    :return: A list of e-mail addresses, a list of phone numbers,
    a dictionary of comments and their position in the file,
    a list of the 100 most frequently used words on the website,
    and lastly a list of those same words paired with the frequency itself.
    """
    global number_of_analyzed_pages
    file_name_list = IO.file_name_list(html_directory, input_file_name_base)
    emails, phone_numbers, comments, new_comments, user_specified_patterns, word_count = [], [], {}, [], [], {}
    for file_name in file_name_list:
        #  Check if maximum amount of pages has been reached.
        if number_of_analyzed_pages < input_total:
            t_start = time.time()
            parsed_html = parse_html(html_directory, file_name)
            emails += Identifier.identify_email_addresses(parsed_html)
            phone_numbers += Identifier.identify_phone_numbers(parsed_html)
            new_comments = {file_name: Identifier.identify_comments(open_html(html_directory, file_name))}
            comments.update(new_comments)
            user_specified_patterns += Identifier.user_regex_loop(parsed_html, input_regex_list)
            word_count.update(dict(Counter(word_count) + Counter(count_words(parsed_html))))
            number_of_analyzed_pages += 1
            t_end = time.time()
            log_event("Analyzing {} took {} seconds.".format(file_name, t_end - t_start))
    sorted_word_count = sorted(word_count.items(), key=lambda item: item[1], reverse=True)[:100]
    hundred_most_frequent_words = [x[0] for x in sorted_word_count]
    return Identifier.remove_duplicates(emails), Identifier.remove_duplicates(phone_numbers),\
           comments, Identifier.remove_duplicates(user_specified_patterns),\
           hundred_most_frequent_words, sorted_word_count


def analyze_page(input_file_name_base, input_total, input_regex):
    """
    Analyze the downloaded content from a website.
    :param input_file_name_base:
    :param input_total:
    :param input_regex:
    :return:
    """
    t_start = time.time()
    output = html_loop(input_file_name_base, input_total, input_regex)
    t_end = time.time()
    log_event("Analyzing {} took {} seconds.".format(input_file_name_base, t_end - t_start))
    return analyzer_log, output
