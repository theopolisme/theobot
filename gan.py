#! /usr/bin/env python

from __future__ import unicode_literals
import re

import mwclient

from theobot import password
from theobot import bot

# CC-BY-SA Theopolisme

# It will check the source code for any maintenance tags, {{citation needed}} {{refimprove}} and so on
# It will check all images in the article and check fair use status

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)

	global CLEANUPTEMPLATES
	CLEANUPTEMPLATES = listpages(site.Categories['Cleanup templates'])
	print CLEANUPTEMPLATES

	# process_article(site.Pages['Earth: Final Conflict']) # debugging
	gan = site.Pages['Wikipedia:Good article nominations']
	articles = re.findall(r"""#\s*{{GANentry\|1=(.*?)\|""",gan.edit(),flags=re.U)
	for article in articles:
		process_article(site.Pages[article])

def listpages(category):
	"""Recursively goes through a category."""
    results = []
    for page in category:
        if page.namespace == 14:  # 14 is the category namespace
            results += listpages(page)
        else:
            results.append(page.name)
    return results

def process_article(page):
	text = page.edit()
	templates = re.findall(r"""\{\{(.*?)(?:\|.*?\}\}|\}\})""",text,flags=re.U)

	results = """;GAN automated review notes for {}\nGenerated ~~~~~ by [[User:Theo's Little Bot|]]""".format(page.name)

	# CLEANUP TEMPLATES
	results += "\n\n== Cleanup templates on page =="
	taggedtemp = []
	for templatename in list(set(templates)):
		if process_template(templatename) == True:
			taggedtemp.append(templatename)
	if len(taggedtemp) > 0:
		for templatename in taggedtemp:
			results += "\n*{{tlx|"+templatename+"}}"
	else:
		results += "\n''The bot found no cleanup templates on the page.''"
	
	# NON-FREE IMAGES
	# !todo

	print results

def process_template(templatename):
	"""Checks if a template is a maintenace template."""
	template = site.Pages['Template:'+templatename]
	if template.redirect == False:
		if template.name in CLEANUPTEMPLATES:
			return True
		else:
			pass
	else:
		target = re.findall(r"""\[\[(.*?)\]\]""",template.edit(),flags=re.U)[0]
		process_template(target)

if __name__ == '__main__':
	main()
