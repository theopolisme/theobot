#! /usr/bin/env python

from __future__ import unicode_literals
import mwclient
import mwparserfromhell
from theobot import password
from theobot import bot
import sys

"""
__FUNCTION DETAILS__

For all files in Category:Non-free images for NFUR review:
	If image meets the following constraints:
		- tagged with {{Non-free album cover}}{{Non-free book cover}}{{Non-free video cover}}{{Non-free logo}}
		- only used in one article
		- file must be used in an infobox
		- file must be the only non-free file in the article
	Then:
		- on the image page:
			- replace {{Non-free use rationale}} or {{Non-free use rationale 2}} with the correct one of the following (subst):
				- {{Non-free use rationale album cover}} {{Non-free use rationale book cover}} {{Non-free use rationale video cover}} {{Non-free use rationale logo}}
			- add "|image has rationale=yes" to {{Non-free album cover}}{{Non-free book cover}}{{Non-free video cover}}{{Non-free logo}}
			- add {{Non-free autogen|bot=Theo's Little Bot}} to the image page
"""

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
		self.page = page # this should be an image object
		self.title = page.page_title
		self.wikicode = mwparserfromhell.parse(page.edit())
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
		self.wikicode = mwparserfromhell.parse("{{subst:"+template+"|Article="+self.article.page_title+"}}\n"+unicode(self.wikicode))

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
			print "Error: ", e
			return False

	def _infobox(self):
		"""Verifies that the image is used in an infobox."""
		for template in self.article_contents.filter_templates():
			if "infobox" in template.name.strip().lower():
				contents = unicode(template)
				if contents.find(self.title) != -1:
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
		return True

	def _no_fur_already(self):
		"""Verifies that the image doesn't already have
		a fair-use rationale, using self.article.
		"""
		contents = unicode(self.wikicode)
		if contents.lower().find(self.article.page_title.lower()) != -1  or contents.find("qualifies as fair use") != -1:
			raise ValueError('{0} already has a fair-use rationale.'.format(self.title))
		return True

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)

	#category = [site.Pages['File:2011 CPISRA Football 7-a-side World Championships.png']]
	category = mwclient.listing.Category(site, 'Category:Non-free images for NFUR review')
	for page in category:
		image = NFURPage(page)
		try:
			print image.final_contents
			print "I would be saving the page right now."
			#page.save(image.final_contents,summary="[[WP:BOT|Bot]]: Adding autogenerated FUR rationale - feel free to expand!")
		except AttributeError:
			continue

if __name__ == '__main__':
	main()
