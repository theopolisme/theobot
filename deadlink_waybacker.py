#! /usr/bin/env python
from __future__ import unicode_literals
import mwclient
import mwparserfromhell
import requests
import re
import sys
import difflib
from datetime import datetime
from dateutil import parser
#from theobot import password

# CC-BY-SA Theopolisme

class DeadLinkBot(object):
	"""This is the bot itself."""

	def __init__(self,dryrun=False,verbose=False):
		print "We're running!"
		self.DRYRUN = dryrun
		self.VERBOSE = verbose
		self.deadlink_templates = ('{{dl','{{deadlink','{{404','{{broken link','{{brokenlink','{{linkbroken','{{link broken','{{dead links','{{deadlinks','{{badlink','{{dead','{{dl','{{dead page','{{dead-link','{{dead link','{{dead url','{{dead cite','{{deadcite')
		self.deadlink_names = ('dl','deadlink','404','broken link','brokenlink','linkbroken','link broken','dead links','deadlinks','badlink','dead','dl','dead page','dead-link','dead link','dead url','dead cite','deadcite')

	def run(self):
		category = mwclient.listing.Category(site, 'Category:All articles with dead external links')
		for page in category:
			dead_refs = []
			print page.page_title
			orig_contents = page.edit()
			contents = page.edit()
			number_done = 0
			all_refs = re.findall(r"""<ref[^>]*>.*?</ref>""",contents,flags=re.UNICODE | re.IGNORECASE)
			for ref in all_refs:
				ref_lower = ref.lower()
				if  any(name in ref_lower for name in self.deadlink_templates):
					dead_refs.append(ref)
			for ref in dead_refs:
				ref_code = mwparserfromhell.parse(ref)
				updated = False
				for template in ref_code.filter_templates():
					if "cite web" in template.name and template.has_param('archiveurl') == False:
						url = unicode(template.get('url').value.strip())
						if requests.get(url).status_code != requests.codes.ok:
							if template.has_param('accessdate'):
								accessdate = parser.parse(str(template.get('accessdate').value))
								wayback_date = accessdate.strftime("%Y%m%d%H%M%S")
								r = requests.get("http://web.archive.org/web/{date}/{url}".format(date=wayback_date,url=url)) 
							else:
								r = requests.get("http://web.archive.org/web/form-submit.jsp", params={'url':url, 'type':'replay'})
							print r.url
							print r.status_code
							if r.status_code == requests.codes.ok:
								number_done += 1
								updated = True
								wayback_url = r.url
								wayback_date_object = datetime.strptime(wayback_url.split('/')[4],"%Y%m%d%H%M%S")
								wayback_date = wayback_date_object.strftime('%d %B %Y')
								template.add('archiveurl',wayback_url)
								template.add('archivedate',wayback_date)
							else:
								print "{url} not archived in wayback machine.".format(url=url)
								continue # this url was not archived by the wayback machine; nothing we can do here.
						else:
							print "No need to add an archive, since the citations's URL currently works!"
				for template in ref_code.filter_templates():
					nameoftemp = template.name.lower()
					if any(name in nameoftemp for name in self.deadlink_names) and updated == True:
						ref_code.remove(template)
				if updated == True:
					new_ref = unicode(ref_code)
					contents = re.sub(re.escape(ref),new_ref,contents,flags=re.U)
				else:
					pass
			if self.DRYRUN == False and number_done > 0:
				page.save(contents,summary="Adding archiveurl for {0} dead link{1}".format(number_done,'s' if number_done > 1 else ''))
				print "{0} saved!".format(page.page_title)
			elif self.DRYRUN == True and self.VERBOSE == True:
				diff = difflib.unified_diff(orig_contents.splitlines(), contents.splitlines())
				print '\n'.join(diff)

# Logs in to the site.
global site
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

the_bot = DeadLinkBot(dryrun=False,verbose=False)
the_bot.run()