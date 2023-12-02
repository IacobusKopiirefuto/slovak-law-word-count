"""
Processing Functions Module

This module provides general-purpose functions for
processing HTML files and extracting relevant information. 
It serves as the backbone for many other analysis scripts in this project.

Functions:
    - `load_html_file(filename)`: 
        Loads an HTML file, extracts the content
        within a specific div element, and returns the text.

    - `simple_count(text, stop_words)`: 
        Computes various text metrics, including word count, character count, 
        word count without stop words, and type-token ratio.

    - `analyze_documents_in_folder(folder_path, process_func, stop_words=None)`: 
        Analyzes HTML documents in a folder using a specified processing function.
        Allows for sorting documents based on specific criteria.

Usage:
    1. Import the module: `from processing_fun import analyze_documents_in_folder, simple_count`
    2. Utilize the functions for processing HTML files and extracting key information.

For more detailed information, refer to the individual function docstrings.
"""
# Copyright 2023 Jakub Škoda
# SPDX-License-Identifier: AGPL-3.0-only

import os
import sys

from bs4 import BeautifulSoup

def load_html_file(filename):
    """
    Loads an HTML file, extracts text from a specific div element, and returns it.

    Args:
        filename (str): The path to the HTML file.

    Returns:
        str or None: The extracted text if found, else None.
    """
    print(f"processed file: {filename}")
    with open(filename, encoding="utf-8") as html_file:
        soup = BeautifulSoup(html_file, "html.parser")

    # Find the desired div element by its class and ID
    div = soup.find("div", {"class": "predpis Skupina", "id": "predpis"})

    if div is None:
        return None

    text = div.get_text()

    if not isinstance(text, str):
        print("Error: 'text' is not a string. Ending the script.")
        sys.exit(1)

    return text

def simple_count(text, stop_words=None):
    """
    Computes basic text metrics including word count, character count,
    word count without stop words, and type-token ratio.

    Type toke ratio is dividing the number of unique words by
    the total number of words in the text.

    Args:
        text (str): The input text.
        stop_words (list): A list of stop words to exclude from word count.

    Returns:
        dict: A dictionary containing word count, character count,
              word count without stop words, and type-token ratio.
    """
    if not isinstance(text, str):
        print("Error: 'text' is not a string. Ending the script.")
        sys.exit(1)

    # To avoid W0102: Dangerous default value [] as argument (dangerous-default-value)
    # stop_words default value is None and changes to [] only inside the function
    if stop_words is None:
        stop_words = []

    word_count = len(text.split())  # word_count including stop words
    char_count = len(text.replace(" ", ""))  # character count without spaces

    # Removes stop words
    words = [word for word in text.split() if word.lower() not in stop_words]
    word_count_stop = len(words)

    # Calculate type-token ratio
    # dividing the number of unique words by the total number of words in the text
    type_token_ratio = len(set(words)) / len(words)

    return {
            "word_count": word_count,  # word_count including stop words
            "char_count": char_count,  # character count without spaces
            "word_count_stop": word_count_stop,  # word count without stop words
            "type_token_ratio": type_token_ratio,
            }

def analyze_documents_in_folder(folder_path, process_func, stop_words=None):
    """
    Analyzes documents in a folder using a specified processing function.

    Documents names are sorted in this order:

    1. vyhlasene_znenie.html goes first, if present
    2. all documents with digit-only filenames go in ascending order

    3. everything else after that


    Args:
        folder_path (str): The path to the folder containing documents.
        process_func (callable): The processing function to apply to each document.
        stop_words (list): A list of stop words to exclude from word count.

    Returns:
        dict: A dictionary containing analyzed documents with document names as keys.
    """
    # To avoid W0102: Dangerous default value [] as argument (dangerous-default-value)
    # stop_words default value is None and changes to [] only inside the function
    if stop_words is None:
        stop_words = []

    analyzed_documents = {}
    def custom_key(value):
        if value == 'vyhlasene_znenie.html':
            return 0
        if value != 'vyhlasene_znenie.html':
            try:
                return int(value.split('.')[0])
            except ValueError:
                return float('inf')
        return None

    for file_name in sorted(os.listdir(folder_path), key=custom_key):
        # Check if file has an eight-digit number name followed by ".html" extension
        # Kinda duplicity, could be done in custom_kye
        if not (file_name.endswith('.html') or
                (file_name != "vyhlasene_znenie.html" and
                 (not file_name[:-5].isdigit() or len(file_name[:-5]) != 8))):
            print(f"skipping file: {file_name}")
            continue
        if file_name.endswith('.html'):
            document_name = file_name[:-5]  # Remove the .html suffix
            file_path = os.path.join(folder_path, file_name)
#            with open(file_path, 'r') as file:
#                html_content = file.read()
            analyzed_document = process_func(file_path, stop_words)
            analyzed_documents[document_name] = analyzed_document
    return analyzed_documents
