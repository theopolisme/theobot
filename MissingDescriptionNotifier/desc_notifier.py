import mwclient, re, sys, datetime, pickle
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme
# Task 2 on [[User:Theo's Little Bot]]

def sokay(donenow):
	"""This function calls a subfunction
	of the theobot module, checkpage().
	"""
	if donenow % 5 == 0:
		if bot.checkpage("User:Theo's Little Bot/disable/desc_notifier") == True:
			return True
		else:
			return False
	else:
		return True

def are_you_still_there(theimage):
	""" This function makes sure that
	a given image is still tagged with
	{{description missing}}.
	"""
	img_name = "File:" + theimage
			
	page = site.Pages[img_name]
	text = page.edit()
	
	regexp1 = re.compile(r'\{\{[Dd]escription missing.*\}\}')
	regexp2 = re.compile(r'\{\{[Dd]esc missing.*\}\}')
	regexp3 = re.compile(r'\{\{[Mm]issing description.*\}\}')
	regexp4 = re.compile(r'\{\{[Ff]ile description.*\}\}')

	if regexp1.search(text) is not None:
		return True
	elif regexp2.search(text) is not None:
		return True
	elif regexp3.search(text) is not None:
		return True
	elif regexp4.search(text) is not None:
		return True
	else:
		return False

def notified_already(user):
	""" This function makes sure that
	a user doesn't currently have a notification
	waiting on their talk page. Returns TRUE
	if user hasn't been notified.
	"""
	usertalk = 'User talk:' + user
			
	page = site.Pages[usertalk]
	text = page.edit()
	
	regexp1 = re.compile(r'<!-- Template:Add-desc-I -->')
	regexp2 = re.compile(r'<!-- Template:Add-desc -->')

	if regexp1.search(text) is None and regexp2.search(text) is None:
		return True
	else:
		return False

def were_they_told_in_three(user):
	"""This checks if the user has been
	already notified in the past three
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
	if (now - xyz) > datetime.timedelta(days=3):
		print "Time greater than 3 days, so we can renotify."
		return False
	else:
		print "User already notified in 3 days."
		return True

def notify(user):
	"""The function checks that a number of
	conditions are true, then notifies the user
	in question. Calls generate_subst().
	"""
	usertalk = 'User talk:' + user
	if were_they_told_in_three(user) == False:
		if bot.nobots(page=usertalk) == True:
			print "We're cleared to edit."
			if notified_already(user) == True:
				print "User hasn't already been notified!"
				page = site.Pages[usertalk]
				text = page.edit()
				text = text + generate_subst(user)
				page.save(text, summary = "Notifying user about missing file description(s) ([[WP:BOT|bot]] on trial)")
				global total_done_now
				total_done_now = total_done_now + 1
				global users_notfied
				users_notified.append(user)
				now123 = datetime.datetime.utcnow()
				users_notified.append(now123)
				print user.encode('ascii', 'ignore') + " notified"
			else:
				print "User was notifed already."
		else:
			print "Bot denied!"
	else:
		print "User has already been notified in past 3 days."


def add_to_dict(user,file):
	"""The function adds an item to a list in a dictionary
	with user as the key.
	"""
	
	if user not in to_notify:
		f_l = []
		f_l.append(file)
		global to_notify
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
	subst = u'\n{{subst:add-desc-I'
	for file in files:
		subst = subst + u'|' + file
	subst = subst + u'}}'
	return subst
	
def main():
	"""This defines and fills a global
	variable for the site, and then runs.
	"""
	print "Logging in as " + password.username + "..."
	
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)
	
	global picklefile
	picklefile = open("users_notified.txt", 'r')
	print picklefile
		
	try:
		global users_notified
		users_notified = pickle.load(picklefile)
	except (EOFError):
		print "Pickle file was empty...we'll have to make do!"
		users_notified = []
	
	global to_notify
	to_notify = {}
	
	picklefile.close()

	global picklefile_write
	picklefile_write = open("users_notified.txt", 'w')

	files = bot.what_transcludes(['Description missing'])

	global total_done_now
	total_done_now = 0
	
	for file in files:
		#print "Working on " + str(file)
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

main()