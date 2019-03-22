#!/usr/bin/env python
"""mapper2.py"""

import sys

# input comes from STDIN (standard input)
for line in sys.stdin:
    # remove leading and trailing whitespace
  line = line.strip()
  word,synonyms_list = line.split("\t",1)

  synonyms = synonyms_list.split(",")
  synset = set()
  for synonym in synonyms :
    words = synonym.split(' ')
    for word_dict in words :
      if word in word_dict :
        synset.add(word_dict)
  if (len(synonyms) > 4):
    print '%s\t%s' % (line,"=".join(synset))
