"""Utilities for building and validating slov-lex static URLs."""

from dataclasses import dataclass
from urllib.parse import urlunparse

DATE_LENGTH = 8
YEAR_LENGTH = 4


@dataclass(frozen=True)
class SlovLexStaticUrlBuilder:
    """Build static slov-lex URLs with fixed host, path prefix, and suffix."""

    host: str = "static.slov-lex.sk"
    path_start: str = "/static"
    end: str = ".portal"
    scheme: str = "https"

    def _validate_country(self, country: str) -> None:
        if not country.isalpha() or not country.isupper():
            msg = "country must contain uppercase letters only (example: SK)"
            raise ValueError(msg)

    def _validate_collection(self, collection: str) -> None:
        if not collection.isalpha() or not collection.isupper():
            msg = "collection must contain uppercase letters only (example: ZZ)"
            raise ValueError(msg)

    def _validate_year(self, year: str) -> None:
        if not (year.isdigit() and len(year) == YEAR_LENGTH):
            msg = "year must be exactly 4 digits"
            raise ValueError(msg)

    def _validate_law_number(self, law_number: str) -> None:
        if not law_number.isdigit():
            msg = "law_number must contain digits only"
            raise ValueError(msg)

    def _validate_date(self, date: str) -> None:
        if not (date.isdigit() and len(date) == DATE_LENGTH):
            msg = "date must be exactly 8 digits in YYYYMMDD format"
            raise ValueError(msg)

    def _validate_version(self, version: str | None) -> None:
        if version is not None and not version.isdigit():
            msg = "version must contain digits only"
            raise ValueError(msg)

    def build(
        self,
        country: str,
        collection: str,
        year: str,
        law_number: str,
        date: str,
        version: str | None = None,
    ) -> str:
        """Build a canonical static URL for slov-lex law snapshots."""
        self._validate_country(country)
        self._validate_collection(collection)
        self._validate_year(year)
        self._validate_law_number(law_number)
        self._validate_date(date)
        self._validate_version(version)

        path = (
            f"{self.path_start.rstrip('/')}/{country}/{collection}/"
            f"{year}/{law_number}/{date}{self.end}"
        )
        query = f"version={version}" if version else ""
        return urlunparse((self.scheme, self.host, path, "", query, ""))
