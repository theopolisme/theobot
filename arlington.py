#! /usr/bin/env python

from __future__ import unicode_literals
import re

import mwclient

from theobot import password
from theobot import bot

# CC-BY-SA Theopolisme

"""
* REQUIRES MANUAL INTERVENTION BEFORE SAVING EACH PAGE *
Create redirects to PAGENAMES in the format "X, Virginia" and "X, Arlington, Virginia" and "X".
"""

R_FORMAT = "#REDIRECT [[%s]] {{R from alternative name}}"

PAGENAMES = [u'Arlington Forest Historic District', u'Arlington Heights Historic District', u'Arlington Ridge, Virginia',
u'Arlington Village Historic District (Arlington, Virginia)', u'Ashton Heights Historic District', u'Aurora Highlands Historic District',
u'Ballston, Arlington, Virginia', u'Cherrydale, Arlington, Virginia', u'Cherrydale Historic District', u'Clarendon, Arlington, Virginia',
u'Colonial Village (Arlington, Virginia)', u'Columbia Forest Historic District', u'Court House, Arlington, Virginia',
u'Crystal City, Arlington, Virginia', u'Fairlington, Arlington, Virginia', u'Glebewood Village Historic District', u'Glencarlyn, Virginia',
u'Glencarlyn Historic District', u'Highland Park-Overlee Knolls', u'Lee Gardens North Historic District', u'Lyon Park Historic District',
u'Lyon Village, Arlington, Virginia', u'Maywood Historic District', u'Monroe Courts Historic District', u'North Arlington, Virginia',
u'Penrose Historic District', u'Pentagon City', u'Rosslyn, Arlington, Virginia', u'Shirlington, Arlington, Virginia',
u'South Arlington, Virginia', u'Virginia Heights Historic District', u'Virginia Square, Arlington, Virginia', u'Westover, Arlington, Virginia']

REDIRECT_FMTS = ["{}, Virginia","{}, Arlington, Virginia","{}"]

def parse_for_raw_name(page_title):
	page_title = re.sub(r"""\s*\((.*?)\)""","",page_title,flags=re.U)

	if page_title.find("Historic District") != 1:
		page_title = page_title.split(" Historic District")[0]

	split_title = page_title.split(',')
	raw_name = split_title[0]

	return raw_name.strip()

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.main_username, password.main_password)

	pages = [site.Pages[page] for page in PAGENAMES]

	for page in pages:
		target = page.page_title
		raw_title = parse_for_raw_name(target)
		for redirect_fmt in REDIRECT_FMTS:
			title = redirect_fmt.format(raw_title)
			if title != target:
				new_page = site.Pages[title]
				if new_page.exists == False:
					if raw_input("Save redirect from {} to {}? [press enter]".format(title,target)) == "":
						#new_page.save(R_FORMAT % target,"Redirected page to [[{}]]".format(target))
						new_page.save(R_FORMAT % target)
					else:
						print "Not saved."
				else:
					print "Skipping redirect from {} to {} since the page already exists.".format(title,target)

if __name__ == '__main__':
	main()
