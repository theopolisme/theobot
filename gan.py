# -*- coding: utf-8 -*-
#! /usr/bin/env python

from __future__ import unicode_literals
import re

import mwclient

from theobot import password
from theobot import bot
from theobot import spellcheck_awb
# from theobot import spellcheck # _awb covers this

from itertools import groupby
import operator
import collections

# CC-BY-SA Theopolisme

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)

	global CLEANUPTEMPLATES
	CLEANUPTEMPLATES = listpages(site.Categories['Cleanup templates'])
	print "Got cleanup templates."

	# process_article(site.Pages['Earth: Final Conflict']) # debugging
	gan = site.Pages['Wikipedia:Good article nominations']
	articles = re.findall(r"""#\s*{{GANentry\|1=(.*?)\|""",gan.edit(),flags=re.U)

	# Report the number of maintenance templates in current GAs
	# !todo don't run this on every run? run other stuff first? 
	full_report()

	# This prints article data for ten articles to one page, to save space in demo
	done = 0
	alphabet = collections.defaultdict(list)
	for article in articles:
		if done < 10:
			alphabet[article[0].upper()].append(process_article(site.Pages[article]))
			done += 1
		else:
			break
	for letter,value in alphabet.items():
		print "Saving {}".format(letter)
		text = '\n'.join(value)
		site.Pages["User:Theo's Little Bot/GAN/"+letter].save(text,"[[WP:BOT|Bot]]: Updating [[WP:GAN|GAN]] report")

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
	print "\n\n=====\nProcessing {}".format(page.name)
	text = page.edit()

	results = """== [[{0}]] ==\n'''Generated ~~~~~ by [[User:Theo's Little Bot|]]'''""".format(page.name)

	## ALERTS
	results += alerts(text)
	## CLEANUP TEMPLATES
	results += cleanup(text,page.name)	
	## IMAGES
	results += images(text,page)

	print results
	return results

def alerts(text):
	results = "\n\n=== Alerts ==="
	alerts = []

	# at least one citation per paragraph
	def paragraph(lines):
		for group_separator,line_iteration in groupby(lines.splitlines(True),key=unicode.isspace):
			if not group_separator:
				yield ''.join(line_iteration)
	paratext = re.sub(r""".*?==""","==",text,count=1,flags=re.DOTALL) # the lead does not need citations
	for p in paragraph(paratext):
		if not re.search(r"""(==|Category:|\[\[File:|\[\[Image:|{{Authority control|{{.*}}|^<.*?>|^;|^\|)""",p.strip()):
			if not re.search(r"""(sfn|\<ref)""",p) and len(p) > 100: # only look at paragraphs longer than 100 chars
				alerts.append("\n* Lacking a citation in the paragraph beginning {{{{xt|{}...}}}}".format(p[:70]))

	# check for common misspelled words
	print "Checking for misspelled words..."
	sp = []

	# from [[Wikipedia:Lists of common misspellings/For machines]]
	# * disabled because _awb covers this, below
	#for spell_tuple in spellcheck.Misspellings(text).check():
	#	sp.append("\"{0}\" (line {1})".format(spell_tuple[1],spell_tuple[0]))

	# from [[Wikipedia:AutoWikiBrowser/Typos]]
	for line,typos in spellcheck_awb.typos(text).items():
		for typo,correction in typos:
			typoindex = text.index(typo)
			sp.append("\"{0}\" → \"{1}\" ({{{{xt|<nowiki>...{2}...</nowiki>}}}})".format(typo,correction,text[typoindex-20:typoindex+20].replace('\n', ' ')))

	if len(sp) > 0:
		alerts.append("\n* Possible typo(s) or misspelling(s) detected: " + ', '.join(sp))

	if len(alerts) > 0:
		results += ''.join(alerts)
	else:
		results += "\n''There are no alerts for this page.''"

	return results

def cleanup(text,raw=False):
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

	results = "\n\n=== Cleanup templates on page ==="
	templates = re.findall(r"""\{\{(.*?)(?:\|.*?\}\}|\}\})""",text,flags=re.U)
	taggedtemp = []
	for templatename in list(set(templates)):
		if process_template(templatename) == True:
			taggedtemp.append(templatename)
	if len(taggedtemp) > 0:
		for templatename in taggedtemp:
			results += "\n*{{tlx|"+templatename+"}}"
	else:
		results += "\n''The bot found no cleanup templates on this page.''"

	if raw == True:
		return taggedtemp
	else:
		return results

def images(text,page):
	results = "\n\n=== Images used on page ==="
	imageresults = []
	for image in page.images():
		tempstring = ""
		original_description = image.edit()
		if original_description != "":
			text = site.expandtemplates(text=original_description).lower()
			if text.find("non-free use") != -1:
				tempstring += " {{red|'''The image is non-free.'''}}"
			if text.find("""width: 15%; font-size: 12pt">Non-free media information and [[Wikipedia:Non-free use rationale guideline|use rationale]]""") != -1:
				tempstring += " A recognizd non-free use rationale was found."
			if text.find("imbox-license") != -1:
				tempstring += " A license was provided for the image."
			if text.find("public domain") != -1:
				tempstring += " The image is said to be in the public domain."
			if tempstring == "":
				tempstring += " No information was found for the image."
		else:
			tempstring += " The image is hosted on Commons, so assuming freely licensed."
		tempstring = "*[[:{}]]:".format(image.name) + tempstring
		imageresults.append(tempstring)

	if len(imageresults) > 0:
		results += '\n' + '\n'.join(imageresults)
	else:
		results += "\n''The bot found no images on this page.''"

	return results

def full_report():
	"""Generates a report about the number of maintenance templates
	in current GAs.
	"""
	report = {}
	good_articles = mwclient.listing.Category(site, 'Category:Good articles')
	for article in good_articles:
		templates = cleanup(article.edit(),raw=True)
		if len(templates) > 0:
			report[article.name] = len(templates)
	sorted_report = sorted(report.iteritems(), key=operator.itemgetter(1))

	resultspage = site.Pages["User:Theo's Little Bot/GAs with maintenance tags"]
	results = "== Good articles tagged with maintenance templates ==\n(sorted by number of templates; last updated ~~~~~)"
	for tuple in sorted_report:
		results += "\n# [[{}]] - {} maintenance templates".format(tuple[0],tuple[1])

	resultspage.save(results,"[[WP:BOT|Bot]]: Updating GA report")

if __name__ == '__main__':
	main()

