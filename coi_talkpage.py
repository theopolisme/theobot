#! /usr/bin/env python
# -*- coding: utf-8  -*-
from __future__ import unicode_literals
import sys
import io
import re
import time
import mwclient
from theobot import password
from theobot import bot

# Originally written by [[User:Riley Huntley]]
# Pywikipedia dependencies converted to mwclient+theobot by [[User:Theopolisme]]
# Licensed under CC-BY-SA 

template_skip_list = [
						'extant organization',
						'COI editnotice',
						'Disambiguation',
						'Disambiguation page',
						'Surname',
						'Sportindex',
						'Given name',
						'DAB',
						'Dab',
						'Sia',
						'Set index',
						'SIA',
						'Set index article',
						'Dbig',
						'Disam',
						'Disamb',
						'Disambig',
						'Hndis',
						'Hospital disambiguation',
						'Mathematical disambiguation',
						'Mountain index',
						'Roadindex',
						'School disambiguation',
						'Shipindex',
						'Mountain index',
						'Disambiguation cleanup',
					]
template_skip_regex = re.compile(ur'\{(Template:)?('+'|'.join(template_skip_list)+')',re.I)
skip_these = ['Organization']
title_blacklist = ['list', 'disambiguation']
title_blacklist_regex = re.compile(ur'(%s)' % '|'.join(title_blacklist),re.I)

site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

log_page = site.Pages["User:Theo's Little Bot/talkpage"]
stop_page = site.Pages["User:Theo's Little Bot/disable/talkpage"]

def main():
	check_page()
	log('Run started')
	cat = mwclient.listing.Category(site, 'CATEGORY') # Category:Companies based in California
	print "Getting category contents..."
	pages = bot.listpages(cat,names=False)
	for page in pages:
		if page.namespace == 0:
			if page.name not in skip_these and not title_blacklist_regex.search(page.name):
				if page.exists:
					if not page.redirect:
						talk_page = site.Pages['Talk:'+page.name]
						text = talk_page.edit()
						if not template_skip_regex.search(text):
							newtext = '{{COI editnotice|track=yes}}\n' + text
							try:
								check_page()
								talk_page.save(newtext, summary="[[WP:BOT|Bot]] on trial: Added [[Template:COI editnotice]] to [[%s]]) ([[User:Theo's Little Bot/disable/talkpage|disable]]" % page.name, minor=True)
								log('Saved edit on [[%s]]' % talk_page.name)
							except:
								log('Skipping %s because of unknown error' % talk_page.name)
						else:
							log('[[%s]] ignored due to regular expression' % talk_page.name)
					else:
						log('Page %s is a redirect; skipping.' % page.name)
				else:
					log('Page %s does not exist; skipping.' % page.name)
			else:
				log('Page %s was in skip list.' % page.name)
		else:
			log('Page %s is not in the article namespace.' % page.name)
	shut_down()

def check_page():
	text = stop_page.edit()
	if 'enable' not in text.lower():
		log('Check page disabled! Aborting!')
		shut_down()
		
def shut_down():
	log('Run ended.')
	f = io.open('Talkpage.txt','r', encoding='utf-8')
	log_text = f.read()
	f.close()
	log_page.save(log_text,"Uploading logs for [[User:Theo's Little Bot|Theo's Little Bot]]")
	sys.exit(0)

def log(text):
	tm = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime())
	print tm + ": " + text
	f3 = io.open('Talkpage.txt', 'a', encoding='utf-8')
	f3.write('\n* %s\t%s' % (tm,text))
	f3.close()

if __name__ == "__main__":
	main()
