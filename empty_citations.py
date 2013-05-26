#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import mwclient
import re
import sys
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme

class EmptyCitationBot(object):
	"""Removes empty citations where the editor used {{citation}}
	when the intent was to use {{citation needed}}.
	"""

	def __init__(self):
		self.pages = []
		for page in mwclient.listing.Category(site, 'Category:Pages with empty citations')
			if page.namespace == 0:
				self.pages.append(page)

	def process_pages(self):
		for page in self.pages:
			if bot.donenow("User:Theo's Little Bot/disable/empty citations",donenow=donenow,donenow_div=5,shutdown=50) == True:
				print "Processing page."
				contents = page.edit()
				new_contents = re.sub(r"""{{(citation|cite)}}""", """{{citation needed|date={{subst:DATE}}}}""", flags=re.UNICODE)
				page.save(new_contents,summary="Converting empty {{[[Template:Citation|citation]]}} to {{[[Template:citation needed|citation needed]]}} ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/empty citations|disable]])")
			else:
				sys.exit()

global site
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

print "Running!"
thebot = EmptyCitationBot()
thebot.process_pages()
