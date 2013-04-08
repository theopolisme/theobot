import mwclient
from time import mktime
from datetime import datetime
import time
import settings

# CC-BY-SA Theopolisme
# A simple script for a simple friend.
# Tracks [[User:RileyBot]]'s global watchlist

# This is for logging...global variable.
global logs
logs = []

# This is for the main output.
global l
l = []

def log(text):
	"""Adds a given piece of text
	to log list. Uses global var.
	"""
	# timestamp every item to make tracking easier, also use UTC time to avoid local issues
	tm = time.strftime(u'%Y-%m-%d %H:%M:%S',time.gmtime())
	# post every item to its own line
	global logs
	logs.append('\n* %s\t%s' % (tm,text))

def prog_end():
	"""When the program ends, this saves
	its log into a wikipage.
	"""
	global logs
	loggery = ''.join(logs)
	site2 = mwclient.Site('en.wikipedia.org')
	site2.login(settings.username, settings.password)
	log_page = site2.Pages['User:RileyBot/Logs/Watchlist']
	log_text = log_page.edit() + loggery
	log_page.save(log_text,'[[User:RileyBot|Bot]]: Uploading logs for [[User:RileyBot/watchlist|watchlist]]')
	
def generate(wiki):
	"""This function does most of the work,
	which includes checking checkpages and
	generating watchlists/tables.
	"""
	print "Working on " + wiki
	log('Working on ' + wiki)
	site1 = mwclient.Site(wiki)
	site1.login(settings.username, settings.password)
	data = site1.watchlist(prop="ids|timestamp|title|user")
	page3 = site1.Pages['User:RileyBot/Stop']
	text3 = page3.edit()
	if text3.lower() != u'enable':
		log('Check page is still enabled on ' + wiki)
	global l
	l.append("\n=== " + wiki + " ===")

	l.append("""\n{| class="wikitable sortable"
	|-
	! Page title !! User !! Revision timestamp !! Diff""")

	iz = 0
	for x in data:
		if iz <= 25:
			dt = datetime.fromtimestamp(mktime(x['timestamp']))
			l.append("\n|-\n| " + """<span class="plainlinks">[//""" + wiki + "/wiki/" + x['title'].replace(" ","_") + " " + x['title'] + "]</span>" + """ || <span class="plainlinks">[//""" + wiki + "/wiki/User:" + x['user'].replace(" ","_") + " " + x['user'] + "]</span> || " + str(dt) + " || " + "[//" + wiki + "/w/index.php?diff=prev&oldid=" + str(x['revid']) + " diff]")
			iz = iz + 1
		else:
			continue

	l.append("\n|}")

wikis = ['en.wikipedia.org',
'en.wikiquote.org',
'en.wikivoyage.org',
'es.wikivoyage.org',
'fr.wikivoyage.org',
'he.wikisource.org', 
'simple.wikipedia.org', 
'sa.wikipedia.org',
'wikisource.org', 
'sv.wikivoyage.org',
'test2.wikipedia.org', 
'test.wikipedia.org', 
'tt.wiktionary.org']

for wiki in wikis:
	generate(wiki)

text = unicode(u''.join(l))

site2 = mwclient.Site('en.wikipedia.org')
site2.login(settings.username, settings.password)
page = site2.Pages['User:RileyBot/watchlist']
page.save(text,"[[User:RileyBot|Bot]]: Updating global watchlist")
log('Global watchlist updated')
prog_end()
