#! /usr/bin/env python
from __future__ import unicode_literals

import mwclient
import mwparserfromhell

from urlparse import urlparse, urlunparse

from theobot import bot
from theobot import password

from bs4 import BeautifulSoup
import requests
import MySQLdb

import difflib

# CC-BY-SA Theopolisme

def process(page):
	contents = page.edit()
	contents_compare = contents
	links = site.api('parse',text=contents,prop="externallinks")['parse']['externallinks']
	for link in links:
		if link.find("utm") != -1:
			html_doc = requests.get(link).text
			soup = BeautifulSoup(html_doc)
			canonical = soup.find("link",rel="canonical")
			if canonical is not None:
				contents = contents.replace(link,canonical['href'])
			else:
				parsed_url = list(urlparse(link))
				parsed_url[4] = '&'.join([x for x in parsed_url[4].split('&') if not x.startswith('utm_')])
				newlink = urlunparse(parsed_url)
				contents = contents.replace(link,newlink)
	diff = difflib.unified_diff(contents_compare.splitlines(), contents.splitlines(), lineterm='')
	print '\n'.join(list(diff))
	print "---------"
	page.save(contents,"[[WP:BOT|Bot]]: Removing Google Analytics tracking codes")

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)

	print "And we're live."
	connection = MySQLdb.connect(
		host = 'enwiki.labsdb',
		db = 'enwiki_p',
		read_default_file = '~/replica.my.cnf'
	)

	# The script runs in 500 article increments.
	# In other words, in each run, it will process
	# and fix 500 articles and then stop.
	# !todo figure out how long a run takes vs replag
	# and then optimize crontab
	cursor = connection.cursor()
	query = """\
	SELECT page_title
	FROM externallinks
	JOIN page
	ON page_id = el_from
	WHERE el_to LIKE "%&utm_%=%"
	AND page_namespace = 0
	LIMIT 500;
	"""
	cursor.execute(query)

	donenow = 0
	for title in cursor.fetchall():
		if bot.donenow("User:Theo's Little Bot/disable/tracking",donenow=donenow,donenow_div=5) == True:
			if bot.nobots(page=title,task='tracking') == True:
				process(site.Pages[title])
			else:
				print "Bot was denied, boo hoo."
			donenow += 1
		else:
			print "Bot was disabled...shutting down..."
			sys.exit()

if __name__ == '__main__':
	main()
