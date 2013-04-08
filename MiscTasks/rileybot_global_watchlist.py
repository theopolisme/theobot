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
	global logs
	final = ''.join(logs)
	site2 = mwclient.Site('en.wikipedia.org')
	log_page = site2.Pages['User:RileyBot/Logs/Watchlist']
	log_text = log_page.edit() + final
	log_page.save(log_text,'[[User:RileyBot|Bot]]: Uploading logs for [[User:RileyBot/Watchlist|watchlist]]')
	sys.exit(0)
	
def generate(wiki):
	print "Working on " + wiki
	log('Working on' + wiki)
	site1 = mwclient.Site(wiki)
	site1.login(settings.username, settings.password)
	data = site1.watchlist(prop="ids|timestamp|title")
	page3 = site1.Pages['User:RileyBot/Stop']
	text3 = page3.edit()
	if text3.lower() != u'enable':
		log('Check page disabled')
		prog_end()
	else:
		print data
	
		global l
		l.append("\n=== " + wiki + " ===")
	
		l.append("""\n{| class="wikitable sortable"
		|-
		! Page title !! Revision timestamp !! Diff""")
	
		iz = 0
		for x in data:
			if iz <= 25:
				dt = datetime.fromtimestamp(mktime(x['timestamp']))
				l.append("\n|-\n| " + """<span class="plainlinks">[//""" + wiki + "/wiki/" + x['title'].replace(" ","_") + " " + x['title'] + "]</span> || " + str(dt) + " || " + "[//" + wiki + "/w/index.php?diff=prev&oldid=" + str(x['revid']) + " diff]")
				iz = iz + 1
			else:
					print "That's all for now!"
	
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

final = ''.join(l)

site2.login(settings.username, settings.password)

page = site2.Pages['User:RileyBot/watchlist']
page.save(final,"[[User:RileyBot|Bot]]: Updating global watchlist")
log('Global watchlist updated')
prog_end()
