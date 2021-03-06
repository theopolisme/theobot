#! /usr/bin/env python
from __future__ import unicode_literals
import mwclient
import re
from theobot import bot
from theobot import password
import sys

# CC-BY-SA Theopolisme

#~~~~ MODIFY THESE SETTINGS ~~~~#
naughty_links = ['playerhistory.com','soccerdatabase.eu']
addtl_summary_info = "(per [[Wikipedia:Administrators%27_noticeboard/IncidentArchive796#Mass_removal_of_references_to_soccerdatabase.eu_website|AN/I thread]])"
#~~~~ MODIFY ABOVE SETTINGS ~~~~#

site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

try:
	temp_var = naughty_links[1]
	summary = "Removing links to defunct sites: {0} {1}. ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/external links|disable]])".format(", ".join(naughty_links),addtl_summary_info)
except IndexError:
	summary = "Removing links to defunct site, {0} {1}. ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/external links|disable]])".format(naughty_links[0],addtl_summary_info)

full_results = []
to_process = []

print "Generating list of pages linking to {0}...be patient!".format(naughty_links)
for link in naughty_links:
	results = mwclient.listing.List(site=site,list_name='exturlusage',prefix='eu',euquery="*."+link,euprop='title')
	for item in results:
		full_results.append(item)

print "Generating list of mainspace pages linking to {0}...".format(naughty_links)

for page in full_results:
	if page[u'ns'] == 0 and page[u'title'] not in to_process:
		print("{0}".format(page[u'title']).encode('UTF-8'))
		to_process.append(site.Pages[page[u'title']])

print "Processing mainspace pages linking to {0}...".format(naughty_links)

donenow = 0
for page in to_process:
	if bot.donenow("User:Theo's Little Bot/disable/external links",donenow=donenow,donenow_div=5) == True:
		print "~~~\n~~~\n"
		contents = page.edit()
		for link in naughty_links:
			try:
				refname = re.search(r"<ref(?:\s*name\s*=\s*(.*?))>[^<]*?" + link.replace('.',r'\.') + r".*?</ref>",contents,flags=re.UNICODE).groups()[0]
				print refname
				contents = re.sub(r"<ref(?:\s*name\s*=\s*(.*?))>[^<]*?" + link.replace('.',r'\.') + r".*?</ref>", '', contents, flags=re.UNICODE | re.DOTALL)
				contents = re.sub(r"<ref.*?" + refname.replace('"',r'') + r".*?>", "", contents, flags=re.UNICODE)
			except AttributeError:
				pass	
			contents = re.sub(r"\*(?!.*?<ref).*?" + link.replace('\.',r'\.') + r".*", '', contents, flags=re.UNICODE)
			contents = re.sub(r"\[.*" + link.replace('.',r'\.') + r".*]", '', contents, flags=re.UNICODE)
		page.save(contents,summary=summary)
		donenow += 1
	else:
		sys.exit('Program was disabled.')

print "We're done!"
