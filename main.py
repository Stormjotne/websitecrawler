from crawler import Crawler
import time

URL = "posten.no"
DEPTH = 1
TOTAL = 10
REGEX = ["[a-z]{20}", "[hei", "[0-9]{20}"]
CRAWL = True
ANALYZE = True


def post_crawler_loop(crawler_output):
    """
    Terminal program loop for viewing data collected through the webcrawler and analysis.
    :param crawler_output: the output object from the Analyzer
    :return:
    """
    post_bool = True
    while post_bool:
        post_input = input("\nWhich results would you like to inspect?:\n"
                           "1. A list of identified e-mail addresses.\n"
                           "2. A list of identified phone numbers.\n"
                           "3. A dictionary containing comments discovered in the source code.\n"
                           "4. A list of data discovered by the user-defined regex.\n"
                           "5. A list of the 100 most frequently used words on the website.\n"
                           "6. A list of the 100 most frequently used words on the website, and their frequency.\n"
                           "7. All of the above in a big, mushy pile.\n"
                           "Any other entry will terminate the program.\n")
        if post_input == "1":
            if not crawler_output[0]:
                print("Sadly, the list is empty.")
            else:
                print([x for x in crawler_output[0]])
        elif post_input == "2":
            if not crawler_output[1]:
                print("Sadly, the list is empty.")
            else:
                print([x for x in crawler_output[1]])
        elif post_input == "3":
            if not crawler_output[2]:
                print("Sadly, the dictionary is empty.")
            else:
                print("Comments were found in {} files:".format(len(crawler_output[2])))
                for key in crawler_output[2]:
                    print(key)
                time.sleep(1)
                print("\nThe html files can be found in the /output/html directory relative to the main file.")
                time.sleep(3)
                for key in crawler_output[2]:
                    print("\nLet's take a look at {}:".format(key))
                    time.sleep(2)
                    for value in crawler_output[2][key]:
                        print("\n\nThe comment\n\t{}\n was found at line number {},\n"
                              "and ended on line {}.".format(value[0], value[1], value[2]))
                        time.sleep(0.1)
        elif post_input == "4":
            if not crawler_output[3]:
                print("Sadly, the list is empty.")
            else:
                print([x for x in crawler_output[3]])
        elif post_input == "5":
            if not crawler_output[4]:
                print("Sadly, the list is empty.")
            else:
                print([x for x in crawler_output[4]])
        elif post_input == "6":
            if not crawler_output[5]:
                print("Sadly, the list is empty.")
            else:
                for word, count in crawler_output[5]:
                    print("The word {} was found {} times.\n".format(word, count))
                    time.sleep(0.1)
        elif post_input == "7":
            print("List of email addresses:\n{}\n".format(output[0]))
            print("List of phone numbers:\n{}\n".format(output[1]))
            print("Dictionary of comments discovered:\n{}\n".format(output[2]))
            print("List of data identified with user specified regex:\n{}\n".format(output[3]))
            print("List of the 100 most frequently used words:\n{}\n".format(output[4]))
            print("List of the 100 most frequently used words and their count:\n{}\n".format(output[5]))
        else:
            print("Program terminated.\nHave a splendid morning, day, afternoon, evening, or night!")
            time.sleep(1)
            print("3..")
            time.sleep(1)
            print("2..")
            time.sleep(1)
            print("1..")
            exit()


def run_crawler(input_kwargs=None):
    """
    Simple function that instantiates a Crawler object, runs its crawl() and analyze(), and returns its results.
    :param input_kwargs: A dictionary containing:
    URL, depth of recursion, maximum/total amount of subpages, and a list of user-defined regex.
    :return: Output object from the Analyzer.
    """
    if input_kwargs is None:
        input_kwargs = {
            "input_url": URL,
            "input_depth": DEPTH,
            "input_total": TOTAL,
            "input_regex": REGEX
        }
    web_crawler = Crawler.Crawler(**input_kwargs, crawl=CRAWL, analyze=ANALYZE)
    web_crawler.crawl()
    analyzer_output = web_crawler.analyze()
    return analyzer_output


if __name__ == '__main__':
    """
    If this python script is the main process, the code below is executed.
    """
    #   Initialize variables for user input.
    output, user_url, user_depth, user_total, user_regex, user_bool = (), "", 0, 0, [], True
    #   Choose to input parameters or try defaults.
    command = input("Would you like to set up your own parameters? y/n\n")
    if command.lower() == "n":
        print("Running the webcrawler with default parameters, please wait.")
        output = run_crawler()
    elif command.lower() == "y":
        command = input(
            "\nHow would you like to run the program?:\n"
            "1. Crawl the web, download pages and analyze.\n"
            "2. Just crawl the web and download pages.\n"
            "3. Just analyze pages that have already been downloaded.\n")
        if command == "1":
            CRAWL, ANALYZE = True, True
        elif command == "2":
            CRAWL, ANALYZE = True, False
        elif command == "3":
            CRAWL, ANALYZE = False, True
        #   Set url, format explained.
        user_url = input("Please enter a URL on the form 'address.domain',\n"
                         "like 'google.com'.\n"
                         "Do not worry about protocol or 'www':\n")
        #   Set the depth of crawler recursion (subpage within subpage).
        user_depth = int(input("Please enter the desired depth of crawler recursion as an integer,\n"
                               "where a depth of 0 will result in only the main page being downloaded,\n"
                               "and a depth of 1 will result in all the links discovered in the main "
                               "page being subject to downloads.\n"
                               "A maximum depth of 3 is recommended, but not enforced:\n"))
        #   Set the maximum/total amount of subpages to download.
        user_total = int(input("Please enter the maximum/total amount of subpages to download,\n"
                               "where the default value is 100, "
                               "the minimum value is 10, "
                               "and the maximum value is 1000\n"))
        while user_bool:
            user_input = input("Please enter a valid regex, or enter c to continue.\n"
                               "For help with regex syntax, visit https://docs.python.org/3/howto/regex.html\n")
            if user_input.lower() == "c":
                user_bool = False
            elif not isinstance(user_input, str):
                print("Invalid entry. Please enter a string.")
                continue
            else:
                user_regex.append(user_input)
        print("Running the webcrawler with your parameters, please wait.")
        output = run_crawler({
            "input_url": user_url,
            "input_depth": user_depth,
            "input_total": user_total,
            "input_regex": user_regex
        })
    print("\nThe web has been successfully crawled! *spider noises*")
    #   Run the post crawl loop for viewing the collected data.
    post_crawler_loop(output)
