#! /usr/bin/env python

from __future__ import unicode_literals
import sys

import mwclient
import mwparserfromhell

from theobot import password

# CC-BY-SA Theopolisme

ABOUT = """

IN PROGRESS

This script will add text at a given position in a page, based on the
position parameter, which should be a term cooresponding to an item
in the following list:

'external' == External links * 
'nav' == Navigation templates (footer navboxes)
'geo' == Geographical coordinates (if not in Infobox) or {{coord missing}} *
'authcontrol' == Authority control template *
'persondata' == Persondata template *
'defaultsort' == Defaultsort *
'category' == Categories
'stub' == Stub template *

* not yet implemented

== API usage ==

	import advanced_addtext
	advanced_addtext.add_text(text,page_contents,position)

`Text` should be the text that you would like added, and `page_contents` should
be a string/unicode object that represents the wikitext into which the text will
be inserted. Position should be a quoted term from the above list denoting the
position where you want the text inserted. `add_text()` will return a string/unicode
object of the new wikitext with the text inserted.

== Command line usage ==

This script can be run on the command line, in the following format:
	python advanced_addtext.py "text" page -position

For example,
	python advanced_addtext.py "Hello, World!" Wikipedia -nav
adds the text "Hello, World!" to the article Wikipedia, in the position
where navigation templates belong.

"""

class ParsedPage(object):
	"""This represents a page that is broken down to allow for easy
	access to a specific area in the page (ex. nav templates).
	"""

	def __init__(self,page_contents):
		self.wikicode = mwparserfromhell.parse(page_contents)
		self.parse()

	def parse(self):
		self.bottom = len(self.wikicode)
		self.CATEGORIES = []
		self.CAT_INDEX = None
		self._cats()

	def _cats(self):
		for node in self.wikicode.ifilter():
			if unicode(node.title).find("Category:") != -1:
				index = self.wikicode.index(node)
				self.CATEGORIES += node.title
				if index > self.CAT_INDEX:
					self.CAT_INDEX = index 
		if self.CAT_INDEX == None:
			self.CAT_INDEX = self.bottom # Hacky, just adds cats to the very bottom

	def insert(self,text,position):
		if position == 'category':
			self.wikicode.insert(self.CAT_INDEX+1,"\n"+text)
		else:
			raise NotImplementedError("""Sorry, but "{}" insertion isn't currently implemented.""".format(position))

		return self.wikicode		

def add_text(text,page_contents,position):
	parsed = ParsedPage(page_contents)
	result = parsed.insert(text,position)
	return result

def main():
	if len(sys.argv) == 4:
		inserttext = sys.argv[1]
		pagename = sys.argv[2]
		type_of_insert = sys.argv[3].strip('-')
	elif 4 > len(sys.argv) > 1:
		raise ValueError("""Exactly four inputs, please, like so:\n$ python advanced_addtext.py "text" page -position\n(Run with no args for detailed instructions)""")
	else:
		print ABOUT
		sys.exit()

	site = mwclient.Site('en.wikipedia.org')
	page = site.Pages[pagename]
	print add_text(inserttext,page.edit(),type_of_insert)

if __name__ == '__main__':
	main()
