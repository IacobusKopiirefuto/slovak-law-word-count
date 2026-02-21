"""Output Functions Module.

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
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

try:
    from wordcloud import WordCloud
except ImportError:
    WordCloud = None

NEGATIVE_INFINITY = float("-inf")
POSITIVE_INFINITY = float("inf")

AnalysisOutput = dict[str, dict[str, Any]]


def csv_count_output(
    output: AnalysisOutput,
    fields: list[str],
    csv_name: str = "count_output",
) -> None:
    """Generate a CSV table for single-number metrics for all analyzed files.

    Args:
        output: Nested dictionary with analysis results for each file.
        fields: Metric names to include in the CSV table.
        csv_name: Output CSV base name (without extension).

    """
    list_output = [["Date", *fields]]

    # converts nested dictionary `output` to into a list of lists `list_output`

    # Iterate through each date (that is analysis results for given file)
    # and corresponding stats in the output dictionary `output`
    for date, stats in output.items():
        # Create a row for the current date
        row = [date]

        # Extending the Row with Selected Fields in the Order of 'fields' List:
        row.extend(str(stats.get(field, "")) for field in fields)

        # PREVIOUSLY USED FUNCTION
        # Extend the row with values for the selected fields
        # iterates through the key-value pairs in the stats dictionary
        # and appends the values to the row list only if the corresponding key
        # is present in the fields list.
        # The values are converted to strings before appending.
        # row.extend(str(value) for key, value in stats.items() if key in fields)

        list_output.append(row)

    # Define the custom sorting function
    def sort_function(row: list[str]) -> int | float:
        if row[0] == "vyhlasene_znenie":
            return NEGATIVE_INFINITY
        if row[0].isdigit():
            return int(row[0])
        return POSITIVE_INFINITY

    # Sort the rows based on the custom function
    data_sorted = sorted(list_output[1:], key=sort_function)

    # Insert the header row at the beginning
    data_sorted.insert(0, list_output[0])

    # Write the sorted data to a new CSV file
    with Path(f"{csv_name}.csv").open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data_sorted)


def csv_lemma_out(output: AnalysisOutput) -> None:
    """Write a CSV file with the most frequent lemmas for each analyzed file.

    Args:
        output: Dictionary containing analysis results for each file.

    """
    for key, value in output.items():
        with Path(f"{key}_lemma_counts.csv").open(
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["lemma", "count"])
            for lemma, count in value["lemma_counts"].items():
                writer.writerow([lemma, count])


def csv_tag_out(output: AnalysisOutput) -> None:
    """Generate CSV tables for word-category frequencies for each analyzed file.

    Args:
        output: Dictionary containing analysis results for each file.

    """
    for key, value in output.items():
        with Path(f"{key}_tag.csv").open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["tag", "count"])
            for tag, count in value["tag_frequencies"].items():
                writer.writerow([tag, count])


def plot_data(
    plot_data_variable: str,
    output: AnalysisOutput,
    plot_title: str,
    plot_ylabel: str,
    *,
    show_plot: bool = False,
) -> None:
    """Generate a bar chart for one metric, ordered by year.

    Args:
        plot_data_variable: Metric key to plot (for example, `word_count`).
        output: Dictionary containing analysis results for each file.
        plot_title: Plot title.
        plot_ylabel: Y-axis label.
        show_plot: If `True`, display the plot instead of saving it.

    """
    # Extract the last ID with each first 4 digits
    last_ids = {}
    for date in output:
        # first_4_digits = date[:4]
        if date[:4] not in last_ids or date > last_ids[date[:4]]:
            last_ids[date[:4]] = date

    # Get the data for plotting using the last IDs (excluding 'vyhlasenie_znenie')
    word_counts = [
        (last_ids[date[:4]], data[plot_data_variable])
        for date, data in output.items()  # OLD: version only 'vyhlasene_znenie' is not plotted, NEW: only numerical are plotted  #               data in output.items() if date != 'vyhlasene_znenie']
        if date.isdigit()
    ]
    word_counts.sort(key=lambda x: x[0])  # Sort by date

    # Create x and y arrays for plotting
    x_array = [
        item[0][:4] for item in word_counts
    ]  # Display only the first four digits
    y_array = [item[1] for item in word_counts]

    # Plot the data
    plt.clf()  # Clear the plot before plotting new data
    plt.bar(x_array, y_array)  # Use plt.bar() for a bar graph
    plt.xticks(rotation=90)
    plt.xlabel("rok")
    plt.ylabel(plot_ylabel)
    plt.title(plot_title)
    plt.grid(axis="y")  # Add gridlines to the y-axis
    plt.tight_layout()
    if show_plot:
        plt.show()
    else:
        plt.savefig(plot_data_variable + ".png")
    plt.clf()  # Clear the plot before plotting new data


# from wordcloud import WordCloud


def word_cloud(
    lemma_counts: dict[str, int],
    file_name: str = "wordcloud",
    stop_words: list[str] | None = None,
    *,
    show_plot: bool = False,
) -> None:
    """Create a word cloud of frequent lemmas while excluding stop words.

    Args:
        lemma_counts: Mapping of lemma to frequency.
        file_name: Output image base name.
        stop_words: Stop words to remove before rendering.
        show_plot: If `True`, display the plot instead of saving it.

    """
    # Check if lemma_counts is empty and return early if true
    if not lemma_counts:
        print("Lemma counts is empty. Skipping word cloud generation.")
        return

    if WordCloud is None:
        print(
            "Skipping word cloud generation: install extra 'stanza' for wordcloud support.",
        )
        return

    # To avoid W0102: Dangerous default value [] as argument (dangerous-default-value)
    # stop_words default value is None and changes to [] only inside the function
    if stop_words is None:
        stop_words = []

    lemma_counts = {
        word: count for word, count in lemma_counts.items() if word not in stop_words
    }

    word_cloud_data = WordCloud(
        width=800,
        height=800,
        background_color="white",
        min_font_size=10,
    )
    word_cloud_data.generate_from_frequencies(lemma_counts)

    plt.clf()  # Clear the plot before plotting new data
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(word_cloud_data)
    plt.axis("off")
    plt.tight_layout(pad=0)
    if show_plot:
        plt.show()
    else:
        plt.savefig(file_name + ".png", bbox_inches="tight")
    plt.clf()  # Clear the plot after plotting new data
