import mwclient
import mwparserfromhell
import sys
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme
# Task 5 on [[User:Theo's Little Bot]]

# Defining list.
pages = []

def sokay(donenow):
	"""This function calls a subfunction
	of the theobot module, checkpage().
	"""
	if donenow % 5 == 0:
		if bot.checkpage("User:Theo's Little Bot/disable/reggaeton") == True:
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
	
	# This is used to check if we need to add the template.	
	has_been_tagged = False
	
	for template in code.filter_templates():
		if template.name in ('WikiProject Latin music', 'Latin music'):
			has_been_tagged = True
		if template.name in ('WikiProject Latin music', 'Latin music') and not template.has_param("reggaeton"):
			template.add("reggaeton", "yes")
			print "Reggaeton value added."
		if template.name == 'WikiProjectBannerShell':
			x = template.get(1).value
			for template in x.filter_templates():
				if template.name in ('WikiProject Latin music', 'Latin music'):
					has_been_tagged = True
				if template.name in ('WikiProject Latin music', 'Latin music') and not template.has_param("reggaeton"):
					template.add("reggaeton", "yes")
					print "Reggaeton value added."
	
	text = unicode(code)
	
	if has_been_tagged = False:
		text = "{{WikiProject Latin music|class=|importance=|reggaeton=yes}}\n" + text
	return text 

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)
	
	print "Getting category contents...this could take a while."
	zam = mwclient.listing.Category(site, 'Category:Reggaeton')
	cats_recursive(zam)

	print "Working on " + str(len(pages)) + " pages."
	
	donenow = 5
	
	for page in pages:
		if sokay(donenow) == True:
			talk = u'Talk:' + page
			print "Working on " + talk.encode('ascii', 'ignore')
			page = site.Pages[talk]
			text = page.edit()
			y = editor(text)
			try:
				page.save(y, summary = "Adding reggaeton parameter to {{[[Template:WikiProject Latin music|WikiProject Latin music]]}} ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/reggaeton|disable]])")
				print talk.encode('ascii', 'ignore') + " saved."
			except AttributeError:
				print "Page save error; retrying."
				try:
					page.save(y, summary = "Adding reggaeton parameter to {{[[Template:WikiProject Latin music|WikiProject Latin music]]}} ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/reggaeton|disable]])")
					print talk.encode('ascii', 'ignore') + " saved."
				except AttributeError:
					print "Page skipped due to unknown error."
			donenow = donenow + 1
		elif sokay(donenow) == False:
			print "Aw, snap, we were disabled. Quitting in 3...2...1..."
			sys.exit()
		
if __name__ == '__main__':
   main()