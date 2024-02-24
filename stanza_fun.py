"""
Functions using the Stanza NLP package for text analysis.

This module provides functions that leverage the Stanza NLP library
to perform various text analysis tasks, including
sentence extraction, part-of-speech tagging, readability estimation, and lemmatization.

Functions:
    - `s_load(text)`:
        Load text into Stanza for further processing.

    - `s_sentences(nlp_text)`:
        Calculate the number of sentences and their average length.

    - `s_tags(nlp_text, word_count, stop_words=None)`:
        Count the frequency of each part-of-speech tag.

    - `s_readability(nlp_text, word_count, sent_count)`:
        Estimate the reading level required to understand the text.

    - `s_lemma(nlp_text, stop_words=None)`:
        Lemmatize the words using Stanza.

Usage:
    1. Import the module: `import stanza_fun`
    2. Load text into Stanza using `s_load`.
    3. Utilize the functions to perform various text analysis tasks.

For more detailed information, refer to the individual function docstrings
and official Stanza documentation <https://stanfordnlp.github.io/stanza/index.html>
"""

# Copyright 2023 Jakub Škoda
# SPDX-License-Identifier: AGPL-3.0-only

import sys

from collections import Counter
from urllib3.exceptions import NameResolutionError

import pyphen

import stanza
from stanza.pipeline.core import DownloadMethod

def s_load(text):
    """
    Load text into Stanza for further processing.

    Args:
        text (str): The input text to be processed.

    Returns:
        stanza.models.common.doc.Document: Stanza document representation.
    """
    # Initialize the Stanza pipeline
    nlp = stanza.Pipeline(lang="sk",
    download_method=DownloadMethod.REUSE_RESOURCES)  # , processors='tokenize, sentiment')

    try:
        stanza.download("sk")
    except ConnectionError as conn_error:
        print(f"Connection error while downloading resources: {conn_error}")
        sys.exit(1)
    except NameResolutionError as dns_error:
        print(f"Failed to resolve host while downloading resources: {dns_error}")
        sys.exit(1)
    except stanza.exceptions.DoesNotExistError as exception:
        print(f"Error downloading resources: {exception}")
        sys.exit(1)
    except stanza.exceptions.StanzaResourceException as exception:
        print(f"Error downloading resources: {exception}")
        sys.exit(1)


    # Use Stanza to process the text
    nlp_text = nlp(text)
    return nlp_text

def s_sentences(nlp_text):
    """
    Calculate the number of sentences and their average length.

    Args:
        nlp_text (stanza.models.common.doc.Document): Stanza document representation.

    Returns:
        dict: A dictionary containing the count of sentences and the average sentence length,
        and the 5 longest sentences.
    """
    # Get the number of sentences and average sentence length
    sent_count = len(nlp_text.sentences)
    avg_sent_length = sum(len(sentence.words) for sentence in nlp_text.sentences) / sent_count

    # Get and `n_longest` sentences

    # Get the lengths of all sentences
    sent_lengths = [(i, len(sentence.words)) for i, sentence in enumerate(nlp_text.sentences)]

    # Sort sentences by length in descending order
    sorted_sentences = sorted(sent_lengths, key=lambda x: x[1], reverse=True)

    # Get the indices of the 5 longest sentences
    longest_sentence_indices = [index for index, _ in sorted_sentences[:5]]

    # Get the actual sentences using the indices
    longest_sentences = [nlp_text.sentences[index].text for index in longest_sentence_indices]

    return {
                "sent_count": sent_count,
                "avg_sent_length": avg_sent_length,
                "longest_sentences": longest_sentences,
            }


