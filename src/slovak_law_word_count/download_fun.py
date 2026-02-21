"""Module for downloading documents from slov-lex.sk.

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

from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Set the maximum supported TLS version to TLS 1.2 # slov-lex.sk does not support TLS 1.3
# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

# Use the custom SSL context when making requests
requests.adapters.DEFAULT_RETRIES = 5
session = requests.Session()
session.mount(
    "https://",
    requests.adapters.HTTPAdapter(max_retries=requests.adapters.Retry(total=5)),
)
session.verify = True  # Set False for debugging
session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.slov-lex.sk",
        "Referer": "https://www.slov-lex.sk/",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    },
)

MIN_ROW_COLUMNS_FOR_LINK = 2
LINK_COLUMN_INDEX = 1


def _get_headers(accept: str) -> dict:
    """Headers matching a regular browser request to slov-lex.sk static API."""
    return {
        "Accept": accept,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
    }


def download_links_from_table(url, save_path) -> None:
    """Downloads links from the specified table on slov-lex.sk.

    Args:
        url (str): The URL of the document page on slov-lex.sk.
        save_path (str): The local directory where downloaded files will be saved.

    """
    url = url.strip()

    try:
        response = session.get(
            url,
            headers=_get_headers("application/json, text/plain, */*"),
            timeout=10,
        )
        response.raise_for_status()
    except requests.exceptions.SSLError as ssl_error:
        print(f"SSL Error: {ssl_error}")
        return
    except requests.exceptions.RequestException as error_name:
        print(f"Error occurred while fetching the page: {error_name!s}")
        return

    content_type = response.headers.get("Content-Type", "").lower()
    if "html" not in content_type:
        save_response_content(url, response, save_path)
        return

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", id="HistoriaTable")
    if table is None:
        print('Table with id "HistoriaTable" not found.')
        return

    process_table(table, url, save_path)


def process_table(table, base_url, save_path) -> None:
    """Processes rows of the table to download files.

    Args:
        table (bs4.element.Tag): The BeautifulSoup Tag representing the table.
        base_url (str): The base URL of the document page.
        save_path (str): The local directory where downloaded files will be saved.

    """
    table_rows = table.find_all("tr")
    # Extract links from the second column of the table
    for row in table_rows:
        process_table_row(row, base_url, save_path)


def process_table_row(row, base_url, save_path) -> None:
    """Processes a single row of the table to download a file.

    Args:
        row (bs4.element.Tag): The BeautifulSoup Tag representing a table row.
        base_url (str): The base URL of the document page.
        save_path (str): The local directory where downloaded files will be saved.

    """
    columns = row.find_all("td")
    if len(columns) >= MIN_ROW_COLUMNS_FOR_LINK:
        link_column = columns[LINK_COLUMN_INDEX]
        link = link_column.find("a")
        if link:
            download_url = get_download_url(link.get("href"), base_url)
            if download_url:
                download_file(download_url, save_path)


def get_download_url(href, base_url):
    """Gets the download URL based on the href.

    Args:
        href (str): The href attribute of the link.
        base_url (str): The base URL of the document page.

    Returns:
        str: The complete download URL.

    """
    if href:
        try:
            if href.startswith("http"):
                return href
            if href.startswith("/"):
                return urljoin(base_url, href[1:])
            return urljoin(base_url, href)
        except requests.exceptions.InvalidURL:
            print(f"Invalid URL: {href}")
    return None


def download_file(download_url, save_path) -> None:
    """Downloads the file from the given URL.

    Args:
        download_url (str): The URL of the file to be downloaded.
        save_path (str): The local directory where downloaded files will be saved.

    """
    try:
        response = session.get(
            download_url,
            headers=_get_headers("application/json, text/plain, */*"),
            timeout=10,
        )
        response.raise_for_status()
    except requests.exceptions.SSLError as ssl_error:
        print(f"SSL Error: {ssl_error}")
        return
    except requests.exceptions.RequestException as error_name:
        print(f"Error occurred while downloading: {error_name!s}")
        return

    filename = urlparse(download_url).path.split("/")[-1]
    save_dir = Path(save_path)
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / filename
    print(file_path)
    with file_path.open("wb") as file:
        file.write(response.content)
    print(f"Downloaded: {download_url}")


def save_response_content(url, response, save_path) -> None:
    """Persist already-downloaded response bytes to disk."""
    filename = urlparse(url).path.split("/")[-1]
    save_dir = Path(save_path)
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / filename
    with file_path.open("wb") as file:
        file.write(response.content)
    print(file_path)
    print(f"Downloaded: {url}")
