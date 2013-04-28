#! /usr/bin/env python
import mwclient
import mwparserfromhell
import sys
from theobot import bot
from theobot import password
from theobot import lists

# CC-BY-SA Theopolisme
# Task 11 on [[User:Theo's Little Bot]]

# Defining list.
pages = []

def sokay(donenow):
	"""This function calls a subfunction
	of the theobot module, checkpage().
	"""
	if donenow % 5 == 0:
		if bot.checkpage("User:Theo's Little Bot/disable/latin music") == True:
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
	for item in category:
		if "Category" in str(item):
			cats_recursive(item)
		else:
			x = item.page_title
			pages.append(x)

def editor(text):
	"""This function does the bulk of the
	work. Requires one parameter, text.
	"""
	
	code = mwparserfromhell.parse(text)
	
	for template in code.filter_templates():
		if template.name in ('WikiProject Latin America', 'WPLAMERICA', 'WP Latin America') and template.has_param("music"):
			try:
				music_imp = template.get('music-importance').value
				template.remove("music-importance")
			except ValueError:
				try:
					music_imp = template.get('importance').value
				except ValueError:
					music_imp = False
			template.name("WikiProject Latin music")
			template.remove("music")
			if music_imp != False:
				template.add("importance",music_imp)

		if template.name in lists.bannershell_redirects:
			x = template.get(1).value
			for template in x.filter_templates():
				if template.name in ('WikiProject Latin America', 'WPLAMERICA', 'WP Latin America') and template.has_param("music"):
					try:
						music_imp = template.get('music-importance').value
						template.remove("music-importance")
					except ValueError:
						try:
							music_imp = template.get('importance').value
						except ValueError:
							music_imp = False
					template.name("WikiProject Latin music")
					template.remove("music")
					if music_imp != False:
						template.add("importance",music_imp)
	
	text = unicode(code)
	
	return text 

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)
	
	print "Getting category contents...this could take a while."
	zam = mwclient.listing.Category(site, 'Category:WikiProject Latin American music articles')
	cats_recursive(zam)

	print "Working on " + str(len(pages)) + " pages."
	
	donenow = 5
	
	for page in pages:
		if sokay(donenow) == True:
			talk = u'Talk:' + page
			print "Working on " + talk.encode('UTF-8')
			page = site.Pages[talk]
			text = page.edit()
			y = editor(text)
			try:
				page.save(y, summary = "Converting to {{[[Template:WikiProject Latin music|WikiProject Latin music]]}} ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/latin music|disable]])")
				print talk.encode('UTF-8') + " saved."
			except AttributeError:
				print "Page save error; retrying."
				try:
					page.save(y, summary = "Converting to {{[[Template:WikiProject Latin music|WikiProject Latin music]]}} ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/latin music|disable]])")
					print talk.encode('UTF-8') + " saved."
				except AttributeError:
					print "Page skipped due to unknown error."
			donenow = donenow + 1
		elif sokay(donenow) == False:
			print "Aw, snap, we were disabled. Quitting in 3...2...1..."
			sys.exit()
		
if __name__ == '__main__':
   main()