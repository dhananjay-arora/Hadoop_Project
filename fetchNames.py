#!/usr/bin/python

import sys

# input comes from STDIN (standard input)
for line in sys.stdin:
  line = line.strip()
  word,fnames,synset = line.split("\t",2)
  for fname in fnames.split(','):
  	print(fname)

