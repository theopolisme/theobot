#! /usr/bin/env python
from __future__ import unicode_literals

import mwclient
import mwparserfromhell

import re

from theobot import bot
from theobot import password

from datetime import datetime

import dateutil.parser as parser

# CC-BY-SA Theopolisme

# Rather hackety, but it works
def parse(self,timestr,default=None,ignoretz=False,tzinfos=None,**kwargs):
	return self._parse(timestr, **kwargs)
parser.parser.parse = parse

def process(page):
	contents = page.edit()
	wikicode = mwparserfromhell.parse(contents)
	for template in wikicode.filter_templates():
		if "infobox poem" in template.name.lower() and template.has_param('publication_date'):
			pub_date_raw = unicode(template.get('publication_date').value).strip()#.replace('[[','').replace(']]','')
			print "-----"
			print "Raw publication_date: "+pub_date_raw
			if pub_date_raw.lower().find("{{start") == -1:
				date = parser.parser().parse(pub_date_raw,None)
				if date is None or date.year is None:
					if pub_date_raw.find("<!-- Date published") == -1:
						template.add('publication_date',pub_date_raw+" [[Category:Infoboxes needing manual conversion to use start date]]")
						#page.save(unicode(wikicode),'[[WP:BOT|Bot]]: Tagging unparsable publication_date')
						print "Tagging unparsable publication_date"
						continue
					else:
						print "No publication date specificed; skipping."
						continue					
				if re.search(r"""\d{1,2} [a-zA-Z]* \d{4}""",pub_date_raw,flags=re.U) is not None:
					df = True
				else:
					df = False
				startdate = mwparserfromhell.nodes.Template(name='start date')
				if date.year:
					startdate.add(1,date.year)
				if date.month:
					startdate.add(2,date.month)
				if date.day:
					startdate.add(3,date.day)
				if df:
					startdate.add('df','y')
				print "Final template: "+unicode(startdate)
				template.add('publication_date',unicode(startdate)+"<!-- Bot-converted date -->")
				#page.save(unicode(wikicode),'[[WP:BOT|Bot]]: Converting publication_date to utilize {{[[Template:start date|]]}}')
			else:
				print "Template already updated."
				continue

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)

	for page in bot.what_transcludes('infobox poem'):
		page = site.Pages[page['title']]
		process(page)

if __name__ == '__main__':
	main()
