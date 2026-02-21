import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from slovak_law_word_count.download_fun import download_links_from_table
from slovak_law_word_count.quick_analysis import q_analysis
from slovak_law_word_count.stanza_analysis import s_analysis
from slovak_law_word_count.stop_words_default import default_stop_words


def main():
    # download_links_from_table('https://static.slov-lex.sk/static/SK/ZZ/1992/460/20251101.portal?version=1771451781064', './downloads')
    # q_analysis("./downloads", default_stop_words, 'o Ústave SR')
    s_analysis("./downloads", default_stop_words, 'o Ústave SR')


if __name__ == "__main__":
    main()
