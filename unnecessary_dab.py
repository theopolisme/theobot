#!/usr/bin/env python
# -*- coding: utf-8  -*-
from __future__ import unicode_literals

import re
import mwclient
from theobot import password

"""
USAGE INSTRUCTIONS
* Download enwiki-latest-all-titles-in-ns0.gz from http://dumps.wikimedia.org/enwiki/latest/
* Save download contents as text file (one page title per line): "enwiki_titles.txt" in working directory
* Run `python unnecessary_dab.py`
* Magic!
"""

site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)
RESULTPAGE = site.Pages["User:Theo's Little Bot/unnecessary_dab"]

PARENS = []
ALL_PAGES = {}

with open("enwiki_titles.txt", "r") as r:
	for line in r:
		page = line.decode("utf-8").strip()
		if page.find('(') != -1 and page.find(')') != -1:
			PARENS.append(page)
		ALL_PAGES[page] = True

RESULTS = [] # Final list of results

for article in PARENS:
	proposed = re.sub(r'[_\s]*\(.*?\)\Z','',article,flags=re.U)
	if len(proposed) > 0 and proposed not in ALL_PAGES and site.Pages[article.replace('_',' ')].redirect == False: # len() is in case the title is enclosed solely by paretheses
		print article,proposed
		RESULTS.append('[[' + article.replace('_',' ') + ']] ➞ [[' + proposed.replace('_',' ') + ']]')

print len(RESULTS)

def split_by(sequence, length):
	iterable = iter(sequence)
	def yield_length():
		for i in xrange(length):
			 yield iterable.next()
	while True:
		res = list(yield_length())
		if not res:
			raise StopIteration
		yield res

for sublist in split_by(RESULTS,1000):
	output =  '# ' + '\n# '.join(sublist)
	RESULTPAGE.save(RESULTPAGE.edit()+'\n'+output,summary='Adding to "unnecessary_dab" list')

