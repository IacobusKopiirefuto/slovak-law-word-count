"""Example of using q_analysis for analyzing documents."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


from slovak_law_word_count.download_fun import download_links_from_table
from slovak_law_word_count.quick_analysis import q_analysis
from slovak_law_word_count.stop_words_default import default_stop_words

download_links_from_table(
    "https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/1992/460/20230701",
    "../Constitution",
)
q_analysis("./Constitution", default_stop_words, "o Ústave SR")
