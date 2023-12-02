"""
Output Functions Module

This module provides functions for generating various output formats based on the analysis results.
It includes functionality for creating CSV tables, bar charts, and word clouds.

Functions:
    - `csv_count_output(output, fields, csv_name='count_output')`:
        Generates a CSV table for single-number metrics for all analyzed files.

    - `csv_lemma_out(output)`:
        Writes out a CSV file with the most frequent lemmas for each analyzed file.

    - `csv_tag_out(output)`:
        Generates CSV tables for word category frequencies (tags) for each analyzed file.
        Additionally, creates an aggregated CSV file with all tag frequencies.

    - `plot_data(plot_data_variable, output, plot_title, plot_ylabel, show_plot=False)`:
        Generates a bar chart for a specified metric, with files ordered by year.

    - `word_cloud(lemma_counts, file_name='wordcloud', show_plot=False, stop_words=None)`:
        Creates a word cloud of the most frequent lemmatized words, excluding stop words.

Usage:
    1. Import the module: `from output_fun import csv_count_output, plot_data, word_cloud`
    2. Utilize the functions to generate and save various output formats.

For more detailed information, refer to the individual function docstrings.
"""

# Copyright 2023 Jakub Škoda
# SPDX-License-Identifier: AGPL-3.0-only

import csv
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def csv_count_output(output, fields, csv_name='count_output'):
    """
    Generates a CSV table for single-number metrics for all analyzed files.

    Parameters:
        - `output` (dict): A nested dictionary containing analysis results for each file.
        - `fields` (list): A list of metric names to include in the CSV table.
        - `csv_name` (str): The desired name of the output CSV file (default is 'count_output').

    Returns:
        None

    Usage:
        csv_count_output(output, ['word_count', 'char_count'], 'analysis_results')
    """

    list_output = [['Date'] + fields]

    # converts nested dictionary `output` to into a list of lists `list_output`

    # Iterate through each date (that is analysis results for given file)
    # and corresponding stats in the output dictionary `output`
    for date, stats in output.items():
        # Create a row for the current date
        row = [date]

        # Extending the Row with Selected Fields in the Order of 'fields' List:
        for field in fields:
            row.append(str(stats.get(field, '')))

        # PREVIOUSLY USED FUNCTION
        # Extend the row with values for the selected fields
        # iterates through the key-value pairs in the stats dictionary
        # and appends the values to the row list only if the corresponding key
        # is present in the fields list.
        # The values are converted to strings before appending.
        # row.extend(str(value) for key, value in stats.items() if key in fields)

        list_output.append(row)

    # Define the custom sorting function
    def sort_function(row):
        if row[0] == 'vyhlasene_znenie':
            return float('-inf')
        if row[0].isdigit():
            return int(row[0])
        return float('inf')

    # Sort the rows based on the custom function
    data_sorted = sorted(list_output[1:], key=sort_function)

    # Insert the header row at the beginning
    data_sorted.insert(0, list_output[0])

    # Write the sorted data to a new CSV file
    with open(csv_name + '.csv', 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data_sorted)


