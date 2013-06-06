#! /usr/bin/env python

from __future__ import unicode_literals
import mwclient
from theobot import password
import urllib2
import datetime
import re
import time

# CC-BY-SA Theopolisme

class WDL(object):
	"""This represents one WDL object, both
	on-wiki and on the WDL site.
	"""
	def __init__(self, id):
		self.id = id
		self.date = datetime.datetime.now().strftime("%d %B %Y")
		self._get_web_details()
	
	def generate_cite_web_wrapper(self):
		citation = unicode("""{{{{cite web
|title={name}
|url={url}
|website=[[World Digital Library]]
|date={date}
|accessdate={accessdate}""".format(name=self.details['name'],url=self.url,date=self.details['date'],accessdate=self.date))
		
		if self.details['language'] != "English":
			citation += """\n|language={0}""".format(self.details['language'])

		if self.details['location'] !=  "":
			citation += """\n|location={0}""".format(self.details['location'])
		
		current_author_num = 0
		for creator in self.details['creators']:
			creator = creator.decode('ascii', 'replace')
			creator = re.sub(r"""(,\s*\d*-\d*|\(\d*-\d*\)|\s*\(.*?\d*.*?\)|,\s(born|died|circa)[\s\d\D]*)""", "", creator)
			current_author_num += 1
			citation += """\n|author{current_author_num}={creator}""".format(current_author_num=current_author_num,creator=creator)
		citation += """\n}}"""
		return citation

	def update(self):
		"""If it was the last one to edit the citation page
		(or if it was never updated), updates it."""
		page = site.Pages["Template:Cite wdl/{0}".format(self.id)]
		
		if page.exists == True:
			z = site.api(action='query',prop='revisions',rvprod='user',revids=page.revision)
			for pageid in z['query']['pages'].items():
				user = z['query']['pages'][unicode(pageid[0])]['revisions'][0]['user']
		else:
			user = u"Theo's Little Bot"

		if user == u"Theo's Little Bot" or u"Theopolisme":
			page.save(self.generate_cite_web_wrapper(),summary="[[WP:BOT|Bot]]: Expanding World Digital Library citation")
		else:
			print "Citation page for {0} was edited by someone other than me; must have been created manually.".format(self.id)

	def _get_web_details(self):
		"""Given self.id, scrapes data from
		wdl.com and wraps it up in a dictionary.
		"""
		self.url = "http://www.wdl.org/en/item/" + str(self.id) + "/"	
		text = urllib2.urlopen(self.url).read()
		details = {}
		details['name'] = re.search(r"""<span class="item_title" itemprop="name">(.*?)</span></h1>""", text, flags=re.DOTALL | re.UNICODE).groups(0)[0]
		details['date'] = re.search(r"""<meta name="dc.date" content="(.*?)">""", text, flags=re.DOTALL | re.UNICODE).groups(0)[0]
		
		try:
			details['language'] = re.search(r"""<meta itemprop="inLanguage" content=".*?"><a href="/en/search/\?languages=.*?">(.*?)</a></li>""", text, flags=re.DOTALL | re.UNICODE).groups(0)[0]
		except AttributeError:
			details['language'] = "English"
		try:
			details['creators'] = re.findall(r"""<li itemprop="creator" itemscope itemtype="http://schema.org/Person">\s*<meta itemprop="additionalType" content="http://viaf.org/viaf/">\s*<a href=".*?"><span itemprop="name">(.*?)</span></a>\s*</li>""", text, flags=re.DOTALL | re.UNICODE | re.M)
		except AttributeError:
			details['creators'] = [] # in case we return nothing			
		try:
			country = re.search(r"""&gt; <a href=".*?"><span itemprop="addressCountry">(.*?)</span></a>\s*&gt;""", text, flags=re.DOTALL | re.UNICODE | re.M).groups(0)[0]
		except AttributeError:
			country = None
		try:	
			region = re.search(r"""&gt; <a href=".*?"><span itemprop="addressRegion">(.*?)</span></a>\s*""", text, flags=re.DOTALL | re.UNICODE | re.M).groups(0)[0]
		except AttributeError:
			region = None
		try:
			locality = re.search(r"""<a href=".*?"><span itemprop="addressLocality">(.*?)</span></a>""", text, flags=re.DOTALL | re.UNICODE | re.M).groups(0)[0]
		except AttributeError:
			locality = None
		
		if country:
			country_data_all = ", [[{0}]]".format(country) if country != "United States of America" else ""
			country_data_else= "[[{0}]]".format(country) if country != "United States of America" else ""
		
		if locality and region and country != None:
			details['location'] = "[[{city}, {state}|{city}]], [[{state}]]{country}".format(city=locality,state = region,country=country_data_all)
		elif locality and region != None and country == None:
			details['location'] = "[[{city}, {state}|{city}]], [[{state}]]".format(city=locality,state = region)			
		elif region and country != None and locality == None:
			details['location'] = "[[{state}]], {country}".format(state=region,country=country_data_else)			
		elif locality != None and region and country  == None:
			details['location'] = "[[{city}]]".format(city=locality)
		elif region != None and locality and country  == None:
			details['location'] = "[[{state}]]".format(city=region)
		elif country != None and locality and region  == None:
			details['location'] = "{country}".format(country=country_data_else)
		else:
			details['location'] = ""
		
		self.details = details

def process_page(page):
	contents = page.edit()
	ids = re.findall(r"""{{cite wdl\|(.*?)}}""", contents, flags=re.DOTALL | re.UNICODE | re.IGNORECASE)
	for id in ids:
		print "Working on id #{0}".format(id)
		this_wdl = WDL(id)
		this_wdl.update()

def get_pages():
	"""Uses a maintenance category on wikipedia to 
	get a list of pages and then processes them.
	"""
	print "Getting pages to process..."
	cat = mwclient.listing.Category(site, 'Category:Pages with incomplete WDL citations')
	for page in cat:
		process_page(page)

print "Powered on."
global site
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

while 1:
	get_pages()
	time.sleep(60)
	print "Running again!"