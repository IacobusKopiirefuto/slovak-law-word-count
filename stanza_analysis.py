"""
Module for analyzing documents using functions from stanza_fun.py.
Provides more complex results compared to quick_analysis.py.

Functions:

- s_file_analysis(filename, stop_words=None):
  Analyzes a single document using various linguistic metrics.

- s_analysis(folder_path, stop_words=None, nazov_zakonu=''):
  Analyzes all documents in a folder and generates output.
"""

# Copyright 2023 Jakub Škoda
# SPDX-License-Identifier: AGPL-3.0-only


import os

from output_fun import csv_count_output, csv_lemma_out, csv_tag_out, plot_data, word_cloud
from processing_fun import analyze_documents_in_folder, load_html_file, simple_count
from stanza_fun import s_load, s_sentences, s_tags, s_readability, s_lemma

def s_file_analysis(filename, stop_words=None):
    """
    Analyzes a single document using various linguistic metrics.

    Parameters:
    - filename (str): The path to the document file.
    - stop_words (list): List of stop words to be excluded from analysis.

    Returns:
    dict: Dictionary containing various linguistic metrics.

    Example:
    ```python
    from stanza_fun import s_file_analysis
    from stop_words_default import default_stop_words
    result = s_file_analysis("/path/to/document.html", default_stop_words)
    ```

    Metrics:
    - 'word_count': Total word count including stop words.
    - 'char_count': Character count without spaces.
    - 'word_count_stop': Word count excluding stop words.
    - 'sent_count': Sentence count.
    - 'avg_sent_length': Average sentence length.
    - 'type_token_ratio': Type-token ratio.
    - 'FKGL': Flesch-Kincaid Grade Level.
    - 'GFI': Gunning Fog Index.
    - 'tag_frequencies': Frequencies of different word categories.
    - 'lemma_counts': Frequencies of lemmatized words.
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
                "sent_count": 0,
                "avg_sent_length": 0,
                "longest_sentences": {},
                "FKGL": 0,
                "GFI": 0,
                "syllable_count": 0,
                "complex_word_count": 0,
                "tag_frequencies": {},
                "lemma_counts": {},
                "s_readability_word_count": 0,
                "tag_word_count": 0,
               }

    counts = simple_count(text, stop_words)

    s_docu = s_load(text)
    sentences = s_sentences(s_docu)
    tag_f, tag_word_count = s_tags(s_docu, counts['word_count'], stop_words)
    readability_c = s_readability(s_docu, counts['word_count'], sentences['sent_count'])
    lemma_c = s_lemma(s_docu, stop_words)

    return {
            "word_count": counts['word_count'],  # word_count including stop words
            "char_count": counts['char_count'],  # character count without spaces
            "word_count_stop": counts['word_count_stop'],  # word count without stop words
            "sent_count": sentences['sent_count'],
            "avg_sent_length": sentences['avg_sent_length'],
            "longest_sentences": sentences['longest_sentences'],
            "type_token_ratio": counts['type_token_ratio'],
            "FKGL": readability_c['FKGL'],
            "GFI": readability_c['GFI'],
            "syllable_count": readability_c['syllable_count'],
            "complex_word_count": readability_c['complex_word_count'],
            "tag_frequencies": tag_f,
            "lemma_counts": lemma_c,
            "s_readability_word_count": readability_c['all_word_count'],
            "tag_word_count": tag_word_count,
            }


def s_analysis(folder_path, stop_words=None, nazov_zakonu=''):
    """
    Analyzes all documents in a folder and generates output.

    Parameters:
    - folder_path (str): The path to the folder containing documents.
    - stop_words (list): List of stop words to be excluded from analysis.
    - nazov_zakonu (str): Name of the law, used in plot titles.

    Returns: nothigs
    
    Save in the {folder_path}:
        - {key}_lemma_counts.csv, {key}_tag.csv for every analyzed file in the directory
        - count_output.csv with all single number metrics for all analyzed files
        - word_count.png, a word cloud for last file with
        digits only name and non-empty `lemma_counts`
        - avg_sent_length.png, char_count.png, sent_count.png, type_token_ratio.png, word_count.png
        bar charts for given variables
        (each bar stands for last version of the legislature for respective year)


    Example:
    ```python
    output = s_analysis("/path/to/documents_folder",
    stop_words=["and", "the"], nazov_zakonu="Zakon123")
    ```

    Metrics are saved in CSV files, and bar charts and word clouds are generated
    for visual analysis.
    """
    output = analyze_documents_in_folder(folder_path, s_file_analysis, stop_words)
    os.chdir(folder_path)

    fields = ['word_count',
              'word_count_stop',
    #          's_readability_word_count',
    #          'tag_word_count',
              'complex_word_count',
              'char_count',
              'syllable_count',
              'sent_count',
              'avg_sent_length',
              'type_token_ratio',
              'FKGL',
              'GFI',
              ]

    csv_count_output(output, fields)
    csv_lemma_out(output)
    csv_tag_out(output)
    plot_data('word_count', output, 'Vývoj počtu slov v ' + nazov_zakonu, 'počet slov')
    plot_data('char_count', output, 'Vývoj počtu znakov v ' + nazov_zakonu, 'počet znakov')
    plot_data('sent_count', output, 'Vývoj počtu viet v ' + nazov_zakonu, 'počet viet')
    plot_data('avg_sent_length', output,
              'Vývoj priemernej dĺžky viet v ' + nazov_zakonu, 'priemerná dĺžka viet')
    plot_data('type_token_ratio', output,
              'Vývoj type token ratio v ' + nazov_zakonu, 'type token ratio')

    # creates word cloud for newest version of the law
    last_date = list(output.keys())[-1]

    # law versions have numerical titles
    k=-1
    while not last_date.isdigit():
        k=k-1
        last_date = list(output.keys())[k]

    #ensures that it's not empty
    while not output[last_date]["lemma_counts"]:
        k=k-1
        last_date = list(output.keys())[k]

    word_cloud(output[last_date]["lemma_counts"], last_date + '_wordcloud', stop_words)
