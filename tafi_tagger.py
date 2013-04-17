import mwclient
import datetime
import re

# CC-BY-SA Theopolisme

from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme
# Task 7 on [[User:Theo's Little Bot]]

def sokay(donenow):
	"""Simple function to check checkpage.
	This function calls a sub-function
	of the theobot.bot module, checkpage().
	"""
	if donenow % 5 == 0:
		if bot.checkpage("User:Theo's Little Bot/disable/tafi") == True:
			return True
		else:
			return False
	else:
		return True

# Logs in to the site.
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

# Sets the timestamp from which we derive week numbers.
now = datetime.datetime.now()

# This loop adds the tags to the new week's articles.
for i in range(1,11):
	if sokay(i+4) == True:
		stringy = "Wikipedia:Today's articles for improvement/" + str(now.year) + "/" + str(now.isocalendar()[1]) + "/" + str(i)
		editme = site.Pages[stringy].edit()
		pagen = re.findall("\[\[(.*?)\]\]", editme)[0]
		page = site.Pages[pagen]
		try:
			x = re.findall("\{\{TAFI\}\}", page.edit(), flags=re.IGNORECASE)[0]
			print "Page already tagged; skipping."
		except:
			text = u"{{TAFI}}\n" + page.edit()
			print "Saving page " + pagen + " - added TAFI template."
			print text
			page.save(text,summary="Adding [[WP:TAFI|Today's articles for improvement]] tag ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/tafi|disable]])")

# This loop removes the tags from the old week's articles.
for i in range(1,11):
	if sokay(i+4) == True:
		stringy = "Wikipedia:Today's articles for improvement/" + str(now.year) + "/" + str((now.isocalendar()[1])-1) + "/" + str(i)
		editme = site.Pages[stringy].edit()
		pagen = re.findall("\[\[(.*?)\]\]", editme)[0]
		page = site.Pages[pagen]
		text = re.sub(r"\{\{TAFI\}\}", "", page.edit())
		print "Saving page " + pagen + " - removed TAFI template."
		page.save(text,summary="Removing [[WP:TAFI|Today's articles for improvement]] tag ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/tafi|disable]])")

		# This next set of instructions is for tagging the article's talk page.
		start_date = now + datetime.timedelta(-7)
		talk = site.Pages["Talk:" + pagen]
		tt = talk.edit()
		tt = "{{Former TAFI|date=" + start_date.strftime('%B %d, %Y') + "}}\n" + tt
		print tt
		talk.save(tt,summary="Tagging page with {{[[Template:Former TAFI|Former TAFI]]}} ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/tafi|disable]])")
		
