#! /usr/bin/env python
import mwclient
import mwparserfromhell
import sys
import re
from theobot import bot
from theobot import password
from theobot import lists

# CC-BY-SA Theopolisme
# Task 6 on [[User:Theo's Little Bot]]

def sokay(donenow):
	"""This function calls a subfunction
	of the theobot module, checkpage().
	"""
	if donenow % 10 == 0:
		if bot.checkpage("User:Theo's Little Bot/disable/greece") == True:
			return True
		else:
			return False
	else:
		return True

def editor(text):
	"""This function does the bulk of the
	work. Requires one parameter, text.
	"""
	
	code = mwparserfromhell.parse(text)

	for template in code.filter_templates():
		if template.name.lower() in ('wikiproject classical greece and rome', 'classical greece and rome', 'classical greece and rome', 'wp classics', 'wikiproject classics', 'classical greece and rome',  'classical_greece_and_rome'):
			try:
				template.remove("importance")
			except ValueError:
				pass
			template.add("importance", "low")
			print "Importance value added."
		if template.name in lists.bannershell_redirects:
			x = template.get(1).value
			for template in x.filter_templates():
				if template.name.lower() in ('wikiproject classical greece and rome', 'classical greece and rome', 'classical greece and rome', 'wp classics', 'wikiproject classics', 'classical greece and rome',  'classical_greece_and_rome'):
					try:
						template.remove("importance")
					except ValueError:
						pass
					template.add("importance", "low")
					print "Importance value added."
	
	text = unicode(code)
	return text 

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)
	
	print "Getting category contents..."
	category = mwclient.listing.Category(site, 'Category:Unknown-importance Classical Greece and Rome articles')

	donenow = 5
	
	for page in category:
		if sokay(donenow) == True:
			if  page.namespace == 1:
				print "Working on {0}".format(page.page_title.encode('ascii','replace'))
				text = page.edit()
				y = editor(text)
				try:
					page.save(y, summary = "Adding importance parameter to {{[[Template:WikiProject Classical Greece and Rome|WikiProject Classical Greece and Rome]]}} ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/greece|disable]])")
					print talk.encode('ascii', 'replace') + " saved."
				except AttributeError:
					print "Page save error; retrying."
					try:
						page.save(y, summary = "Adding importance parameter to {{[[Template:WikiProject Classical Greece and Rome|WikiProject Classical Greece and Rome]]}} ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/greece|disable]])")
						print talk.encode('ascii', 'replace') + " saved."
					except AttributeError:
						print "Page skipped due to unknown error."
				donenow = donenow + 1
			else:
				print "Skipping page...not in article space :/"
		elif sokay(donenow) == False:
			print "Aw, snap, we were disabled. Quitting in 3...2...1..."
			donenow = donenow + 1
			sys.exit()
		
if __name__ == '__main__':
   main()