#! /usr/bin/env python

from __future__ import unicode_literals
import sys
import re

import mwclient
import mwparserfromhell

from theobot import password
from theobot import bot

# CC-BY-SA Theopolisme

global NONFREE_TAGS,RATIONALE_TEMPLATES,ALL_RATIONALE

RATIONALE_TEMPLATES = [
				"Non-free use rationale album cover",
				"Non-free use rationale book cover",
				"Non-free use rationale video cover",
				"Non-free use rationale logo"
				]

NONFREE_TAGS = [
				"Non-free album cover",
				"Non-free book cover",
				"Non-free video cover",
				"Non-free logo"
				]

ALL_RATIONALE = []
ALL_RATIONALE.extend(RATIONALE_TEMPLATES)
for name in RATIONALE_TEMPLATES:
	ALL_RATIONALE += bot.redirects(name,namespace=10,pg_prefix="Template:",output='page_title')

class NFURPage():
	"""This class is used to represent a page
	in Category:Non-free images for NFUR review.
	"""

	def __init__(self,page):
		self.page = page # this is an image object
		self.title = page.page_title
		self.wikicode = mwparserfromhell.parse(page.edit())
		self.additionaldetails = {}
		if self.assert_okay() == True:
			print "{0} is ready for auto-review!".format(self.title)
			self.add_rationale()
			self.add_image_has_rationale()
			self.final_contents = unicode(self.wikicode)

	def add_rationale(self):
		"""Adds the correct rationale template based
		on the non-free tag.
		"""
		index = NONFREE_TAGS.index(self.imagetype)
		template = RATIONALE_TEMPLATES[index]
		new_wikicode = "{{"+template+"|Article="+self.article.page_title+"|Use=Infobox"
		for key,value in self.additionaldetails.items():
			if value != None:
				new_wikicode += "|{0}={1}".format(key,value)
		new_wikicode += "}}\n"+unicode(self.wikicode)
		self.wikicode = mwparserfromhell.parse(new_wikicode)

	def add_image_has_rationale(self):
		"""Add image_has_rationale parameter."""
		for template in self.wikicode.filter_templates():
			if template.name in NONFREE_TAGS: 
				template.add('image has rationale','yes')

	def add_autogen(self):
		"""Adds the non-free autogen template."""
		self.wikicode = mwparserfromhell.parse("{{Non-free autogen|bot=Theo's Little Bot}}\n"+unicode(self.wikicode))

	def assert_okay(self):
		"""Makes sure that the image satisfies all
		conditions for processing.
		"""
		try:
			self._tagged()
			self._usage()
			self._infobox()
			self._no_fur_already()
			return True
		except ValueError as e:
			print "Error: ", unicode(e).encode('ascii', 'replace')
			return False

	def _infobox(self):
		"""Verifies that the image is used in an infobox."""
		for template in self.article_contents.filter_templates():
			if "infobox" in template.name.strip().lower():
				contents = unicode(template)
				if contents.find(self.title) != -1:
					try:
						self.additionaldetails['Artist'] = re.search("Artist\s*=\s*(.*)\s*",contents,flags=re.U | re.IGNORECASE).group(1)
					except AttributeError:
						pass
					try:
						self.additionaldetails['Author'] = re.search("Author\s*=\s*(.*)\s*",contents,flags=re.U | re.IGNORECASE).group(1)
					except AttributeError:
						pass
					try:
						self.additionaldetails['Cover_artist'] = re.search("Cover_artist\s*=\s*(.*)\s*",contents,flags=re.U | re.IGNORECASE).group(1)
					except AttributeError:
						pass
					try:
						self.additionaldetails['Name'] = re.search("Name\s*=\s*(.*)\s*",contents,flags=re.U | re.IGNORECASE).group(1)
					except AttributeError:
						pass
					try:
						self.additionaldetails['Publisher'] = re.search("Publisher\s*=\s*(.*)\s*",contents,flags=re.U | re.IGNORECASE).group(1)
					except AttributeError:
						pass
					try:
						self.additionaldetails['Author'] = re.search("Author\s*=\s*(.*)\s*",contents,flags=re.U | re.IGNORECASE).group(1)
					except AttributeError:
						pass
					try:
						self.additionaldetails['Label'] = re.search("Label\s*=\s*(.*)\s*",contents,flags=re.U | re.IGNORECASE).group(1)
						self.additionaldetails['Label'] = unicode(mwparserfromhell.parse(re.sub(r"<\s*br[\s*>|/]", " / ", self.additionaldetails['Label'], flags=re.U | re.IGNORECASE)).strip_code())
					except AttributeError:
						pass
					try:
						self.additionaldetails['Distributor'] = re.search("Distributor\s*=\s*(.*)\s*",contents,flags=re.U | re.IGNORECASE).group(1)
					except AttributeError:
						pass
					return True
		raise ValueError('{0} is not used in an infobox in {1}.'.format(self.title,self.article))

	def _tagged(self):
		"""Verifies that the image is tagged with one
		of the currently bot-supported non-free tags.
		"""
		for template in self.wikicode.filter_templates():
			if any(name in template.name.strip() for name in NONFREE_TAGS):
				self.imagetype = template.name
				return True

		raise ValueError('{0} is not tagged with one of the currently accepted templates.'.format(self.title))

	def _usage(self):
		"""Verifies that an image is used in only one article."""
		usage = self.page.imageusage(limit=50)
		for i, page in enumerate(usage):
			if i == 0:
				self.article = page
				self.article_contents = mwparserfromhell.parse(page.edit())
			else:
				raise ValueError('{0} is used in more than one article!'.format(self.title))
		if usage.count == 0: 
			raise ValueError('{0} is used in no articles!'.format(self.title))
		return True

	def _no_fur_already(self):
		"""Verifies that the image doesn't already have
		a fair-use rationale, using self.article.
		"""
		contents = unicode(self.wikicode)

		for rationale in ALL_RATIONALE:
			if contents.lower().find(rationale.lower()) != -1:
				raise ValueError('{0} already has a fair-use rationale template.'.format(self.title))
		if contents.lower().find(self.article.page_title.lower()) != -1  or contents.find("qualifies as fair use") != -1:
			raise ValueError('{0} already has something that resemebles a fair-use rationale.'.format(self.title))
		return True

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)
	donenow = 0

	# category = [site.Pages['File:TheoBotTestImage.png']] - testing only
	category = mwclient.listing.Category(site, 'Category:Non-free images for NFUR review')
	for page in category:
		image = NFURPage(page)
		try:
			if image.final_contents and bot.donenow("User:Theo's Little Bot/disable/nfur",donenow=donenow,donenow_div=5,shutdown=50) == True:
			 	page.save(image.final_contents,summary="[[WP:BOT|Bot]] on trial: Adding autogenerated FUR rationale - feel free to expand!) ([[User:Theo's Little Bot/disable/nfur|disable]]")
			 	donenow += 1
			 	sys.exit()
		except AttributeError:
			continue

if __name__ == '__main__':
	main()
