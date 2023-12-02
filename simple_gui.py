"""
Module: `simple_gui.py`

Contains a simple GUI app for easier use of the project scripts.

Usage:
- This GUI allows users to interactively select a folder, input a URL for downloading,
and choose between full analysis or word and character count only.
- The folder path and URL provided by the user are utilized in the analysis scripts.

Example:
```python
# Run the GUI by executing this script
python simple_gui.py
```
Note:

- The GUI uses PySimpleGUI for simplicity.
- Ensure all required dependencies are installed before running the script.
- If on computer with not enough RAM, use the `Word and char count only` analysis.
"""

# Copyright 2023 Jakub Škoda
# SPDX-License-Identifier: AGPL-3.0-only

import os
import PySimpleGUI as sg
from stop_words_default import default_stop_words
from quick_analysis import q_analysis
from stanza_analysis import s_analysis
from download_fun import download_links_from_table

def analyze_folder(selected_folder_path):
    """
    Check if a valid folder path is provided and print the status.

    Parameters:
    - selected_folder_path (str): The path to the selected folder.

    Returns:
    None
    """
    if os.path.isdir(selected_folder_path):
        # Perform document analysis here
        print("Analyzing folder:", selected_folder_path)
    else:
        print("Invalid folder path:", selected_folder_path)

#layout = [
#    [sg.Text("Select a folder:")],
#    [sg.Input(), sg.FolderBrowse(key="folder_selector")],
#    [sg.Button("Analyze")]
#]

layout = [
    [sg.Text("Enter a URL:")],
    [sg.Input(key="url_input"), sg.Button("Download")],
    [sg.Text("Select a folder:")],
    [sg.Input(), sg.FolderBrowse(key="folder_selector")],
    [sg.Text("Select analysis type:")],
    [sg.Button("Full analysis"), sg.Button("Word and char count only")]
]


window = sg.Window("Document Analyzer", layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    if event == "Word and char count only":
        folder_path = values["folder_selector"]
        q_analysis(folder_path, default_stop_words, "zákone")
    if event == "Full analysis":
        folder_path = values["folder_selector"]
        s_analysis(folder_path, default_stop_words, "zákone")
    if event == "Download":
        download_url = values["url_input"]
        folder_path = values["folder_selector"]
        print(download_url)
        print(folder_path)
#        sg.popup("Downloading data")
        download_links_from_table(download_url, folder_path)
        sg.popup("Download completed")
#        save_path = os.path.join(os.getcwd(), "downloaded_file")
#        download_file(download_url, save_path)
#        print("File downloaded successfully:", save_path)

window.close()
