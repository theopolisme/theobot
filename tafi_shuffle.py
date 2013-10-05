#! /usr/bin/env python
from __future__ import unicode_literals
import mwclient
import mwparserfromhell
import random
import re
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme

global site
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

page = site.Pages["Wikipedia:Today's articles for improvement/Nominated articles"]
text = page.edit()
header,noms = text.split('<!-- BEGIN SECTIONS (for bot, please do not remove this line) -->',1)

def process_section(section):
	text = unicode(section)
	if re.sub(r'\s*==.*?==\s*','',text,flags=re.U) == '':
		text += '\n{{subst:dated|empty section}}'
	return text

code = mwparserfromhell.parse(noms)
hellsections = code.get_sections()
sections = [process_section(section) for section in hellsections]

random.shuffle(sections)
while sections[0].find('empty section') != -1:
	# So we don't have an empty section at the top
	random.shuffle(sections)

output = header + '<!-- BEGIN SECTIONS (for bot, please do not remove this line) -->\n\n' + '\n\n'.join(sections)
output = re.sub(r'(?:[\t ]*(?:\r?\n|\r)){3,}','\n\n',output,flags=re.U)

page.save(output,'[[WP:BOT|Bot]]: Reshuffling TAFI sections')
