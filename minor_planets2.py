#! /usr/bin/env python

from __future__ import unicode_literals

import mwclient
import mwparserfromhell

from theobot import password
from theobot import bot

import re

# CC-BY-SA Theopolisme

def checktext(page):
	"""Given a string of wikicode, checks if it
	- has only one body sentence
	- has no references
	"""
	text = page.edit()
	wikicode = mwparserfromhell.parse(text)
	sections = wikicode.get_sections(include_lead=False,include_headings=True)
	for section in sections:
		header = section.get(0)
		title = header.title.lower()
		if "external links" in title:
			section.remove(header)
			contents = re.sub(r"\*\s?{{jpl small body[\s\S]*?}}","",section.lower(),flags=re.UNICODE)
			contents = re.sub(r"\[\[category.*?\]\]","",contents,flags=re.U)
			contents = mwparserfromhell.parse(contents).strip_code()
			if len(contents.strip()) == 0:
				return True
	if text.find("Citation from the [[Minor Planet Circular|MPCs]]") != -1 and text.find("''No citation yet''") != -1:
		return True
	return False

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)

	original = site.Pages["User:Theo's Little Bot/Minor planets"]
	text = original.edit()
	articles = re.findall(r"\[\[(.*?)\]\]",text,flags=re.U)
	results = []
	for article in articles:
		page = site.Pages[article]
		if checktext(page) == True:
			results.append(page.name)

	output = "== Articles with only [[Template:JPL small body|]] in their external links or only an empty citation list ==\n<sup>Updated ~~~~~ by [[User:Theo's Little Bot|]]</sup>"

	results = sorted(set(results))
	for result in results:
		output += "\n# [[{}]]".format(result)

	page = site.Pages["User:Theo's Little Bot/Minor planets2"]
	page.save(output,summary="[[WP:BOT|Bot]]: Updating minor planets report")

if __name__ == '__main__':
	main()
