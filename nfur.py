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
		- file must be the only non-free file in the article
	Then:
		- on the image page:
			- add some fairuse rationales to {{Non-free use rationale}} or {{Non-free use rationale 2}}
				- *** I will need rationales to insert ***
			- add "|image has rationale=yes" to {{Non-free album cover}}{{Non-free book cover}}{{Non-free video cover}}{{Non-free logo}}
			- add a new parameter "bot=Theo's Little Bot", to {{Non-free album cover}}{{Non-free book cover}}{{Non-free video cover}}{{Non-free logo}}
				- this might need additional discussion as far implementation/categorization
"""

global NONFREE_TAGS

RATIONALE_TEMPLATES = [
						"Non-free use rationale",
						"Non-free use rationale 2"
						]
NONFREE_TAGS = [
				"Non-free album cover",
				"Non-free book cover",
				"Non-free video cover",
				"Non-free logo"
				]

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

	def assert_okay(self):
		"""Makes sure that the image satisfies all
		conditions for processing.
		"""
		try:
			self._tagged()
			self._usage()
			self._onlynonfree()
			return True
		except ValueError as e:
			print "Error: ", e
			return False

	def _tagged(self):
		"""Verifies that the image is tagged with one
		of the currently bot-supported non-free tags.
		"""
		for template in self.wikicode.filter_templates():
			if any(name in template.name.strip() for name in NONFREE_TAGS):
				return True

		raise ValueError('{0} is not tagged with one of the currently accepted templates.'.format(self.title))

	def _usage(self):
		"""Verifies that an image is used in only one article."""
		usage = self.page.imageusage()
		usage.next()
		if usage.count > 1:
			raise ValueError('{0} is used in more than one article!'.format(self.title))
		else:
			return True

	def _onlynonfree(self):
		"""Verifies that an image is the only non-free
		image used in an article.
		"""
		# !TODO
		# We'll need to find all images on the page, and then parse their
		# description pages to look for signs that they are non-free.
		# raise ValueError("{0} can't be processed because there are more than one non-free images used in the article {1}".format(self.title,article))
		return True

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)

	category = mwclient.listing.Category(site, 'Category:Non-free images for NFUR review')
	for page in category:
		NFURPage(page)

if __name__ == '__main__':
	main()