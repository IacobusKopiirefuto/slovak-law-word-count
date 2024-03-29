# slovak-law-word-count

This project aims to offer linguistic analysis of legal acts of the Slovak Republic and other documents available on [Slov-Lex](https://www.slov-lex.sk/web/en).

It was created as part of a report Analysis of law volume - revealing dormant potential (Analýza objemu zákonov - odhalenie spiaceho potenciálu, [HTML](https://www.iness.sk/sk/analyza-objemu-zakonov-odhalenie-spiaceho-potencialu), [PDF](https://www.iness.sk/sites/default/files/pictures/analyza_objemu_zakonov-odhalenie_spiaceho_potencialu.pdf)) for The Institute of Economic and Social Studies (INESS). It was also shortly mentioned in the [short news](https://e.dennikn.sk/minuta/3778916) and [economic newsletter & podcast](https://e.dennikn.sk/3780222/ekonomicky-newsfilter-fico-sa-pred-svetovou-biznis-elitou-neblysol/) of DennikN.

So far it offers these metrics and outputs:

- word_count
- char_count
- word_count_stop
- sent_count
- avg_sent_length
- type_token_ratio
- FKGL
- GFI
- syllable_count
- complex_word_count
- tag_frequencies
- lemma_counts
- s_readability_word_count
- tag_word_count


# Running project

Simply download the script and run either quick analysis (almost instant results, low hardware requirements) or analysis using Stanza natural language analysis package (outputs more metrics but is also more resource heavy)

Example for analysing the Constitution of Slovak Republic:

- quick analysis:

```python
# from download_fun import download_links_from_table
from quick_analysis import q_analysis
from stop_words_default import default_stop_words

# download_links_from_table('https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/1992/460/20230701', '../Constitution')
q_analysis("./Constitution", default_stop_words, 'o Ústave SR')
```

- stanza analysis:

```python
# from download_fun import download_links_from_table
from stanza_analysis import s_analysis
from stop_words_default import default_stop_words

# download_links_from_table('https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/1992/460/20230701', './Constitution')
s_analysis("./Constitution", default_stop_words, 'o Ústave SR')
```

# To Do

- fix `download_fun.py`: function seems to work, but slov-lex.sk started to block it
    - currently gives error: `HTTPSConnectionPool(host='www.slov-lex.sk', port=443): Max retries exceeded with url: /pravne-predpisy/SK/ZZ/1992/460/20230701 (Caused by SSLError(SSLError(1, '[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure (_ssl.c:1006)')))`
    - but `curl https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/1992/460/20230701` as well as `download_links_from_table('https://example.org/', '../Constitution')` works
    - you can also download all legal texts (11 GB, zip archive) from [slov-lex.sk](https://www.slov-lex.sk/archiv-zbierky-zakonov)
- add additional metrics:
    - longest (shortest) sentences from `s_sentences()`
    - longest (shortest) words from `s_readability()`
    - page count (conversion from character count)
    - number of internal and external hyperlinks in text
    - number of paragraphs
    - number of footnotes
- generalize input
    - make it easy to take any plain text format as an input
    - try to add analysis for other contries <https://n-lex.europa.eu/n-lex/index?lang=en>
-    graph of interconnected legal texts (already available on Slov-Lex 'Zobraziť graf k predpisu' (top right corner, icon of a pie chart without text))
