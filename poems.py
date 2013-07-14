#! /usr/bin/env python
from __future__ import unicode_literals

import mwclient
import mwparserfromhell

import re

from theobot import bot
from theobot import password

from dateutil import parser

from datetime import datetime

# CC-BY-SA Theopolisme
DEFAULT = datetime(3000, 01, 01)

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)

	for page in bot.what_transcludes('infobox poem'):
		page = site.Pages[page['title']]
		contents = page.edit()
		wikicode = mwparserfromhell.parse(contents)
		for template in wikicode.filter_templates():
			if "infobox poem" in template.name.lower() and template.has_param('publication_date'):
				pub_date_raw = unicode(template.get('publication_date').value).strip()
				print pub_date_raw
				if pub_date_raw.lower().find("{{start") == -1:
					try:
						date = parser.parse(pub_date_raw,fuzzy=True,default=DEFAULT)
					except ValueError:
						print "Date was unparsable."
						if pub_date_raw.find("<!-- Date published") == -1:
							template.add('publication_date',pub_date_raw+" [[Category:Poem publication dates needing manual review]]")
							#page.save(unicode(wikicode),'[[WP:BOT|Bot]]: Tagging unparsable publication_date')
							print "[[WP:BOT|Bot]]: Tagging unparsable publication_date"
							continue
						else:
							print "No publication date specificed; skipping."
							continue
					# !todo convert this date object to {{start date}}
				else:
					print "Template already updated."
					continue

if __name__ == '__main__':
	main()
