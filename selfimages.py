#! /usr/bin/env python

from __future__ import unicode_literals
import sys
import time

import mwclient

from theobot import password
from theobot import bot

# CC-BY-SA Theopolisme

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)

	global donenow
	donenow = 0

	category = mwclient.listing.Category(site, 'Category:Self-published work')
	for page in category:
		if page.namespace == 6 and "description" not in site.expandtemplates(text=page.edit()).lower():
			process_page(page)
		else:
			print "skipping {0}".format(page.page_title)

def process_page(page):
	"""Given an image object, gets its uploader and
	its upload date, fills in {{Information}} for it,
	and saves the new page.
	"""
	print "processing {0}".format(page.page_title)
	revision =  page.revisions(dir='newer').next()
	user = revision['user']
	date = time.strftime("%d %B %Y",revision['timestamp'])

	contents = page.edit()
	contents = u"""{{Information
| description = 
| source      = {{own}}
| date        = """ + date + """
| author      = {{subst:usernameexpand|""" + user + """}}
}}\n""" + contents

	global donenow
	if bot.donenow("User:Theo's Little Bot/disable/selfimages",donenow=donenow,donenow_div=5,shutdown=50) == True:
		page.save(contents,"[[WP:BOT|Bot]]: Automatically adding {{[[Template:Information|Information]]}} to self-published work) ([[User:Theo's Little Bot/disable/selfimages|disable]]")
		print "saved {0}".format(page.page_title)
		donenow += 1
	else:
		sys.exit()

if __name__ == '__main__':
	main()
