# -*- coding: utf-8 -*-

import re
import mwclient
import password
from bs4 import BeautifulSoup

""" Regex-based typo hunting, using the AWB dataset """

site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

typopage = site.Pages['Wikipedia:AutoWikiBrowser/Typos']
text = typopage.edit()
soup = BeautifulSoup(text)

PATTERNS = []
typos = soup.find_all('typo')
count = len(typos)
errs = 0
for tag in typos:
	try:
		PATTERNS.append([tag['word'],re.compile(tag['find'],flags=re.U),re.sub(r"\$(\d*)",r"\\\1",tag['replace'],flags=re.U),re.sub(r"\((?!\?)","(|",tag['find'])])
		#print PATTERNS
	except:
		errs += 1

print "Typo dataset loaded.\nWe were able to utilize {}% of the dataset.".format((float(count-errs)/count)*100)

def typos(string):
	"""Returns a list of typos and their line numbers, in the form of
	{line:[currentspelling,currentspelling]}
	{3:[['aplhabet','flooors']]} 
	"""
	lines = string.splitlines()
	results = {}
	for i,line in enumerate(lines):
		matches = []
		for tuple in PATTERNS:
			match = re.search(tuple[1],line)
			if match:
				matches.append([match.group(),re.sub(tuple[3],tuple[2],unicode(match.group()))])
		if len(matches) > 0:
			results[i] = matches
	return results
