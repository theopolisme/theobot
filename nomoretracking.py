#! /usr/bin/env python
from __future__ import unicode_literals

import mwclient
import mwparserfromhell

import urlparse
import datetime

from theobot import bot
from theobot import password

from bs4 import BeautifulSoup
import requests
import MySQLdb

import difflib

# CC-BY-SA Theopolisme

MONTHYEAR = datetime.date.today().strftime("%B %Y")

def process(page):
	contents = page.edit()
	contents_compare = contents
	links = site.api('parse',text=contents,prop="externallinks")['parse']['externallinks']
	for link in links:
		if link.find("utm") != -1:
			req = requests.get(link)
			if req.status_code == requests.codes.ok:
				html_doc = req.text
				soup = BeautifulSoup(html_doc)
				canonical = soup.find("link",rel="canonical")
				if canonical is not None:
					origurl = urlparse.urlsplit(link)
					base_url = urlparse.urlunsplit((origurl[0],origurl[1],'','',''))
					newurl = urlparse.urljoin(base_url, canonical['href'])
					contents = contents.replace(link,newurl)
				else:
					parsed_url = list(urlparse.urlparse(link))
					parsed_url[4] = '&'.join([x for x in parsed_url[4].split('&') if not x.startswith('utm_')])
					newlink = urlparse.urlunparse(parsed_url)
					contents = contents.replace(link,newlink)
			else:
				wikicode = mwparserfromhell.parse(contents)
				templated = False
				# If the link is inside a template, then add {{dead link}} immediately after the template
				for template in wikicode.filter_templates(recursive=True):
					if link in template:
						templated = True
						wikicode.insert_after(template," {{Dead link|date="+MONTHYEAR+"|bot=Theo's Little Bot}}")
				if templated == True:
					contents = unicode(wikicode)
				else:
					# Otherwise, just add {{dead link}} right after the link and hope for the best
					contents = re.sub(r"""("""+re.escape(link)+r"""(?:.*])?))""",
						r"\1 {{Dead link|date="+MONTHYEAR+"|bot=Theo's Little Bot}}",
						flags=re.UNICODE|re.DOTALL
						)
	if contents == contents_compare:
		return False
	diff = difflib.unified_diff(contents_compare.splitlines(), contents.splitlines(), lineterm='')
	print '\n'.join(list(diff))
	print "---------"
	page.save(contents,"[[WP:BOT|Bot]] on trial: Removing Google Analytics tracking codes) ([[User:Theo's Little Bot/disable/tracking|disable]]")
	return True

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

	# The script runs in 500 article increments. ** 50 for the trial **
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
	LIMIT 50;
	"""
	cursor.execute(query)

	donenow = 0
	for title in cursor.fetchall():
		title = title[0].decode("utf-8") # since tuples are returned
		if bot.donenow("User:Theo's Little Bot/disable/tracking",donenow=donenow,donenow_div=5) == True:
			if bot.nobots(page=title,task='tracking') == True:
				if process(site.Pages[title]) == True:
					donenow += 1
				else:
					print "No changes to make."
			else:
				print "Bot was denied, boo hoo."
			
		else:
			print "Bot was disabled...shutting down..."
			sys.exit()

if __name__ == '__main__':
	main()
