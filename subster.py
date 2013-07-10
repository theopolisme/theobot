#! /usr/bin/env python
from __future__ import unicode_literals

import mwclient
import mwparserfromhell

import re

from theobot import bot
from theobot import password

import difflib

# CC-BY-SA Theopolisme

# EDIT THIS
SUBST_ME = 'Infobox Unternehmen'


OLD = r"""\{\{"""+SUBST_ME.replace(" ",r"[_ ]")
NEW = "{{subst:"+SUBST_ME

print OLD,NEW

site = mwclient.Site('en.wikipedia.org')
site.login(password.main_username,password.main_password)

for page in bot.what_transcludes(SUBST_ME):
	contents = page.edit()
	newtext = re.sub(OLD,NEW,contents)
	if contents != newtext:
		diff = difflib.unified_diff(contents.splitlines(), newtext.splitlines(), lineterm='')
		print '\n'.join(list(diff))
		choice = raw_input("[s]ave page or [p]ass?").strip().lower()
		if choice == "s":
			page.save(newtext,"Substituting [[Template:Infobox Unternehmen]] (assisted)")
		else:
			print "Skipped edit."
	else:
		pass # there were no modifications

