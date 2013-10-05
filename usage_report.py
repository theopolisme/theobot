#! /usr/bin/env python

from __future__ import unicode_literals

import mwclient

from theobot import password
from theobot import bot

# CC-BY-SA Theopolisme

class TemplateUsage(object):
	"""Given a template name, creates an object with
	data about its usage.

	>>> tu = TemplateUsage("Template:RailGauge")

	Example row from tu.csv():
	[ID, NAMESPACE, PAGENAME, PARAM1, OTHERPARAMS, REDIRECTFROM]
	"7865", "0", "Indian Railways", "1676mm", "", ""

	"""
	def __init__(self,template):
		self.template = site.Pages[template]

	def get(self):
		"""Starts all of the necessary functions to get the
		usage data"""
		self._redirects()
		self.usagedata = self._getusagedata()


	def _redirects(self):
		"""Stores all of the redirects to the template
		(as well as original template name) to
		self.template_redirects
		"""
		return True

	def _getusagedata(self,page):
		"""Given a page object returns a list of lists
		with usage data. Each transclusion is its own
		item in the list.

		[TRANSCLUSION1, TRANSCLUSION2]
		"""

	def csv(self,file):
		"""Saves a CSV to a given file with the template usage,
		where each row represents a transclusion.
		"""
		return True
		

print "Powered on."
global site
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

if __name__ == '__main__':
	main()
