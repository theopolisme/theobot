#! /usr/bin/env python

from __future__ import unicode_literals
import mwclient
from theobot import password
import re
import urllib

# CC-BY-SA Theopolisme

class CentijimboBot():
	def __init__(self):
		self.cj = self.calculate_jimbo()

	def calculate_jimbo(self):
		"""Calculates the current
		centijimbo rate.
		"""
		jimbo_watchers = self._watchers(['User:Jimbo Wales'])
		cj = float(.01 * jimbo_watchers)
		return cj

	def process_users(self):
		"""Does most of the work."""
		page = site.Pages["User:Theo's Little Bot/centijimbo"]
		contents = page.edit()

		lines = contents.splitlines()
		newlines = []
		line_user = {}
		for line in lines:
			user = re.findall(r"\[\[(User:.*?|User[\s_]talk:.*?)(?:\||\]\]|#)",line,flags=re.U)[0]
			line_user[user] = line

		watcher_stuff = self._watchers(line_user.keys())

		for user,watchers in watcher_stuff.iteritems():
			try:
				line = line_user[user]
			except KeyError:
				line = line_user[user.lower().capitalize()]
			usercj = self._to_centi(watchers)
			newline = re.sub(r"\d*?\.\d}}\'\'\'",str(usercj)+"}}'''",line,flags=re.U)
			line_zip = [usercj,newline]
			newlines.append(line_zip)

		newlines = sorted(newlines, key=lambda cj: float(cj[0]),reverse=True)
		
		final = ''
		for item in newlines:
			final = final + item[1].replace(r'\'','\'') + "\n"
		
		return final

	def _watchers(self,list_of_pages):
		"""Returns a dictionary containing the
		number of watchers for each page, or, if
		only one page was specified, simply the
		number of watchers for that page.
		"""
		results = site.api(action='query',prop='info',inprop='watchers',titles='|'.join(map(unicode,list_of_pages)))
		pages = results[u'query'][u'pages']
		watcher_data = {}
		for page in pages:
			try:
				watchers = pages[page][u'watchers']
			except KeyError:
				watchers = 0
			if len(list_of_pages) == 1:
				return watchers # we're done here, no need for the dictionary
			title = pages[page][u'title']
			watcher_data[title] = watchers
		return watcher_data

	def _to_centi(self,watchers):
		"""Given a number, converts it
		to centijimbos.
		"""
		raw = float(watchers) / self.cj
		return "{0:.1f}".format(raw)

global site
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

robot = CentijimboBot()
x = robot._watchers(['User:Jimbo Wales','User:Theopolisme'])
page = site.Pages["User:Theo's Little Bot/centijimbo"]
page.save(robot.process_users(),summary="[[WP:BOT|Bot]]: Updating centijimbo records, enjoy!")
print "All done!"