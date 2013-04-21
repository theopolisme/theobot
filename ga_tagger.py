import mwclient
import re
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme

def cats_recursive(category):
	"""Recursively goes through
	categories. Almost TOO
	straightforward.
	
	Note that category must be
	a STRING.
	"""
	pages = []
	
	category = mwclient.listing.Category(site, category)
	print category
	
	for item in category:
		if "Category:" in unicode(item):
			cats_recursive(item)
		else:
			x = item.strip_namespace(item.name)
			print x.encode('UTF-8', 'ignore')
			pages.append(x)
	
	return pages

def tagged_already(page):
	"""Returns TRUE if page has been
	tagged with {{Good article}} or
	one of its redirects.
	"""
	page = site.Pages[page]
	text = page.edit()
	
	regexp1 = re.compile(r'\{\{([Gg]ood [Aa]rticle|GA [Aa]rticle)\}\}')

	if regexp1.search(text) is not None:
		return True
	else:
		return False

def process_current_gas():
	"""For all current GAs, makes sure
	topicon is on article and, if not,
	adds it.
	"""
	pages = cats_recursive('Category:Wikipedia good articles')

	for talkpage in pages:
		page = talkpage
		print "Working on: " + page.encode('UTF-8', 'ignore')
		if tagged_already(page) == False:
			pagee = site.Pages[page]
			text = pagee.edit()
			text = "{{Good article}}\n" + text
			pagee.save(text,summary="Adding {{[[Template:Good article|Good article]]}} topicon")
			global counts
			counts['current-added'] = counts['current-added'] + 1
			counts['total_edits'] = counts['total_edits'] + 1
		else:
			print "Page already tagged."

def process_delisted_gas():
	"""Removes topicon from delisted
	or former GA nominees.
	"""
	pages = cats_recursive('Category:Delisted good articles')
	pages += cats_recursive('Former good article nominees')

	for talkpage in pages:
		page = talkpage[5::]
		print "Working on: " + page.encode('UTF-8', 'ignore')
		if tagged_already(page) == True:
			pagee = site.Pages[page]
			text = pagee.edit()
			text_diff = pagee.edit()
			text = re.sub(r'\{\{([Gg]ood [Aa]rticle|GA [Aa]rticle)\}\}', '', text)
			if text != text_diff:
				pagee.save(text,summary="Removing {{[[Template:Good article|Good article]]}} topicon")
				global counts
				counts['former-removed'] = counts['former-removed'] + 1
				counts['total_edits'] = counts['total_edits'] + 1

def main():
	"""This defines and fills a global
	variable for the site, and then runs.
	"""
	print "Logging in as " + password.username + "..."
	
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)
	
	global counts
	counts = {'total_edits': 0, 'current-added': 0, 'former-removed': 0}
	
	process_current_gas()
	process_delisted_gas()
	
	print "TOTAL EDITS MADE: " + counts['total_edits'] + "\nADDED: " + counts['current-added'] + "\nREMOVED: " + counts['former-removed']

if __name__ == '__main__':
   main()