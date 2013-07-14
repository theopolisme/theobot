#! /usr/bin/env python
from __future__ import unicode_literals

import mwclient
import mwparserfromhell

import re

from theobot import bot
from theobot import password

from bs4 import BeautifulSoup
import requests

import difflib

# CC-BY-SA Theopolisme

URL = re.compile(r"""((?:\w+:)?\/\/[^<>\[\]\s"]+)""",flags=re.UNICODE|re.DOTALL)
UTM = re.compile(r"""[\?&]utm_.*?=.*?(?=\s|&|$)""",flags=re.UNICODE|re.DOTALL)

def process(page):
	contents = page.edit()
	contents_compare = contents
	links = re.findall(URL,contents)
	for link in links:
		if link.find("utm") != -1:
			html_doc = requests.get(link).text
			soup = BeautifulSoup(html_doc)
			canonical = soup.find("link",rel="canonical")
			if canonical is not None:
				contents = contents.replace(link,canonical['href'])
			else:
				newlink = re.sub(UTM,"",link)
				contents = contents.replace(link,newlink)
	diff = difflib.unified_diff(contents_compare.splitlines(), contents.splitlines(), lineterm='')
	print '\n'.join(list(diff))
	print "---------"
	page.save(contents,"[[WP:BOT|Bot]]: Removing Google Analytics tracking codes")

global site
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

process(site.Pages['User:Theopolisme/Bay 1']) # debugging
