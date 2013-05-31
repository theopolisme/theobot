#! /usr/bin/env python
import mwclient
import datetime
import re
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme
# Task 7 on [[User:Theo's Little Bot]]

def sokay(donenow):
	"""Simple function to check checkpage.
	This function calls a sub-function
	of the theobot.bot module, checkpage().
	"""
	if donenow % 5 == 0:
		if bot.checkpage("User:Theo's Little Bot/disable/tafi") == True:
			return True
		else:
			return False
	else:
		return True

def static_list():
	"""A little function per request to generate a static
	page of this week's TAFI nominations.
	"""
	final_contents = "=== Week {{subst:CURRENTWEEK}}'s TAFIs ===\n<sup>Last updated ~~~~~</sup>\n"
	#http://en.wikipedia.org//w/api.php?action=query&prop=extracts&format=json&explaintext=&titles=Template%3ATAFI%2FBlurb%2Fthisweek
	x = site.api(action='query',prop='extracts',explaintext='y',titles='Template:TAFI/Blurb/thisweek')
	for key,contents in x['query']['pages'].items():
		contents = contents['extract']
	for line in contents.splitlines():
		page = line.strip()
		final_contents += "\n* [[" + page + "]]"
	pg = site.Pages['Template:TAFI/Blurb/static']
	pg.save(final_contents,summary='[[WP:BOT|Bot]]: Updating static TAFI listings')

def remove_old_week_from_schedule():
		"""Removes the previous, now completed week from the schedule
		and moves it to archive."""
		schedule = site.Pages["Wikipedia:Today's articles for improvement/Schedule/real"]
		text = schedule.edit()
		
		old_schedule_contents = re.finall(r"""(;<big>\[\[Wikipedia:Today's articles for improvement/""" + str(now.year) + r"/" + str((now.isocalendar()[1])-1) + r"""\|.*?)\s*;<big>\[\[""", text)[0]
		
		new_text = re.sub(r""";<big>\[\[Wikipedia:Today's articles for improvement/""" + str(now.year) + r"/" + str((now.isocalendar()[1])-1) + r"""\|.*?;<big>\[\[""", r""";<big>\[\[""", text, re.IGNORECASE | re.DOTALL | re.UNICODE)
		schedule.save(new_text,summary="[[WP:BOT|Bot]]: Removing completed week from schedule - week {0}.".format(str((now.isocalendar()[1])-1)))

		schedule_archive = site.Pages["Wikipedia:Today's articles for improvement/Archives/{0} schedule".format(str(now.year))]
		arch_text = schedule_archive.edit() + "\n\n" + old_schedule_contents
		schedule_archive.save(arch_text,summary="[[WP:BOT|Bot]]: Moving completed week to archive - week {0}.".format(str((now.isocalendar()[1])-1)))

# Logs in to the site.
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

# Sets the timestamp from which we derive week numbers.
global now
now = datetime.datetime.now()

# Runs the static_list() function per request
static_list()

# Removes the completed week from the schedule and moves it to archive
remove_old_week_from_schedule()

# This loop adds the tags to the new week's articles.
for i in range(1,11):
	if sokay(i+4) == True:
		stringy = "Wikipedia:Today's articles for improvement/" + str(now.year) + "/" + str(now.isocalendar()[1]) + "/" + str(i)
		editme = site.Pages[stringy].edit()
		pagen = re.findall("\[\[(.*?)\]\]", editme)[0]
		page = site.Pages[pagen]
		try:
			x = re.findall("\{\{TAFI\}\}", page.edit(), flags=re.IGNORECASE)[0]
			print "Page already tagged; skipping."
		except:
			text = page.edit()
			if text[0] == "{" and text[2] != "I":
				text = re.sub(r"}}", "}}\n{{TAFI}}", text, 1, flags = re.U)
			else:
				text = "{{TAFI}}\n" + text
			print text[0:100] # debugging - shows the changes
			print "Saving page " + pagen.encode("ascii", "replace") + " - added TAFI template."
			page.save(text,summary="Adding [[WP:TAFI|Today's articles for improvement]] tag ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/tafi|disable]])")

# This loop removes the tags from the old week's articles.
for i in range(1,11):
	if sokay(i+4) == True:
		stringy = "Wikipedia:Today's articles for improvement/" + str(now.year) + "/" + str((now.isocalendar()[1])-1) + "/" + str(i)
		editme = site.Pages[stringy].edit()
		pagen = re.findall("\[\[(.*?)\]\]", editme)[0]
		page = site.Pages[pagen]
		text = re.sub(r"\{\{TAFI\}\}\n", "", page.edit())
		print "Saving page " + pagen + " - removed TAFI template."
		page.save(text,summary="Removing [[WP:TAFI|Today's articles for improvement]] tag ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/tafi|disable]])")
		
		# This next set of instructions is for tagging the article's talk page.
		start_date = now + datetime.timedelta(-7)
		talk = site.Pages["Talk:" + pagen]
		tt = talk.edit()
		try:
			x = re.findall("\{\{Former TAFI\}\}", tt, flags=re.IGNORECASE)[0]
			print "Talk page already tagged; skipping."
		except:
			tt = "{{Former TAFI|date=" + start_date.strftime('%B %d, %Y') + "}}\n" + tt
			talk.save(tt,summary="Tagging page with {{[[Template:Former TAFI|Former TAFI]]}} ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/tafi|disable]])")
		
