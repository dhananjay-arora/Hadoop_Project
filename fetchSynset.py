#!/usr/bin/python

import sys
synstring = []
# input comes from STDIN (standard input)
for line in sys.stdin:
  line = line.strip()
  word,fnames,synset = line.split("\t",2)
  # for fname in fnames:
  synstring.append(synset)

print(','.join(synstring))