"""Run the default stanza analysis example."""

from slovak_law_word_count.stanza_analysis import s_analysis
from slovak_law_word_count.logging_config import setup_logging
from slovak_law_word_count.stop_words_default import default_stop_words


def main() -> None:
    """Execute the default local stanza analysis workflow."""
    setup_logging()
    # download_links_from_table('https://static.slov-lex.sk/static/SK/ZZ/1992/460/20251101.portal?version=1771451781064', './downloads')
    # q_analysis("./downloads", default_stop_words, 'o Ústave SR')
    s_analysis("./downloads", default_stop_words, "o Ústave SR")


if __name__ == "__main__":
    main()
