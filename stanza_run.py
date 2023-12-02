"""
Example of using s_analysis for analyzing documents
"""

from download_fun import download_links_from_table
from stanza_analysis import s_analysis
from stop_words_default import default_stop_words

download_links_from_table('https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/1992/460/20230701', './Constitution')
s_analysis("./Constitution", default_stop_words, 'o Ústave SR')
