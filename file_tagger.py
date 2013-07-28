#! /usr/bin/env python
import mwclient
import re
import time
import urllib
import urllib2
import sys
from xml.dom import minidom
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme
# Task 3 on [[User:Theo's Little Bot]]

def sokay(donenow):
	"""This function calls a subfunction
	of the theobot module, checkpage().
	"""
	if donenow > 40:
		return False
	
	if donenow % 5 == 0:
		if bot.checkpage("User:Theo's Little Bot/disable/file_tagger") == True:
			return True
		else:
			return False
	else:
		return True

def tag_files(cat_input,project):
	"""The function requires two parameters,
	"cat_input," a list of categories to get
	pages from, and "project," the WikiProject
	name (as it appears in template to be added
	to the resulting talk pages. For example,
	"WikiProject Baseball" -> {{WikiProject Baseball}}
	"""
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)
	
	for category in cat_input:
		zam = mwclient.listing.Category(site, category)
		glob = zam.members()
		flub = []
		for file in glob:
			zip = file.page_title
			print zip.encode('ascii', 'ignore')
			flub.append(zip)

		pages_to_search = []
		
		for member in flub:
			"""The reason this loop exists is so we
			can start midway through if interrupted
			for some reason.
			"""
			print "Appended."
			pages_to_search.append(member)
		
		print "Ready to go!"
		
		donenow = 5
		
		for thisisapage in pages_to_search:
			print "Working on page."
			page = site.Pages[thisisapage]
			text = page.edit()
			r = re.compile(r'\[\[(File|Image):(.*?\.)(jpg|png|gif|svg|JPG|PNG|GIF|SVG).*?\]\]')
			try:
				l = re.findall(r, text)
			except:
				continue
			for set in l:
				if sokay(donenow) == True:
					filename = set[1] + set[2]
					print filename.encode('UTF-8', 'ignore')
					pg = "File talk:" + filename
					page = site.Pages[pg]
					xtext = page.edit()
					x = re.compile(project)
					if x.search(xtext, re.IGNORECASE) is None:
						xtext = "{{" + project + "}}\n" + xtext
						page.save(xtext, summary = "Tagging page for [[Wikipedia:" + project + "|" + project + "]] ([[WP:BOT|bot]] on trial)")
						donenow = donenow + 1
						print "Page saved!"
						time.sleep(2)
						print "Sleeping two seconds." 
					else:
						print "Page was already tagged; skipping."	
				else:
					print "We were disabled."
					sys.exit()

def main():
	cat_input = ['Category:History of baseball']
	project = "WikiProject Baseball"
	
	tag_files(cat_input,project)
	
	print "Run complete!"
	
if __name__ == '__main__':
   main()