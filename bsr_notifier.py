#! /usr/bin/env python
import mwclient
import re
import sys
import datetime
import pickle
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme
# Task 9 on [[User:Theo's Little Bot]]

def sokay(donenow):
	"""This function calls a subfunction
	of the theobot module, checkpage().
	"""
	
	if donenow % 5 == 0:
		if bot.checkpage("User:Theo's Little Bot/disable/bsr") == True:
			return True
		else:
			return False
	else:
		return True

def notified_already(user):
	""" This function makes sure that
	a user doesn't currently have a notification
	waiting on their talk page. Returns TRUE
	if user hasn't been notified.
	"""
	usertalk = 'User talk:' + user
			
	page = site.Pages[usertalk]
	text = page.edit()

	if text.find('It is best to specify the exact Web page where you found the image') == -1 and text.find('<!-- Template:Bsr-user -->') == -1:
		return True
	else:
		return False

def already_told(user):
	"""This checks if the user has been
	already notified in the past twenty
	days.
	"""
	now = datetime.datetime.now()
	try:
		lop = users_notified.index(user)
	except (ValueError):
		print "User was not in list!"
		return False
	lop = lop + 1
	xyz = users_notified[lop]
	if (now - xyz) > datetime.timedelta(days=20):
		print "Time greater than 20 days, so we can renotify."
		return False
	else:
		print "User already notified in the last 20 days."
		return True

def notify(user):
	"""The function checks that a number of
	conditions are true, then notifies the user
	in question. Calls generate_subst().
	"""
	usertalk = 'User talk:' + user
	if already_told(user) == False:
		if bot.nobots(page=usertalk,task='bsr') == True:
			print "We're cleared to edit."
			if notified_already(user) == True:
				print "User hasn't already been notified!"
				page = site.Pages[usertalk]
				text = page.edit()
				text = text + generate_subst(user)
				#text = generate_subst(user)
				try:
					page.save(text,summary="Notifying user about file(s) with inadequate source information ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/bsr|disable]])")
					global total_done_now
					total_done_now = total_done_now + 1
					global users_notfied
					users_notified.append(user)
					now123 = datetime.datetime.utcnow()
					users_notified.append(now123)
					print user.encode('ascii', 'ignore') + " notified."
				except:
					print "Unknown error // skipping " + user.encode('ascii', 'ignore') + "."
			else:
				print "User was notifed already."
		else:
			print "Bot denied!"
	else:
		print "User has already been notified in past 7 days."


def add_to_dict(user,file):
	"""The function adds an item to a list in a dictionary
	with user as the key.
	"""
	
	global to_notify

	if user not in to_notify:
		f_l = []
		f_l.append(file)	
		to_notify[user] = f_l
	else:
		f_l = to_notify[user]
		f_l.append(file)
		to_notify[user] = f_l
		
def generate_subst(user):
	"""This function creates the
	wikicode for the substituted
	template, by appending text to
	a base string.
	"""
	files = to_notify[user]
	subst = u'\n{{subst:Bsr-user'
	for file in files:
		subst = subst + u'|' + file
	subst = subst + u'}} ~~~~'
	return subst
	
def main():
	"""This defines and fills a global
	variable for the site, and then runs.
	"""
	print "Logging in as " + password.username + "..."
	
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)
	
	try:
		global picklefile
		picklefile = open("bsr_notified.txt", 'r')
		print picklefile
		global users_notified
		users_notified = pickle.load(picklefile)
		picklefile.close()
	except (EOFError, IOError, NameError):
		print "Pickle file was empty...we'll have to make do!"
		users_notified = []

	global to_notify
	to_notify = {}
	

	global picklefile_write
	picklefile_write = open("bsr_notified.txt", 'w')

	files = bot.what_transcludes('Bsr')
	
	
	global total_done_now
	total_done_now = 0
	
	for file in files:
		x = site.images[file]
	
		zam = x.revisions(dir='newer',prop='user')
		try:
			rrev = zam.next()
		except:
			print file.encode('ascii', 'ignore') + " skipped!"
			continue

		zammy = rrev['user']
	
		print "Adding " + file.encode('ascii', 'ignore') + " to " + zammy.encode('ascii', 'ignore') + "'s list now."
		add_to_dict(zammy,file)

	print "Now, let's run through those lists."
	
	donenow = 5
	
	for key in to_notify:
		if sokay(donenow) == True:
			notify(key)
			donenow = donenow + 1
		elif sokay(donenow) == False:
			pickle.dump(users_notified, picklefile_write)
			sys.exit()
	
	print "All done, pickling."
	pickle.dump(users_notified, picklefile_write)
	print "Pickled!"

if __name__ == '__main__':
   main()