"""Command-line interface for slovak-law-word-count."""

import argparse

from .download_fun import download_links_from_table
from .stop_words_default import default_stop_words


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="slovak-law-word-count",
        description="Download and analyze Slovak law documents.",
    )
    parser.add_argument(
        "folder",
        help="Folder with HTML files to analyze (or where downloads will be saved).",
    )
    parser.add_argument(
        "--download-url",
        help="Optional URL to download before analysis.",
    )
    parser.add_argument(
        "--mode",
        choices=("quick", "stanza"),
        default="quick",
        help="Analysis mode (default: quick).",
    )
    parser.add_argument(
        "--law-name",
        default="",
        help="Law name used in output plot titles.",
    )
    return parser


def main() -> None:
    """Parse CLI arguments and run the selected analysis mode."""
    args = build_parser().parse_args()

    if args.download_url:
        download_links_from_table(args.download_url, args.folder)

    if args.mode == "stanza":
        from .stanza_analysis import s_analysis  # noqa: PLC0415

        s_analysis(args.folder, default_stop_words, args.law_name)
    else:
        from .quick_analysis import q_analysis  # noqa: PLC0415

        q_analysis(args.folder, default_stop_words, args.law_name)


if __name__ == "__main__":
    main()
