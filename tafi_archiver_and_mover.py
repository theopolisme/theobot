#! /usr/bin/env python
from __future__ import unicode_literals
import mwclient
import mwparserfromhell
import re
import datetime
import sys
from theobot import bot
from theobot import password
from theobot import timey
import difflib

# CC-BY-SA Theopolisme

def checkpage():
	"""This function calls a subfunction
	of the theobot module, checkpage().
	"""
	if bot.checkpage("User:Theo's Little Bot/disable/tafi arch") == True:
		return True
	else:
		print "Bot was disabled...quitting."
		sys.exit()

def net_support(section):
	supports = re.findall(r"""''support''""",section,re.IGNORECASE | re.DOTALL | re.UNICODE)
	opposes = re.findall(r"""''oppose''""",section,re.IGNORECASE | re.DOTALL | re.UNICODE)
	gross_s = len(supports)
	gross_o = len(opposes)
	
	net_support = gross_s - gross_o
	
	return net_support

def agecheck(section):
	lines = section.split('\n')
	thread = timey.DiscussionThread(howold='old(30d)')
	for line in lines:
		thread.feedLine(line)
	if thread.shouldBeArchived() == True:
		return True
	else:
		return False

def process_nomination(nom,section_header):
	if net_support(nom) >= 3:
		print "net support > 3...moving to holding area..."
		nom_details = [nom,section_header]
		global to_holding
		to_holding.append(nom_details)
	else:
		print "net support not greater than 3."
		if agecheck(nom) == True:
			print "archiving as unsuccessful."
			global to_archive
			to_archive.append(nom)
		else:
			print "30 days haven't elapsed yet; skipping thread."

def process_section(section):
	nominations = re.findall(r'(\s*?\{\{TAFI nom[.\|].*?)\s*?(?=[^=]\{\{TAFI|\=\=|$)',section,re.IGNORECASE | re.DOTALL | re.UNICODE)
	section_header = re.findall(r'==(.*?)==',section,re.IGNORECASE | re.DOTALL | re.UNICODE)[0].strip()
	print "Processing " + section_header
	for nom in nominations:
		process_nomination(nom,section_header)

def move_to_archive():
	for nom in to_archive:
		print "Moving 1 item to archive..."
		global nominations_page_new
		nominations_page_new = nominations_page_new.replace(nom,'',1)
		global unsuccessful_page_new
		unsuccessful_page_new += "\n" + nom.strip()
		global count_archive
		count_archive += 1

def move_to_holding():
	for nom in to_holding:
		header = nom[1]
		print header.encode('ascii', 'ignore')
		msg = nom[0]
		print msg.encode('ascii', 'ignore')
		print "Moving 1 item to holding area..."
		global nominations_page_new
		nominations_page_new = nominations_page_new.replace(nom[0],'',1)
		global count_toholding
		count_toholding += 1
		regex = re.compile(r"""==\s*?{0}\s*?==(.*?)\n==""".format(header), flags=re.DOTALL | re.UNICODE | re.M)
		global holding_new
		holding_new = re.sub(regex, """== {0} ==\g<1>\n\n{1}\n==""".format(header, msg.strip()), holding_new)
	
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

now = datetime.datetime.now()
day = int(now.day)
month = now.strftime('%B')
year = str(now.year)

unsuccessful_page = site.Pages["Wikipedia:Today's articles for improvement/Archives/Unsuccessful Nominations/" + month + " " + year]

global to_archive
to_archive = []

global to_holding
to_holding = []

global unsuccessful_page_new
unsuccessful_page_new = unsuccessful_page.edit()
unsuccessful_page_new += "\n== Archived " + now.strftime('%B') + " " + timey.ordinal(now.day) + " =="

holding_page = site.Pages["Wikipedia:Today's articles for improvement/Holding area"]
global holding_new
holding_new = holding_page.edit()

nominations_page = site.Pages["Wikipedia:Today's articles for improvement/Nominated articles"]
nominations_page_text = nominations_page.edit()

global nominations_page_new
nominations_page_new = nominations_page.edit()

sections = mwparserfromhell.parse(nominations_page_text).get_sections(levels=[2], include_headings=True)
del sections[0] # removes lede section, which we don't want

for section in sections:
	process_section(unicode(section))

# Two counters used in edit summaries
count_toholding = 0
count_archive = 0

move_to_holding()
move_to_archive()

# This is used to remove extras spaces in the noms page. Warning: HACKY.
# !Todo just fix the original regex above. 
rm_spaces = re.compile(r"""\n\n*{{TAFI""", flags=re.DOTALL | re.UNICODE | re.M)
re.sub(rm_spaces, """\n\n{{TAFI""", nominations_page_new)

checkpage()

if count_archive > 0:
	unsuccessful_page.save(unsuccessful_page_new,summary="Moving " + str(count_archive) + " nomination(s) to archive. ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/tafi arch|disable]])")

checkpage()

if count_toholding > 0:
	holding_page.save(holding_new,summary="Moving " + str(count_toholding) + " nomination(s) to holding area. ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/tafi arch|disable]])")

checkpage()

nominations_page.save(nominations_page_new,summary="Moving " + str(count_archive) + " nomination(s) to archive and " + str(count_toholding) + " nomination(s) to holding area. ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/tafi arch|disable]])")
	
print "Run complete!"		