def csv_lemma_out(output):
    """
    Writes out a CSV file with the most frequent lemmas for each analyzed file.

    Parameters:
        - `output` (dict): A dictionary containing analysis results for each file.

    Returns:
        None

    Usage:
        csv_lemma_out(output)
    """
    for key, value in output.items():
        with open(f"{key}_lemma_counts.csv", "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["lemma", "count"])
            for lemma, count in value["lemma_counts"].items():
                writer.writerow([lemma, count])


def csv_tag_out(output):
    """
    Generates CSV tables for word category frequencies (tags) for each analyzed file.
    Additionally, creates an aggregated CSV file with all tag frequencies.

    Parameters:
        - `output` (dict): A dictionary containing analysis results for each file.

    Returns:
        None
        saves {key}_tag.csv in a directory

    Usage:
        csv_tag_out(output)
    """

    for key, value in output.items():
        with open(f"{key}_tag.csv", "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["tag", "count"])
            for tag, count in value["tag_frequencies"].items():
                writer.writerow([tag, count])


def plot_data(plot_data_variable, output, plot_title, plot_ylabel, show_plot=False):
    """
     Generates a bar chart for a specified metric, with files ordered by year.
     From each year only the latest file for that year is graphed.

     Parameters:
         - `plot_data_variable` (str): The metric to be plotted
         (e.g., 'word_count', 'char_count').
         - `output` (dict): A dictionary containing analysis results for each file.
         - `plot_title` (str): The title of the generated plot.
         - `plot_ylabel` (str): The label for the y-axis of the generated plot.
         - `show_plot` (bool): If True, the plot is displayed;
         if False (default), the plot is saved.

     Returns:
         None
         saves {plot_data_variable}.png in a directory


     Usage:
         plot_data('word_count', output, 'Word Count Analysis', 'Word Count')
    """
    # Extract the last ID with each first 4 digits
    last_ids = {}
    for date, data in output.items():
        # first_4_digits = date[:4]
        if date[:4] not in last_ids or date > last_ids[date[:4]]:
            last_ids[date[:4]] = date

    # Get the data for plotting using the last IDs (excluding 'vyhlasenie_znenie')
    word_counts = [(last_ids[date[:4]], data[plot_data_variable]) for date,
    #               data in output.items() if date != 'vyhlasene_znenie']
    # OLD: version only 'vyhlasene_znenie' is not plotted, NEW: only numerical are plotted
                   data in output.items() if date.isdigit()]
    word_counts.sort(key=lambda x: x[0])  # Sort by date

    # Create x and y arrays for plotting
    x_array = [item[0][:4] for item in word_counts]  # Display only the first four digits
    y_array = [item[1] for item in word_counts]

    # Plot the data
    plt.clf()  # Clear the plot before plotting new data
    plt.bar(x_array, y_array)  # Use plt.bar() for a bar graph
    plt.xticks(rotation=90)
    plt.xlabel('rok')
    plt.ylabel(plot_ylabel)
    plt.title(plot_title)
    plt.grid(axis='y')  # Add gridlines to the y-axis
    plt.tight_layout()
    if show_plot:
        plt.show()
    else:
        plt.savefig(plot_data_variable + '.png')
    plt.clf()  # Clear the plot before plotting new data


# from wordcloud import WordCloud

def word_cloud(lemma_counts, file_name='wordcloud', stop_words=None, show_plot=False):
    """
    Creates a word cloud of the most frequent lemmatized words, excluding stop words.

    Parameters:
        - `lemma_counts` (dict): A dictionary containing lemma counts for each analyzed file.
        - `file_name` (str): The desired name of the output word cloud image
        (default is 'wordcloud').
        - `show_plot` (bool): If True, the word cloud is displayed; if False (default),
        it is saved.
        - `stop_words` (list): A list of stop words to be excluded from the word cloud.

    Returns:
        None
        save's {file_name}.png in a directory

    Usage:
        word_cloud(output['file_name']['lemma_counts'], 'wordcloud', True, default_stop_words)
    """

    # Check if lemma_counts is empty and return early if true
    if not lemma_counts:
        print("Lemma counts is empty. Skipping word cloud generation.")
        return

    # To avoid W0102: Dangerous default value [] as argument (dangerous-default-value)
    # stop_words default value is None and changes to [] only inside the function
    if stop_words is None:
        stop_words = []

    lemma_counts = {word: count for word,
                    count in lemma_counts.items() if word not in stop_words}

    word_cloud_data = WordCloud(width=800, height=800,
                   background_color='white',
                   min_font_size=10)
    word_cloud_data.generate_from_frequencies(lemma_counts)

    plt.clf()  # Clear the plot before plotting new data
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(word_cloud_data)
    plt.axis("off")
    plt.tight_layout(pad=0)
    if show_plot:
        plt.show()
    else:
        plt.savefig(file_name + '.png', bbox_inches='tight')
    plt.clf()  # Clear the plot after plotting new data
