"""
Module for downloading documents from slov-lex.sk.

This module provides functions to download various versions of documents in HTML
format from the slov-lex.sk website.

Functions:
    - `download_links_from_table(url, save_path)`:
        Downloads links from the specified table on slov-lex.sk.

    - `process_table(table, base_url, save_path)`:
        Processes rows of the table to download files.

    - `process_table_row(row, base_url, save_path)`:
        Processes a single row of the table to download a file.

    - `get_download_url(href, base_url)`:
        Gets the download URL based on the href.

    - `download_file(download_url, save_path)`:
        Downloads the file from the given URL.

Usage:
    1. Import the module: `import download_fun`
    2. Specify the URL of the document and the local path to save downloaded files.
    3. Use the functions to download links from the specified table in the document's page.
"""

# Copyright 2023 Jakub Škoda
# SPDX-License-Identifier: AGPL-3.0-only

import os
from urllib.parse import urljoin, urlparse
import requests
import ssl
from bs4 import BeautifulSoup

# Set the maximum supported TLS version to TLS 1.2 # slov-lex.sk does not support TLS 1.3
# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

# Use the custom SSL context when making requests
requests.adapters.DEFAULT_RETRIES = 5
session = requests.Session()
session.mount("https://", requests.adapters.HTTPAdapter(max_retries=requests.adapters.Retry(total=5)))
session.verify = True  # Set False for debugging
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})

def download_links_from_table(url, save_path):
    """
    Downloads links from the specified table on slov-lex.sk.

    Args:
        url (str): The URL of the document page on slov-lex.sk.
        save_path (str): The local directory where downloaded files will be saved.
    """
    url = url.strip()

    try:
        response = requests.get(url, timeout=10)
#        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
    except requests.exceptions.SSLError as ssl_error:
        print(f"SSL Error: {ssl_error}")
        return
    except requests.exceptions.RequestException as error_name:
        print(f"Error occurred while fetching the page: {str(error_name)}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', id='HistoriaTable')
    if table is None:
        print('Table with id "HistoriaTable" not found.')
        return

    process_table(table, url, save_path)

def process_table(table, base_url, save_path):
    """
    Processes rows of the table to download files.

    Args:
        table (bs4.element.Tag): The BeautifulSoup Tag representing the table.
        base_url (str): The base URL of the document page.
        save_path (str): The local directory where downloaded files will be saved.
    """
    table_rows = table.find_all('tr')
    # Extract links from the second column of the table
    for row in table_rows:
        process_table_row(row, base_url, save_path)

def process_table_row(row, base_url, save_path):
    """
    Processes a single row of the table to download a file.

    Args:
        row (bs4.element.Tag): The BeautifulSoup Tag representing a table row.
        base_url (str): The base URL of the document page.
        save_path (str): The local directory where downloaded files will be saved.
    """
    columns = row.find_all('td')
    if len(columns) >= 2:
        link_column = columns[1]
        link = link_column.find('a')
        if link:
            download_url = get_download_url(link.get('href'), base_url)
            if download_url:
                download_file(download_url, save_path)

def get_download_url(href, base_url):
    """
    Gets the download URL based on the href.

    Args:
        href (str): The href attribute of the link.
        base_url (str): The base URL of the document page.

    Returns:
        str: The complete download URL.
    """
    if href:
        try:
            if href.startswith('http'):
                return href
            if href.startswith('/'):
                return urljoin(base_url, href[1:])
            return urljoin(base_url, href)
        except requests.exceptions.InvalidURL:
            print(f"Invalid URL: {href}")
    return None

def download_file(download_url, save_path):
    """
    Downloads the file from the given URL.

    Args:
        download_url (str): The URL of the file to be downloaded.
        save_path (str): The local directory where downloaded files will be saved.
    """
    try:
        response = requests.get(download_url, timeout=10)
#        response = requests.get(download_url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
    except requests.exceptions.SSLError as ssl_error:
        print(f"SSL Error: {ssl_error}")
        return
    except requests.exceptions.RequestException as error_name:
        print(f"Error occurred while downloading: {str(error_name)}")
        return

    filename = urlparse(download_url).path.split('/')[-1]
    file_path = os.path.join(save_path, filename)
    print(file_path)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded: {download_url}")
