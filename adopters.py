#! /usr/bin/env python

from __future__ import unicode_literals
import mwclient
import mwparserfromhell
import datetime
from theobot import password
from time import mktime

# CC-BY-SA Theopolisme

page = site.Pages["Wikipedia:Adopt-a-user/Adoptee's Area/Adopters"]
now = datetime.datetime.now()

def active(user):
	"""Returns True if a user is active (i.e., last edit withinin
	XX months ago), False if inactive.
	"""
	contribs = site.usercontributions(user,limit=1)
	for contrib in contribs:
		timestamp = datetime.datetime.fromtimestamp(mktime(contrib[u'timestamp']))
		tdelta = now - timestamp
		if tdelta > datetime.timedelta(days=30):
			print "{0} hasn't edited for {1}, which is greater than 30 days.".format(user,tdelta)
			return False # user has not edited in past 30 days
		else:
			print "{0} last edited {1}, which is less than 30 days.".format(user,tdelta)
			return True

def main():
	wikicode = mwparserfromhell.parse(page.edit())
	for template in wikicode.filter_templates():
		if "Wikipedia:Adopt-a-user/Adopter Profile" in template.name:
			user = template.get('username').value.strip()
			if active(user) == False:
				template.add('available','no')
				template.add('bot-updated','yes')
			elif template.has_param('bot-updated') == True:
				template.add('available','yes')
	new_contents = unicode(wikicode)
	page.save(new_contents,summary="[[WP:BOT|Bot]]: Updating availabilities.")

if __name__ == '__main__':
	print "Powered on."
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)
	main()