def s_tags(nlp_text, word_count, stop_words=None):
    """
    Count the frequency of each part-of-speech tag.

    Args:
        nlp_text (stanza.models.common.doc.Document): Stanza document representation.
        word_count (int): The total number of words in the input text.
        stop_words (list, optional): List of stop words to be excluded.

    Returns:
        dict: A dictionary containing the frequency of each part-of-speech tag.

    ````
    abbreviations = {
        'ADJ': 'adjective',
        'ADP': 'adposition',
        'ADV': 'adverb',
        'AUX': 'auxiliary',
        'CCONJ': 'coordinating conjunction',
        'DET': 'determiner',
        'INTJ': 'interjection',
        'NOUN': 'noun',
        'NUM': 'numeral',
        'PART': 'particle',
        'PRON': 'pronoun',
        'PROPN': 'proper noun',
        'PUNCT': 'punctuation',
        'SCONJ': 'subordinating conjunction',
        'SYM': 'symbol',
        'VERB': 'verb',
        'X': 'other'
    }
    ```

    For further explanation of the tags see
<https://universaldependencies.org/u/pos/>
    """

    # To avoid W0102: Dangerous default value [] as argument (dangerous-default-value)
    # stop_words default value is None and changes to [] only inside the function
    if stop_words is None:
        stop_words = []

    tag_counts = {}
    for sent in nlp_text.sentences:
        for word in sent.words:
            # Skip stop words if provided
            if stop_words and word.text.lower() in stop_words:
                continue
            tag = word.upos
            if tag not in tag_counts:
                tag_counts[tag] = 1
            else:
                tag_counts[tag] += 1

    tag_frequencies = {tag: count / word_count for tag,
                       count in tag_counts.items()}

    s_tag_word_count = sum(tag_counts.values())

    return tag_frequencies, s_tag_word_count

def s_readability(nlp_text, word_count, sent_count):
    """
    Estimate the reading level required to understand the text by
    calculating FKGL (Flesch-Kincaid Grade level) and GFI (Gunning Fog Index).

    Complex words are here defined as words with three or more syllables.

    Uses pyphen library.

    Args:
        nlp_text (stanza.models.common.doc.Document): Stanza document representation.
        word_count (int): The total number of words in the input text.
        sent_count (int): The number of sentences in the input text.

    Returns:
        dict: A dictionary containing the FKGL and GFI readability metrics.
   """

    # Load the Pyphen hyphenation dictionary for Slovak
    dic = pyphen.Pyphen(lang="sk")

    # Initialize variables for word and syllable counts
    all_word_count = 0
    syllable_count = 0
    complex_word_count = 0

    # Iterate over sentences and tokens
    for sent in nlp_text.sentences:
        for token in sent.tokens:
            # Count words and syllables
            all_word_count += 1
            syllable_count += len(dic.inserted(token.text).split("-"))
            # Check if word is complex
            if len(dic.inserted(token.text).split("-")) >= 3:
                complex_word_count += 1

    fkgl = 0.39 * (word_count / sent_count) + 11.8 * (syllable_count / word_count) - 15.59
    gfi = 0.4 * ((word_count / sent_count) + 100 * (complex_word_count / word_count))
    return {
                "FKGL": fkgl,
                "GFI": gfi,
                "syllable_count": syllable_count,
                "complex_word_count": complex_word_count,
                "all_word_count": all_word_count,
            }



def s_lemma(nlp_text, stop_words=None):
    """
   Lemmatize the words using Stanza.

    Args:
        nlp_text (stanza.models.common.doc.Document): Stanza document representation.
        stop_words (list, optional): List of stop words to be excluded.

    Returns:
        Counter: A Counter object containing the frequency of each lemma.
    """
    lemmas = []


    # To avoid W0102: Dangerous default value [] as argument (dangerous-default-value)
    # stop_words default value is None and changes to [] only inside the function
    if stop_words is None:
        stop_words = []

    for sentence in nlp_text.sentences:
        for token in sentence.tokens:
            lemma = token.words[0].lemma
            # are stop words not already removed?
            if lemma.isalpha() and lemma not in stop_words:
                lemmas.append(lemma)

    lemma_counts = Counter(lemma for lemma in lemmas if lemmas.count(lemma) >= 5)

    return lemma_counts
