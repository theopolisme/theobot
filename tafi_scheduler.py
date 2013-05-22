#! /usr/bin/env python
# -*- coding: utf-8 -*-

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
from random import shuffle
import operator
from datetime import date, timedelta

# CC-BY-SA Theopolisme

class TAFIScheduler():

	def __init__(self):
		self.now = datetime.datetime.now()
		#self.week = self.now.isocalendar()[1]+1 
		self.week = 27
		self.holding_area_page = site.Pages["Wikipedia:Today's articles for improvement/Holding area"]
		self.parse_holding(self.holding_area_page.edit())
		self.holding_numbers(self.holding_contents_dict)
		self.holding_sections_slots(self.holding_contents_dict)
		self.holding_sections_selection(self.holding_contents_dict)
		self.generate_page_list()
		self.update_date_pages()
		self.update_weekly_subpage()
		self.rm_from_holding()
		self.update_schedule()

	def parse_holding(self,holding_contents):
		"""Returns a dict of subsections in the holding area,
		for which each value is a list of nominations in that
		subsection.
		"""
		
		sections = mwparserfromhell.parse(holding_contents).get_sections(levels=[2], include_headings=True)
		del sections[0:2] # removes lede section and instructions section, which we don't want
		
		useful_dict = {}
		for section in sections:
			nominations = re.findall(r'(\s*?\{\{TAFI nom[.\|].*?)\s*?(?=([^=]\{\{TAFI|\z))',unicode(section),re.IGNORECASE | re.DOTALL | re.UNICODE | re.M)
			real_noms = []
			for nom in nominations:
				if nom[0] != u'':
					real_noms.append(nom[0])
			section_header = re.findall(r'==(.*?)==',unicode(section),re.IGNORECASE | re.DOTALL | re.UNICODE)[0].strip()
			useful_dict[section_header] = real_noms
		
		self.holding_contents_dict = useful_dict

	def holding_numbers(self,dict):
		"""We end up with two variables, see bottom, used
		for determining how many "slots" each section gets.
		"""
		
		nom_counts = {} # this is a dict that includes the total number of noms for each section

		for key, value in dict.iteritems(): # in other words, for each section
			number_of_noms = len(value)
			nom_counts[key] = number_of_noms
		
		total_number_of_noms = 0
		for key,value in nom_counts.iteritems():
			total_number_of_noms += value
		
		self.total_number_of_noms = total_number_of_noms
		self.nom_counts = nom_counts
	
	def holding_sections_slots(self,dict):
		"""For each section, figures out how many slots it deserves.
		Saves to self.slots_dict a dict with each section and
		number of slots.
		"""
		
		slots_dict = {}

		total_slots = 0	
		items = self.nom_counts.items()
		items = sorted(items, key=operator.itemgetter(1), reverse=True) # sorts the list by # of noms
		
		high_ones = {}
		low_ones = {}
		
		for key,value in items:
			if value >= 10:
				high_ones[key] = value
			if value < 10:
				low_ones[key] = value
		
		low_ones = low_ones.items()
		shuffle(low_ones)
		
		items = high_ones.items() + low_ones
		
		for key, value in items:
			percentage = int(100 * (float(value)/self.total_number_of_noms))
			number_of_slots = int((.01 * percentage) * 10)
			total_slots += number_of_slots
			if total_slots < 10 and number_of_slots < 1:
				number_of_slots = 1
				total_slots += number_of_slots
			print "{0} has {1} slots.".format(key,number_of_slots)
			slots_dict[key] = number_of_slots

		print "Total number of slots this week: {0}".format(total_slots)
		
		self.slots_dict = slots_dict

	def holding_sections_selection(self,dict):
		"""Given a dict of nominations + section titles,
		selects the correct number of noms for each section
		and outputs them to a master list, self.weekly_noms
		"""
		
		thisweek = []
		for section, noms in dict.items():
			to_pick = self.slots_dict[section]
			for i in range(0,to_pick):
				thisweek.append(noms[i])
		
		self.weekly_noms = thisweek

	def rm_from_holding(self):
		"""Removes old noms from the holding area."""
		
		new_page = self.holding_area_page.edit()
		
		for nom in self.weekly_noms:
			new_page = new_page.replace(nom,'')
		
		rm_spaces = re.compile(r"""\n\n*{{TAFI""", flags=re.DOTALL | re.UNICODE | re.M)
		new_page = re.sub(rm_spaces, """\n\n{{TAFI""", new_page)
		
		self.holding_area_page.save(new_page,summary="Removing newly scheduled nominations.")

	def generate_page_list(self):
		"""Updates self.pagesforthisweek with a list of
		unicode literals for this week's pages.
		"""
		pagesforthisweek = []
		
		for nom in self.weekly_noms:
			nom_title = re.findall(r"{{TAFI nom.*?|article=(.*?)\|",nom,re.IGNORECASE | re.DOTALL | re.UNICODE)[1].strip()
			pagesforthisweek.append(nom_title)
			
		self.pagesforthisweek = pagesforthisweek
		print self.pagesforthisweek

	def update_date_pages(self):
		"""Edits each /1/1 (date) page and adds that week's article."""
	
		i = 0 # this is for page numbers

		for page in self.pagesforthisweek:
			i += 1
			stringy = "Wikipedia:Today's articles for improvement/" + str(self.now.year) + "/" + str(self.week) + "/" + str(i) # note the plus one, this is so we do the week AFTER
			text = "[[" + page + "]]"	
			site.Pages[stringy].save(text,"[[WP:BOT|Bot]]: Updating TAFI schedule.")

	def update_weekly_subpage(self):
		"""Updates this week's subpage."""
		page_contents = """<noinclude>[[File:Today's Article For Improvement star.svg|right|85px]]</noinclude>
<includeonly>{{Random subpage|page=Wikipedia:Today's articles for improvement/{{#time:Y}}/{{#time:W}}|start=1|end=4}}&nbsp;– {{Random subpage|page=Wikipedia:Today's articles for improvement/{{#time:Y}}/{{#time:W}}|start=5|end=7}}&nbsp;– {{Random subpage|page=Wikipedia:Today's articles for improvement/{{#time:Y}}/{{#time:W}}|start=8|end=10}}<div style="float: right;">[[Wikipedia:Today's articles for improvement|'''More&nbsp;selections...''']]</div></includeonly>
<noinclude>This is the '''[[Wikipedia:Today's articles for improvement|TAFI]]''' queue for week {{SUBPAGENAME}} in the year 2013.  It is currently [[Wikipedia:Today's articles for improvement/{{#time:Y}}/{{#time:W}}|week {{#time:W}}]]{{#ifeq:{{CURRENTYEAR}}|2013||&#32;in the year {{CURRENTYEAR}}}}.
*{{/1}}
*{{/2}}
*{{/3}}
*{{/4}}
*{{/5}}
*{{/6}}
*{{/7}}
*{{/8}}
*{{/9}}
*{{/10}}
</noinclude>"""

		self.subpage_str = "Wikipedia:Today's articles for improvement/" + str(self.now.year) + "/" + str(self.week) 
		if site.Pages[self.subpage_str].edit() == u'':
			site.Pages[self.subpage_str].save(page_contents,summary="[[WP:BOT|Bot]]: Updating TAFI weekly subpage.")
		else:
			print "Someone already updated this week's subpage!"

	def week_start_date(self, year, week):
		"""Given a year and a week, calculates
		the start and end dates for that week.
		"""
		d = date(year, 1, 1)    
		delta_days = d.isoweekday() - 1
		delta_weeks = week
		if year == d.isocalendar()[0]:
			delta_weeks -= 1
		delta = timedelta(days=-delta_days, weeks=delta_weeks)
		start_date = d + delta
		return start_date.strftime('%d %B %Y')

	def update_schedule(self):
		"""Adds this week to the schedule."""
		schedule = site.Pages["Wikipedia:Today's articles for improvement/Schedule/real"]
		text = schedule.edit()
		text += """\n\n;<big>[[Wikipedia:Today's articles for improvement/2013/{0}|Week {0}]]:</big> (beginning {1})""".format(self.week,self.week_start_date(self.now.year,self.week))
		
		nommies = []

		for nom in self.weekly_noms:
			nom_contents = re.findall(r"\{\{TAFI nom.*?\}\}",nom,re.IGNORECASE | re.DOTALL | re.UNICODE)[0].strip()
			nommies.append(nom_contents)
		
		for nom in nommies:
			text += """\n* """ + nom
			
		schedule.save(text,summary="[[WP:BOT|Bot]]: Updating TAFI schedule - adding week {0}.".format(self.week))

site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

scheduler = TAFIScheduler()
