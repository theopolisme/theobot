import mwclient, urllib
from time import mktime
from datetime import datetime
from theobot import password

# CC-BY-SA Theopolisme
# A simple script for a simple friend.
# Tracks [[User:RileyBot]]'s global watchlist

l = []

def generate(wiki):
	print "Working on " + wiki
	site = mwclient.Site(wiki)
	site.login('RileyBot', 'python')

	data = site.watchlist(prop="ids|timestamp|title")
	
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
			l.append("\n|-\n| " + """<span class="plainlinks">[//""" + wiki + "/wiki/" + urllib.quote(x['title']) + " " + x['title'] + "]</span> || " + str(dt) + " || " + "[//" + wiki + "/w/index.php?diff=prev&oldid=" + str(x['revid']) + " diff]")
			iz = iz + 1
		else:
			print "That's all for now!"

	l.append("\n|}")

# @Riley_Huntley - Edit this list of wikis to suit your liking.
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
site = mwclient.Site('en.wikipedia.org')

# @Riley_Huntley - You can change this to log in as your own bot if you'd like.
site.login(password.username, password.password)

page = site.Pages['User:RileyBot/watchlist']
text = page.edit()
text = final
page.save(text, summary = "Bot: Updating global watchlist per request.")
