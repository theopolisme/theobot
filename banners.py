from __future__ import unicode_literals

import re
import json

import mwclient

from theobot import password
from theobot import bot

# Saves a dictionary of WikiProject names and their associated banners to a javascript file on-wiki for AFCH
# CC-BY-SA Theopolisme

def get_project(template):
	"""Given a WikiProject template mwclient.Page object, get the
	title of the project, or None if no title could be found
	"""
	text = template.edit()
	projectmatch = re.search(r'\|\s*PROJECT\s*=\s*(.*)[\n\r]',text,flags=re.U | re.I)
	if projectmatch is not None:
		project = projectmatch.groups(1)[0].replace("WikiProject","").strip()
	else:
		project = None
	return project

def main():
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)

	templates = {}
	cat = mwclient.listing.Category(site,'Category:WikiProject banners with quality assessment')
	for template in bot.listpages(cat,names=False,includeredirects=False):
		if template.page_title.find('/testcases') == -1 and template.page_title.find('/sandbox') == -1:
			print "working on {}".format(template.page_title)
			templates[get_project(template) or template.page_title] = template.page_title
		else:
			pass

	output = """// WikiProject banner templates and their associated WikiProjects
// afcHelper_wikiprojectindex['associated wikiproject name'] = 'template name without namespace'
afcHelper_wikiprojectindex = """

	output += json.dumps(templates,sort_keys=True,indent=4,separators=(',', ': '))

	outputpage = site.Pages["User:Theo's Little Bot/afchwikiproject.js"]
	outputpage.save(output,summary="[[WP:BOT|Bot]]: Updating WikiProject index for [[WP:AFCH|]]")

if __name__ == '__main__':
	main()
