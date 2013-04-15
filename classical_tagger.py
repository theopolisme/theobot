import mwclient
import mwparserfromhell
import sys
import re
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme
# Task 6 on [[User:Theo's Little Bot]]

# Defining list.
pages = []

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
	
	code_compare = mwparserfromhell.parse(text)
	code = mwparserfromhell.parse(text)

	for template in code.filter_templates():
		print template.name
		if template.name in ('WikiProject Classical Greece and Rome', 'Classical Greece and Rome', 'Classical greece and rome', 'WP Classics', 'WikiProject Classics', 'Classical greece and rome',  'Classical_greece_and_rome'):
			try:
				template.remove("importance")
			except ValueError:
				pass
			template.add("importance", "low")
			print "Importance value added."
		if template.name in ('WikiProjectBannerShell', 'WikiProject Banners', 'WPBS'):
			x = template.get(1).value
			for template in x.filter_templates():
				if template.name in ('WikiProject Classical Greece and Rome', 'Classical Greece and Rome', 'Classical greece and rome', 'WP Classics', 'WikiProject Classics',  'Classical greece and rome', 'Classical_greece_and_rome'):
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
	
	print "Getting category contents...this could take a while."
	zam = mwclient.listing.Category(site, 'Category:Unknown-importance Classical Greece and Rome articles')
	cats_recursive(zam)

	print "Working on " + str(len(pages)) + " pages."
	
	donenow = 5
	
	search_strings = ['Papyrus Oxyrhynchus', 'Milecastle', 'Legio ', 'Classis ', 'Cohors ', 'Battle of ', 'Lex ', 'Arch of', 'Pons ', 'Pont ', 'Ponte ', 'Siege of ', 'Aqua ', 'bridge', 'Bridge', 'fort', 'Fort', 'villa', 'Villa', '(mythology)']

	for page in pages:
		okay = False
		if sokay(donenow) == True:
			for x in search_strings:
				if page.find(x) != -1:
					okay = True
			if okay == True:
				talk = u'Talk:' + page
				print "Working on " + talk.encode('ascii', 'ignore')
				page = site.Pages[talk]
				text = page.edit()
				y = editor(text)
				try:
					page.save(y, summary = "Adding importance parameter to {{[[Template:WikiProject Classical Greece and Rome|WikiProject Classical Greece and Rome]]}} ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/greece|disable]])")
					print talk.encode('ascii', 'ignore') + " saved."
				except AttributeError:
					print "Page save error; retrying."
					try:
						page.save(y, summary = "Adding importance parameter to {{[[Template:WikiProject Classical Greece and Rome|WikiProject Classical Greece and Rome]]}} ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/greece|disable]])")
						print talk.encode('ascii', 'ignore') + " saved."
					except AttributeError:
						print "Page skipped due to unknown error."
				donenow = donenow + 1
			else:
				# Page was not applicable.
				pass
		elif sokay(donenow) == False:
			print "Aw, snap, we were disabled. Quitting in 3...2...1..."
			donenow = donenow + 1
			sys.exit()
		
if __name__ == '__main__':
   main()