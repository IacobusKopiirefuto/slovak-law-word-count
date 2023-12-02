"""
Example of using q_analysis for analyzing documents
"""


from download_fun import download_links_from_table
from quick_analysis import q_analysis
from stop_words_default import default_stop_words

download_links_from_table('https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/1992/460/20230701', '../Constitution')
q_analysis("./Constitution", default_stop_words, 'o Ústave SR')
