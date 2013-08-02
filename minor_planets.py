#! /usr/bin/env python

from __future__ import unicode_literals

import mwclient
import mwparserfromhell

from theobot import password
from theobot import bot
import time

# CC-BY-SA Theopolisme

def checktext(page):
	"""Given a string of wikicode, checks if it
	- has only one body sentence
	- has no references
	"""
	text = page.edit()
	if text.find("<ref") != -1:
		return False
	wikicode = mwparserfromhell.parse(text)
	stripped = unicode(wikicode.strip_code())
	sentences = 0
	for line in stripped.splitlines():
		if len(line) > 25 and line.find("Category:") == -1 and line[0] != " ":
			sentences += line.count('.') + line.count('!') + line.count('?')
	if sentences <= 1:
		return True
	else:
		return False

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)

	category = mwclient.listing.Category(site, 'Category:Minor planets')
	results = []
	for page in bot.listpages(category,names=False,includeredirects=False):
		if page.namespace == 0:
			if checktext(page) == True:
				results.append(page.name)

	output = "== Minor planet articles with one sentence and no references ==\n<sup>Updated ~~~~~ by [[User:Theo's Little Bot|]]</sup>"

	results = sorted(set(results))
	for result in results:
		output += "\n# [[{}]]".format(result)

	page = site.Pages["User:Theo's Little Bot/Minor planets"]
	page.save(output,summary="[[WP:BOT|Bot]]: Updating minor planets report")

if __name__ == '__main__':
	main()
