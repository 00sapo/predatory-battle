#! /usr/bin/env python2
import string
import re
import operator
import os
import time
import sys
import codecs

import requests
import latexcodec
from fuzzywuzzy import fuzz
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 

# the number of days aftwer which the lists are updated
UPDATE_DAYS = 30

CHECK_LIST = {
    # predatoryjournals.com
    'predatory_list': "https://predatoryjournals.com/journals/",
    # Bealls list
    'bealls_list': "https://beallslist.weebly.com/",
    # Bealls list - standalone journals
    'bealls_list_journals': "https://beallslist.weebly.com/standalone-journals.html",
    # Fake DOAJ journals
    'fake_doaj': "https://docs.google.com/spreadsheets/d/1Y_Sza4rPDkf-NNX9kwiErGrKeNTM75md9B63A_gVpaQ/export?format=csv",
    # Questionable conferences
    'questionable_conferences': "https://libguides.caltech.edu/c.php?g=512665&p=3503029"
}

FIELD_LIST = ('booktitle', 'journal', 'maintitle', 'journaltitle', 'issuetitle', 'eventtitle')

try:
    STOP_WORDS = set(stopwords.words('english')) 
except LookupError:
    # downloading stop words
    import nltk
    nltk.download('stopwords')
    STOP_WORDS = set(stopwords.words('english')) 

PUNCTUATION_FILTER = str.maketrans("", "", string.punctuation)

REGEX = re.compile('<.*?>')


def clean(text):
    """
        Clean text: remove trailing spaces, html tags, punctuation, stopwords
        and convert to lower case
    """
    # removing html tags
    text = re.sub(REGEX, '', text)

    # removing punctuation
    text = text.translate(PUNCTUATION_FILTER)
  
    # removing stop words
    word_tokens = word_tokenize(text) 
    filtered_text = [] 
    for w in word_tokens: 
        if w not in STOP_WORDS: 
            filtered_text.append(w) 
    text = " ".join(str(x) for x in filtered_text)

    # removing trailing spaces and lowering
    return text.lower().strip()


def update_lists():
    """
        Simply download pages containing lists to txt files, representing html
        or csv. The global variable `CHECK_LIST` and `UPDATE_DAYS` must be
        setted. It always returns a dictionary of strings representing the
        {web-address: content-of-file}, even if they are already updated.
    """

    returned = {}
    for (name, address) in CHECK_LIST.items():
        name_path = name + '.txt'
        # checking date of last modification
        file_exists = os.path.isfile(name_path)
        if file_exists:
            file_is_old = time.time() - os.path.getmtime(name_path)\
                > UPDATE_DAYS * 24 * 3600
        if not file_exists or file_is_old:
            print("Downloading " + name + "...")
            # Warning! I'm having troubles with SSL handshake, so I'm turning
            # verification off. Not recommended!
            response = requests.get(address, verify=False)
            if response.status_code != 200:
                print("Can't download " + name + "!!")
                continue
            # force encoding
            response.encoding = 'utf-8'
            content = response.text
            content = clean(content)

            with open(name_path, 'w') as file:
                file.write(content)
            print("Downloaded and written to " + name + ".txt")
            
        with open(name_path, 'r') as file:
            returned[address] = file.read()
    return returned


def parse_bib_file(filename):
    """
        Simply parse the bib file given as argument and returns a
        dictionary with {bibtek-key: [strings]} pairs, where `strings`
        represent the name of journals, proceedings, books, collections.
        This function needs the global variable `FIELD_LIST`.
    """
    def _error(start, end):
        if end == -1 or start == 0:
            raise RuntimeError('Error in bibtex formatting. Please,\
                format it with tools like `biber` or`jabref`')

    output_dict = {}
    key = ""
    journal_list = []
    with open(filename, 'r') as bib_file:
        for line in bib_file:
            line = line.strip()
            if line.startswith('@'):
                # add old key
                if len(key) > 0:
                    if len(journal_list) > 0:
                        output_dict[key] = journal_list
                    else:
                        print("WARNING! No journal found for " + key)

                # search new key
                start = line.find('{') + 1
                end = line.find(',')
                _error(start, end)
                key = clean(line[start:end])
                journal_list = []
            elif line.startswith(FIELD_LIST):
                start = line.find('{') + 1
                end = line.rfind('}')
                _error(start, end)
                journal_name = line[start:end]
                codecs.decode(journal_name, "ulatex")
                journal_list.append(clean(journal_name))

    return output_dict

def parse_pdf_file(filename):
    """
        Simply parse the pdf file given as argument and returns a
        dictionary with {generated-key: [strings]} pairs, where `strings`
        represent the name of journals, proceedings, books, collections.
        This function needs the global variable `FIELD_LIST`.
    """
    import refextract.refextract as ref 
    references = ref.extract_references_from_file(filename)
    output = {}

    for ref in references:
        key = ref['texkey'][0]
        journal_name = ref['journal_title']
        output[key] = journal_name
    
    return output

def parse_file():
    """
        Depending on the extension of the file passed as command line argument,
        it calls `parse_pdf_file` or `parse_bib_file`.
    """
    filename = sys.argv[1] 
    if filename.endswith('.pdf'):
        return parse_pdf_file(filename)
    elif filename.endswith('.bib'):
        return parse_bib_file(filename)
    else:
        print("Unknown file extension for: " + filename)
        sys.exit(2)

def search(journal_dict, string_dict):
    """
        This function uses fuzzywuzzy to search journal names in the list of
        string_dict provided as argument. It prints to video the results.
    """
    def _output(score):
        print("________________________________________________\n")
        print("WARNING! " + key + " can be a predatory publication!")
        print("  match score: " + score)
        print("  suspect journal: " + journal)
        print("  it seems listed at: " + address)
    
    print("\n\nLOOKING FOR EXACT MATCHES..")
    # search exact matches
    for key, journal_list in list(journal_dict.items()):
        exact_match = False
        for journal in journal_list:
            for address, string in string_dict.items():
                if string.find(journal) > 0:
                    _output("EXACT MATCH")
                    del journal_dict[key]
                    exact_match = True
                    break
            if exact_match:
                break

    print("\n\nLOOKING FOR APPROXIMATE MATCHES (most of them will be false positives)..")
    # search additional approximate matches
    for key, journal_list in journal_dict.items():
        for journal in journal_list:
            matched_lists = {}
            for address, string in string_dict.items():
                    match_score = fuzz.token_set_ratio(journal, string)
                    if match_score > 96:
                        matched_lists[address] = match_score
            # take the list with the maximum match score
            if len(matched_lists) > 0:
                address = max(matched_lists.items(), key=operator.itemgetter(1))[0]
                _output(str(matched_lists[address]))
                break




if __name__ == '__main__':
    string_dict = update_lists()
    journal_dict = parse_file()
    search(journal_dict, string_dict)
    print("\nCheck out http://thinkchecksubmit.org for a guideline against predatory publishing!")

    print("\nRemember that this tool does not handle abbreviations very well...")
