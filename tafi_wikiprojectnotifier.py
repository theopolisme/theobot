#! /usr/bin/env python
from __future__ import unicode_literals
import mwclient
import mwparserfromhell
import re
import datetime
import sys
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme

class WikiProjectNotifier():
	def __init__(self):
		"""We're ready!"""
		self.donenow = 0
		self.get_current_articles()
		associated_wikiprojects = {}
		for article in self.articles:
			associated_wikiprojects[article] = self.process_article(article)

		for article,wikiprojects in associated_wikiprojects.items():
			for project in wikiprojects:
				if bot.donenow("User:Theo's Little Bot/disable/tafi",donenow=self.donenow,donenow_div=5) == True:
					self.notify_wikiproject(project,article)
					self.donenow += 1
				else:
					print "Bot was disabled."
					sys.exit()

	def get_current_articles(self):
		"""Stores this week's articles to a variable,
		`self.articles`. """
		pages = []
		x = site.api(action='query',prop='extracts',explaintext='y',titles='Template:TAFI/Blurb/thisweek')
		for key,contents in x['query']['pages'].items():
			contents = contents['extract']
		for line in contents.splitlines():
			page = line.strip()
			pages.append(page)
		self.articles = pages

	def process_article(self,article):
		"""Given an article, returns a list of wikiprojects
		associated with the given article.
		"""
		print "Working on " + article
		talk = site.Pages['Talk:'+article]
		contents = talk.edit()
		wikicode = mwparserfromhell.parse(contents)

		wikiprojects = []
		
		def process_template(template):
			"""Get the wikiproject that a
			given template represents.
			"""
			templatey = site.Pages[unicode(template)]
			if templatey.redirect == False:
				contents = templatey.edit()
				if contents.find('WPBannerMeta') != -1:
					project = re.search(r"""\s*\|\s*PROJECT\s*=\s*(.*?)\s*\|""",contents,flags=re.U | re.DOTALL | re.M).group(1)
					wikiprojects.append(project.strip())
				else:
					pass
			else:
				target = re.findall(r"""\[\[(.*?)\]\]""",templatey.edit(),flags=re.U)[0]
				process_template(target)

		for template in wikicode.filter_templates(recursive=True):
			process_template("Template:"+unicode(template.name))

		return wikiprojects

	def notify_wikiproject(self,project,article):
		"""Given a WikiProject and an article, notifies
		the WikiProject via its talk page.
		"""
		page = site.Pages['Wikipedia talk:WikiProject '+project]
		if page.exists == True:
			notification = u"""\n\n== One of your project's articles has been featured ==\n{{{{subst:TAFI project notice/bot|Article={article}|user=[[User:Theopolisme|Theopolisme]]}}}}""".format(article=article)
			current_contents = page.edit()
			page.save(current_contents+notification,summary="[[WP:BOT|Bot]]: Notifying WikiProject about [[{article}]] being selected as one of [[WP:TAFI|Today's articles for improvement]]".format(article=article))
			print "Project notified!"
		else:
			print "I think we got a bad egg; [[{0}]] doesn't exist!".format(page.page_title)

# Logs in to the site.
global site
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

WikiProjectNotifier()
