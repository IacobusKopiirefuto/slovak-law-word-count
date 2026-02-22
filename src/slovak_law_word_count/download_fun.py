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

import logging
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from .normalize import SlovLexStaticUrlBuilder

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
MIN_STANDARD_PATH_PARTS = 4
STANDARD_PATH_WITH_DATE_PARTS = 5
STANDARD_DATE_INDEX = 4
DATE_LENGTH = 8
STANDARD_URL_PREFIX = "/ezbierky/pravne-predpisy/"
STATIC_URL_PREFIX = "/static/"
PathLike = str | Path
logger = logging.getLogger(__name__)
static_url_builder = SlovLexStaticUrlBuilder()


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


def _remove_query_and_fragment(url: str) -> str:
    """Return URL without query string and fragment."""
    parsed = urlparse(url)
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            "",
            "",
            "",
        ),
    )


def _normalize_static_url(url: str) -> str:
    """Normalize static.slov-lex URL and remove the optional version query."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    tail = path[len(STATIC_URL_PREFIX) :].strip("/")
    path_parts = tail.split("/")
    if len(path_parts) >= STANDARD_PATH_WITH_DATE_PARTS:
        date_part = path_parts[STANDARD_DATE_INDEX]
        date_part = date_part.removesuffix(static_url_builder.end)
        try:
            return static_url_builder.build(
                country=path_parts[0],
                collection=path_parts[1],
                year=path_parts[2],
                law_number=path_parts[3],
                date=date_part,
            )
        except ValueError:
            logger.warning("Invalid static URL components: %s", url)
    return urlunparse(("https", "static.slov-lex.sk", path, "", "", ""))


def _resolve_standard_url_to_static(url: str) -> str | None:
    """Follow redirects to obtain static URL for standard links without date."""
    try:
        response = session.get(url, allow_redirects=True, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        logger.exception("Failed to resolve standard URL to static URL")
        return None

    resolved_url = _remove_query_and_fragment(response.url)
    parsed_resolved = urlparse(resolved_url)
    if (
        parsed_resolved.netloc == "static.slov-lex.sk"
        and parsed_resolved.path.startswith(STATIC_URL_PREFIX)
    ):
        return _normalize_static_url(resolved_url)
    return None


# TODO: simplify ulr normalization process,
#   this works but the code is not as readable as it could
def normalize_slov_lex_url(url: str) -> str:
    """Normalize slov-lex document URLs to static portal format when possible."""
    normalized_input = url.strip()
    parsed = urlparse(normalized_input)
    host = parsed.netloc.lower()
    path = parsed.path.rstrip("/")

    if host == "static.slov-lex.sk" and path.startswith(STATIC_URL_PREFIX):
        return _normalize_static_url(normalized_input)

    if host != "www.slov-lex.sk" or not path.startswith(STANDARD_URL_PREFIX):
        return _remove_query_and_fragment(normalized_input)

    tail = path[len(STANDARD_URL_PREFIX) :].strip("/")
    path_parts = tail.split("/")
    if len(path_parts) < MIN_STANDARD_PATH_PARTS:
        return _remove_query_and_fragment(normalized_input)

    # Standard URLs with explicit date can be rewritten locally.
    if (
        len(path_parts) >= STANDARD_PATH_WITH_DATE_PARTS
        and path_parts[STANDARD_DATE_INDEX].isdigit()
        and len(path_parts[STANDARD_DATE_INDEX]) == DATE_LENGTH
    ):
        try:
            return static_url_builder.build(
                country=path_parts[0],
                collection=path_parts[1],
                year=path_parts[2],
                law_number=path_parts[3],
                date=path_parts[STANDARD_DATE_INDEX],
            )
        except ValueError:
            logger.warning("Invalid standard URL components: %s", normalized_input)
            return _remove_query_and_fragment(normalized_input)

    # For legacy URLs without date, resolve the redirect once.
    resolved = _resolve_standard_url_to_static(normalized_input)
    if resolved:
        return resolved

    return _remove_query_and_fragment(normalized_input)


def download_links_from_table(url: str, save_path: PathLike) -> None:
    """Download links from the specified table on slov-lex.sk.

    Args:
        url (str): The URL of the document page on slov-lex.sk.
        save_path (str): The local directory where downloaded files will be saved.

    """
    url = normalize_slov_lex_url(url)

    try:
        response = session.get(
            url,
            headers=_get_headers("application/json, text/plain, */*"),
            timeout=10,
        )
        response.raise_for_status()
    except requests.exceptions.SSLError:
        logger.exception("SSL Error")
        return
    except requests.exceptions.RequestException:
        logger.exception("Error occurred while fetching the page")
        return

    content_type = response.headers.get("Content-Type", "").lower()
    if "html" not in content_type:
        save_response_content(url, response, save_path)
        return

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", id="HistoriaTable")
    if table is None:
        logger.warning('Table with id "HistoriaTable" not found.')
        return

    process_table(table, url, save_path)


def process_table(table: Tag, base_url: str, save_path: PathLike) -> None:
    """Process rows of the table to download files.

    Args:
        table (bs4.element.Tag): The BeautifulSoup Tag representing the table.
        base_url (str): The base URL of the document page.
        save_path (str): The local directory where downloaded files will be saved.

    """
    table_rows = table.find_all("tr")
    # Extract links from the second column of the table
    for row in table_rows:
        process_table_row(row, base_url, save_path)


def process_table_row(row: Tag, base_url: str, save_path: PathLike) -> None:
    """Process a single row of the table to download a file.

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


def get_download_url(href: str | None, base_url: str) -> str | None:
    """Get the download URL based on the href.

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
            logger.exception("Invalid URL: %s", href)
    return None


def download_file(download_url: str, save_path: PathLike) -> None:
    """Download the file from the given URL.

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
    except requests.exceptions.SSLError:
        logger.exception("SSL Error")
        return
    except requests.exceptions.RequestException:
        logger.exception("Error occurred while downloading")
        return

    filename = urlparse(download_url).path.split("/")[-1]
    save_dir = Path(save_path)
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / filename
    logger.info("%s", file_path)
    with file_path.open("wb") as file:
        file.write(response.content)
    logger.info("Downloaded: %s", download_url)


def save_response_content(
    url: str,
    response: requests.Response,
    save_path: PathLike,
) -> None:
    """Persist already-downloaded response bytes to disk."""
    filename = urlparse(url).path.split("/")[-1]
    save_dir = Path(save_path)
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / filename
    with file_path.open("wb") as file:
        file.write(response.content)
    logger.info("%s", file_path)
    logger.info("Downloaded: %s", url)
