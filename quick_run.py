"""Example of using q_analysis for analyzing documents."""

from slovak_law_word_count.download_fun import download_links_from_table
from slovak_law_word_count.quick_analysis import q_analysis
from slovak_law_word_count.stop_words_default import default_stop_words


def main() -> None:
    download_links_from_table(
        "https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/1992/460/20230701",
        "../Constitution",
    )
    q_analysis("./Constitution", default_stop_words, "o Ústave SR")


if __name__ == "__main__":
    main()
