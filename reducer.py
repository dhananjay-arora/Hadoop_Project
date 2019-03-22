#!/usr/bin/env python
"""reducer.py"""

from operator import itemgetter
import sys
current_synonyms = set()
current_word = None
word = None

# input comes from STDIN
for line in sys.stdin:
    # remove leading and trailing whitespace
    line = line.strip()

    # parse the input we got from mapper.py
    try:
        word,synonyms_list = line.split('\t',1)
        synonyms = set(synonyms_list.split(","))
    except:
        # count was not a number, so silently
        # ignore/discard this line
        continue
    if current_word == word:
        # if full_word[:5] == word:
        current_synonyms = current_synonyms.union(synonyms)
        # current_count += count
    else:
        if current_word:
            # write result to STDOUT
            # if full_word[:5] == word:
            print '%s\t%s' % (current_word, ",".join(current_synonyms))
        current_synonyms = synonyms
        current_word = word

# do not forget to output the last word if needed!
if current_word == word:
    # if word == full_word[:5]:
    print '%s\t%s' % (current_word, ",".join(current_synonyms))