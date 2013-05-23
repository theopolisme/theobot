#! /usr/bin/env python
from __future__ import unicode_literals
import mwclient
import mwparserfromhell
import re
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme

global site
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

class ArchiveURLProcessor():
	def __init__(self):
		self.donenow = 0
		print "ArchiveURLProcessor() initialized."
		return

	def start(self,pages):
		for page in pages:
			self.process_page(page)

	def process_page(self,page):
		if bot.donenow("User:Theo's Little Bot/disable/archiveurl",donenow=self.donenow,donenow_div=5) == True:
			print "Processing " + page.encode("ascii", "replace")
			page = site.Pages[page]
			text = page.edit()
			wikicode = mwparserfromhell.parse(text)
			for template in wikicode.filter_templates():
				if "cite web" in template.name:
					archiveurl = None
					for param in template.params:
						items = param.strip().split('=')
						if items[0] == 'url':
							continue
						if items[0] == 'archiveurl':
							archiveurl = items[0]
					if archiveurl is not None: 
						if re.search(r"web\.archive\.org",unicode(template),flags=re.U) != None:
							try:
								new_url = re.search(r"\|[\s]*archiveurl[\s]*=[\s]*(?:http://|https://)web.archive.org/web/\d*/(.*?)(?:\||}})", unicode(template), flags=re.UNICODE | re.M).groups(0)[0]
							except AttributeError:
								print "I don't recognize the archive structure, sadly. Skipping."
								continue
							template.add("url", new_url.strip())
							print "Added url parameter to {{cite web}} template."
					else:
						continue
			text = unicode(wikicode)
			try:
				page.save(text,summary="Fixing references: adding url parameter ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/archiveurl|disable]])")
				self.donenow += 1 # we only count it as "done" when we make a change
			except:
				print "Unable to save page; skipping."

pages = bot.cats_recursive('Category:Pages with archiveurl citation errors')
archivebot = ArchiveURLProcessor()		
archivebot.start(pages)