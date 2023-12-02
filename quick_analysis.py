"""
Quick Analysis Module

This module provides functionality for rapid analysis of HTML documents without heavy dependencies. 

It relies primarily on the `processing_fun` module for processing HTML files efficiently. 
Designed for quick analysis tasks on machines with limited RAM.

Functions:
    - `q_file_analysis(filename, stop_words=None)`: 
        Analyzes an HTML file and returns basic text metrics.
    
    - `q_analysis(folder_path, stop_words=None, nazov_zakona='')`:
        Runs analysis on all HTML files in a folder using `q_file_analysis`.

Usage:
    1. Import the module: `from quick_analysis import q_analysis`
    2. Analyze a folder of HTML documents with minimal resource consumption.

Note: Ensure that the required files, such as `output_fun.py`, `processing_fun.py`,
      and others are present in the same directory or available in the Python path.

For more detailed information, refer to the individual function docstrings.
"""

# Copyright 2023 Jakub Škoda
# SPDX-License-Identifier: AGPL-3.0-only

import os

from output_fun import csv_count_output, plot_data
from processing_fun import analyze_documents_in_folder, load_html_file, simple_count

def q_file_analysis(filename, stop_words=None):
    """
    Analyzes an HTML file and returns basic text metrics.

    Args:
        filename (str): The path to the HTML file.
        stop_words (list): A list of stop words to exclude from word count.

    Returns:
        dict: A dictionary containing word count, character count,
        word count without stop words, and type-token ratio.
    """
    text = load_html_file(filename)

    if text is None:
        print("Could not find div element.")
        # Return a default dictionary with all values set to 0 or an empty list
        return {
                "word_count": 0,  # word_count including stop words
                "char_count": 0,  # character count without spaces
                "word_count_stop": 0,  # word count without stop words
                "type_token_ratio": 0,
               }

    counts = simple_count(text, stop_words)
    return {
            "word_count": counts['word_count'],  # word_count including stop words
            "char_count": counts['char_count'],  # character count without spaces
            "word_count_stop": counts['word_count_stop'],  # word count without stop words
            "type_token_ratio": counts['type_token_ratio'],
            }


def q_analysis(folder_path, stop_words=None, nazov_zakona=''):
    """
    Runs analysis on all HTML files in a folder using q_file_analysis.

    Args:
        folder_path (str): The path to the folder containing HTML files.
        stop_words (list): A list of stop words to exclude from word count.
        nazov_zakona (str): An optional parameter to specify the name of the law.

    Returns:
        dict: A dictionary containing analyzed documents with document names as keys.
    """
    output = analyze_documents_in_folder(folder_path, q_file_analysis, stop_words)
    os.chdir(folder_path)

    print(output)

    fields = ['word_count',
              'char_count',
              'word_count_stop',
              'type_token_ratio']

    csv_count_output(output, fields)
    plot_data('word_count', output, 'Vývoj počtu slov v ' + nazov_zakona, 'počet slov')
    plot_data('char_count', output, 'Vývoj počtu znakov v ' + nazov_zakona, 'počet znakov')
    plot_data('type_token_ratio', output,
              'Vývoj type token ratio v ' + nazov_zakona, 'type token ratio')
    return output
