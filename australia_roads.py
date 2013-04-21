#! /usr/bin/env python
import mwclient
import mwparserfromhell
import sys
import re
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme
# Task 4 on [[User:Theo's Little Bot]]

# Defining list.
pages = []

def sokay(donenow):
	"""This function calls a subfunction
	of the theobot module, checkpage().
	"""
	if donenow % 5 == 0:
		if bot.checkpage("User:Theo's Little Bot/disable/australia roads") == True:
			return True
		else:
			return False
	else:
		return True

def cats_recursive(category):
	"""Recursively goes through
	categories. Almost TOO
	straightforward.
	"""
	
	str = 'Jubilee 150 Walkway'
	
	for item in category:
		if item.find(str) != -1:
			pass
		
		if "Category" in str(item):
			cats_recursive(item)
		else:
			x = item.page_title
			pages.append(x)

def editor(text):
	"""This function does the bulk of the
	work. Requires one parameter, text.
	"""
	
	code_compare = mwparserfromhell.parse(text)
	code = mwparserfromhell.parse(text)
	
	for template in code.filter_templates():
		if template.name in ('WP Australia', 'WP Australian music', 'WPAUS', 'WPAUSTRALIA', 'WPAustralia', 'WikiProject Australia') and not template.has_param("road"):
			template.add("road", "yes")
			print "Road value added."
		if template.name in ('WP Australia', 'WP Australian music', 'WPAUS', 'WPAUSTRALIA', 'WPAustralia', 'WikiProject Australia') and not template.has_param("road-importance"):
			try:
				xyz = template.get("importance").value
				template.add("road-importance", xyz)
				print "Road-importance value added."
			except:
				print "No importance to add."
		if template.name == 'WikiProjectBannerShell':
			x = template.get(1).value
			for template in x.filter_templates():
				if template.name in ('WP Australia', 'WP Australian music', 'WPAUS', 'WPAUSTRALIA', 'WPAustralia', 'WikiProject Australia') and not template.has_param("road"):
					template.add("road", "yes")
					print "Road value added."
				if template.name in ('WP Australia', 'WP Australian music', 'WPAUS', 'WPAUSTRALIA', 'WPAustralia', 'WikiProject Australia') and not template.has_param("road-importance"):
					try:
						xyz = template.get("importance").value
						template.add("road-importance", xyz)
						print "Road-importance value added."
					except:
						print "No importance to add."
	
	text = unicode(code)
	
	return text 

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)
	
	print "Getting category contents...this could take a while."
	zam = mwclient.listing.Category(site, 'Category:Roads in Australia')
	cats_recursive(zam)

	print "Working on " + str(len(pages)) + " pages."
	
	donenow = 5
	y = pages.index('Thomas Price')
	y = y-5
	del pages[:y]
	
	for page in pages:
		if sokay(donenow) == True:
			talk = u'Talk:' + page
			print "Working on " + talk.encode('ascii', 'ignore')
			page = site.Pages[talk]
			text = page.edit()
			y = editor(text)
			try:
				page.save(y, summary = "Adding road parameter to {{[[Template:WikiProject Australia|WikiProject Australia]]}} ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/australia_roads|disable]])")
				print talk.encode('ascii', 'ignore') + " saved."
			except AttributeError:
				print "Page save error; retrying."
				try:
					page.save(y, summary = "Adding road parameter to {{[[Template:WikiProject Australia|WikiProject Australia]]}} ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/australia_roads|disable]])")
					print talk.encode('ascii', 'ignore') + " saved."
				except AttributeError:
					print "Page skipped due to unknown error."
			donenow = donenow + 1
		elif sokay(donenow) == False:
			print "Aw, snap, we were disabled. Quitting in 3...2...1..."
			sys.exit()
		
if __name__ == '__main__':
   main()