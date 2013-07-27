# -*- coding: utf-8 -*-
#! /usr/bin/env python

from __future__ import unicode_literals
import re

import mwclient

from theobot import password

import operator

# CC-BY-SA Theopolisme

def full_report():
	"""Generates a report about the number of maintenance templates
	in current GAs.
	"""
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)

	global CLEANUPTEMPLATES
	CLEANUPTEMPLATES = listpages(site.Categories['Cleanup templates'])
	print "Got cleanup templates."

	report = {}
	good_articles = mwclient.listing.Category(site, 'Category:Good articles')
	for article in good_articles:
		print article.name
		templates = cleanup(article.edit())
		if len(templates) > 0:
			report[article.name] = len(templates)
	sorted_report = sorted(report.iteritems(), key=operator.itemgetter(1), reverse=True)

	resultspage = site.Pages["User:Theo's Little Bot/GAs with maintenance tags"]
	results = "== Good articles tagged with maintenance templates ==\n(sorted by number of templates; last updated ~~~~~)"
	for tuple in sorted_report:
		results += "\n# [[{}]] - {} maintenance templates".format(tuple[0],tuple[1])

	resultspage.save(results,"[[WP:BOT|Bot]]: Updating GA report")

def cleanup(text):
	def process_template(templatename):
		"""Checks if a template is a maintenance template."""
		template = site.Pages['Template:'+templatename]
		if template.redirect == False:
			if template.name in CLEANUPTEMPLATES:
				return True
			else:
				pass
		else:
			target = re.findall(r"""\[\[(.*?)\]\]""",template.edit(),flags=re.U)[0]
			process_template(target)

	templates = re.findall(r"""\{\{(.*?)(?:\|.*?\}\}|\}\})""",text,flags=re.U)
	taggedtemp = []
	for templatename in list(set(templates)):
		if process_template(templatename) == True:
			taggedtemp.append(templatename)
	return taggedtemp

def listpages(category):
	"""Recursively goes through a category."""
	results = []
	for page in category:
		if page.namespace == 14:  # 14 is the category namespace
			results += listpages(page)
		else:
			results.append(page.name)
	return results

if __name__ == '__main__':
	full_report()
