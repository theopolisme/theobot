#! /usr/bin/env python

from __future__ import unicode_literals
import sys
import re

import mwclient
import mwparserfromhell

from theobot import password
from theobot import bot

# CC-BY-SA Theopolisme

"""

IN PROGRESS

This script will add text at a given position in a page, based on the
position parameter, which should be a number cooresponding to an item
in the following list:

1) External links * 
2) Navigation templates (footer navboxes)
3) Geographical coordinates (if not in Infobox) or {{coord missing}} *
4) Authority control template *
5) Persondata template *
6) Defaultsort *
7) Categories
8) Stub template *
9) Very bottom

* not yet implemented

== API usage ==

	import advanced_addtext
	advanced_addtext.add_text(text,page_contents,position)

`Text` should be the text that you would like added, and `page_contents` should
be a string/unicode object that represents the wikitext into which the text will
be inserted. Position should be an integer from the above list denoting the
position where you want the text inserted. `add_text()` will return a string/unicode
object of the new wikitext with the text inserted.

== Command line usage ==

This script can be run on the command line, in the following format:
	python advanced_addtext.py "text" page -position

For example,
	python advanced_addtext.py "Hello, World!" Wikipedia -2
adds the text "Hello, World!" to the article Wikipedia, in the position
where navigation templates belong.

"""

class ParsedPage(object):
	"""This represents a page that is broken down to allow for easy
	access to a specific area in the page (ex. nav templates).
	"""

	def add_


def add_text(text,page_contents,position):

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.main_username, password.main_password)

if __name__ == '__main__':
	main()
