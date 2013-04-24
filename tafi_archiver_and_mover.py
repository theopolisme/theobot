#! /usr/bin/env python
import mwclient
import mwparserfromhell
import re
import datetime
from theobot import bot
from theobot import password
from theobot import timey

# CC-BY-SA Theopolisme

def net_support(section):
	supports = re.findall(r'support',section,re.IGNORECASE | re.DOTALL | re.UNICODE)
	opposes = re.findall(r'oppose',section,re.IGNORECASE | re.DOTALL | re.UNICODE)
	gross_s = len(supports)
	gross_o = len(opposes)
	
	net_support = gross_s - gross_o
	
	return net_support

def older_than_ten_days(section):
	lines = section.split('\n')
	thread = timey.DiscussionThread(howold='old(10d)')
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
		if older_than_ten_days(nom) == True:
			print "archiving as unsuccessful."
			global to_archive
			to_archive.append(nom)
		else:
			print "10 days hasn't elapsed yet; skipping thread."

def process_section(section):
	nominations = re.findall(r'(\{\{TAFI nom[.\|].*?)(?=[^=]{{TAFI)',section,re.IGNORECASE | re.DOTALL | re.UNICODE)
	section_header = re.findall(r'==(.*?)==',section,re.IGNORECASE | re.DOTALL | re.UNICODE)[0]
	print "Processing " + section_header
	for nom in nominations:
		process_nomination(nom,section_header)

def move_to_archive():
	for nom in to_archive:
		print "Moving 1 item to archive..."
		global nominatons_page_new
		nominatons_page_new.replace(nom, '')
		global unsuccessful_page_new
		unsuccessful_page_new += "\n" + nom
		global count_archive
		count_archive += 1

def move_to_holding():
	for nom in to_holding:
		print "Moving 1 item to holding area..."
		global nominatons_page_new
		nominatons_page_new.replace(nom[0], '')
		global count_toholding
		count_toholding += 1
		# !TODO
		# Add some code to move given nom to the holding area under correct section

site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

now = datetime.datetime.now()
day = int(now.day)
month = str(now.month)
year = str(now.year)

unsuccessful_page = site.Pages["Wikipedia:Today's articles for improvement/Archives/Unsuccessful Nominations/" + month + " " + year]

global unsuccessful_page_new
unsuccessful_page_new = unsuccessful_page.edit()
unsuccessful_page_new += "\n== Archvied " + now.month + " " + timey.ordinal(now.day) + " =="

holding_page = site.Pages["Wikipedia:Today's articles for improvement/Holding area"]
global holding_new
holding_new = holding_page.edit()

nominatons_page = site.Pages["Wikipedia:Today's articles for improvement/Nominated articles"]
nominations_page_text = nominatons_page.edit()
global nominatons_page_new
nominatons_page_new = nominatons_page.edit()

sections = mwparserfromhell.parse(nominations_page_text).get_sections(levels=[2], include_headings=True)
del sections[0] # removes lede section, which we don't want

for section in sections:
	#print unicode(section).encode('UTF-8', 'ignore')
	process_section(unicode(section))

# Two counters used in edit summaries
count_toholding = 0
count_archive = 0

move_to_holding()
move_to_archive()

unsuccessful_page.save(unsuccessful_page_new,summary="[[WP:BOT|Bot]]: Moving " + count_archive + " nominations to archive.")
holding_page.save(holding_new,summary="[[WP:BOT|Bot]]: Moving " + count_toholding + " nominations to holding area.")
nominatons_page.save(nominatons_page_new,summary="[[WP:BOT|Bot]]: Moving " + count_archive + " nominations to archive and " + count_toholding + " nominations to holding area.")
			