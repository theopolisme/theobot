#! /usr/bin/env python

from __future__ import unicode_literals
import sys
import time
import os
import cStringIO
import re

import mwclient
import requests

from PIL import Image
from PIL.ExifTags import TAGS

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

def get_exif_date(image):
	"""Given a filename, downloads the file, gets its
	EXIF creation date, and returns it.
	"""
	try:
		response = requests.get(image.imageinfo['url'])
	except AttributeError:
		return None # It wasn't even a file to begin with

	imageobj = cStringIO.StringIO(response.content)

	result = None
	try:
		i = Image.open(imageobj)
		info = i._getexif()
		for tag, value in info.items():
			if result == None:
				decoded = TAGS.get(tag, tag)
				if decoded == "DateTime":
					result = time.strptime(value, "%Y:%m:%d %H:%M:%S")
					result = time.strftime("%d %B %Y",result)
					break
	except:
		pass #This means that the image didn't have any EXIF data

	return result

def process_page(page):
	"""Given an image object, gets its uploader and
	its upload date, fills in {{Information}} for it,
	and saves the new page.
	"""
	print "processing {0}".format(page.page_title)
	revision =  page.revisions(dir='newer').next()

	user = revision['user']

	date = get_exif_date(page)
	if date == None:
		date = time.strftime("%d %B %Y",revision['timestamp'])

	contents = page.edit()

	if contents != "":
		description = re.sub(r"={1,5}[^=]*={1,5}","",contents,flags=re.U|re.DOTALL) # remove all headers
		description = re.sub(r"{{.*?}}","",description,flags=re.U|re.DOTALL) # remove all templates
		description = description.replace('\n',' ').strip()
	else:
		description = ""

	contents = u"""{{Information
| description = """+description+"""
| source      = {{own}}
| date        = """ + unicode(date) + """
| author      = {{subst:usernameexpand|""" + user.replace(" ","_") + """}}
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
