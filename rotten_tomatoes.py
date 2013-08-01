#! /usr/bin/env python

from __future__ import unicode_literals
import datetime
import time
import pickle
import re
import hashlib
import HTMLParser

import mwclient
import requests
import mwparserfromhell

from theobot import password
from theobot import bot

# CC-BY-SA Theopolisme

global TODAY
TODAY = datetime.datetime.now().strftime("%d %B %Y")

global NONDECIMAL
NONDECIMAL = re.compile(r'[^\d.]+',flags=re.U)

global HPARSER
HPARSER = HTMLParser.HTMLParser()

global UPDATED_SCORES
try:
	UPDATED_SCORES = pickle.load(open("rotten_tomatoes_scores.p","rb"))
except IOError:
	print "The score pickle didn't exist, so starting 'fresh'...haha, get it? ...<crickets>"
	UPDATED_SCORES = {}

global UPDATED_IDS
try:
	UPDATED_IDS = pickle.load(open("rotten_tomatoes_updated.p","rb"))
except IOError:
	print "The last-updated pickle didn't exist, so starting 'fresh'...haha, get it? ...<crickets>"
	UPDATED_IDS = {}

class RotTomMovie():
	def __init__(self,imdbid):
		self.imdbid = imdbid
		self.results = {}
		self.page = site.Pages[u'Template:Rotten Tomatoes score/'+imdbid]
		self.collect_data_api()

	def collect_data_api(self):
		"""Uses the Rotten Tomatoes API to fetch data.
		This also starts up a bunch of other functions.
		"""
		ok_id = NONDECIMAL.sub('',self.imdbid)
		payload = {'apikey':password.rottentomkey,'id':ok_id,'type':'imdb'}
		r = requests.get('http://api.rottentomatoes.com/api/public/v1.0/movie_alias.json', params=payload)
		jsonresults = r.json()
		try:
			self.title = jsonresults['title']
			self.url = jsonresults['links']['alternate']
			ratings = jsonresults["ratings"]
			self.results['tomatometer'] = ratings["critics_score"]
			self.collect_data_scraper(url=self.url)
			self.citation_generation(title=self.title,year=jsonresults['year'],url=self.url)
			self.all_in_one()
			ok = False
			sc_hash = hashlib.md5(repr(self.results)).hexdigest()
			try:
				if sc_hash != UPDATED_SCORES[self.imdbid]:
					UPDATED_SCORES[self.imdbid] = sc_hash
					ok = True
				else:
					print "The scores haven't changed, so not updating."
			except KeyError:
				print "This is the first time we've processed this movie."
				UPDATED_SCORES[self.imdbid] = sc_hash
				ok = True
			if ok == True:
				self.wikipage_output()
		except:
			print "There were no movies matching this title...ABORT!"
			self.page.save("{{error|There are no listings on Rotten Tomatoes for this title. Questions? [[User talk:Theopolisme|Contact Theopolisme]].}}",summary="[[WP:BOT|Bot]]: Updating Rotten Tomatoes data")

	def collect_data_scraper(self,url):
		"""This uses some good old-fashioned web scraping to get the date we're after."""
		r = requests.get(url)
		contents = r.text

		try:
			self.results['average_rating'] = re.findall(r"Average Rating: <span>(.*?)</span><br />",contents,flags=re.U|re.DOTALL)[0]
		except:
			self.results['average_rating'] = 0
		try:
			self.results['number_of_reviews'] = re.findall(r"""Reviews Counted: <span itemprop="reviewCount">(.*?)</span><br />""",contents,flags=re.U|re.DOTALL)[0]
		except:
			self.results['number_of_reviews'] = 0

		try:
			self.results['fresh'],self.results['rotten'] = re.findall(r"""Fresh: (\d*) \| Rotten: (\d*)""",contents,flags=re.U|re.DOTALL)[0]
		except:
			self.results['fresh'],self.results['rotten'] = 0,0

		try:
			consensus = re.findall(r"""<p class="critic_consensus">(.*?)</p>""",contents,flags=re.U|re.DOTALL)[0].strip()
			consensus = HPARSER.unescape(consensus).replace(self.title,"''"+self.title+"''")
		except:
			consensus = ''
		if consensus.find('No consensus yet.') != -1 or len(consensus) == 0:
			self.results['consensus'] = 'No consensus yet.'
		else:
			self.results['consensus'] = consensus

	def citation_generation(self,title,year,url):
		"""Creates a citation using the data."""
		self.results['citation'] = """{{{{cite web
|title={title} ({year})
|url={url}
|publisher=Rotten Tomatoes
|accessdate={date}
}}}}""".format(title=title,year=year,url=url,date=TODAY)

	def all_in_one(self):
		"""Wraps up all of the items in self.results in pretty packaging."""
		self.results['all_in_one'] = 'The [[review aggregator]] website [[Rotten Tomatoes]] reported a {0}% approval rating with an average rating of {1} based on {2} reviews.<includeonly><ref>{3}</ref></includeonly>'.format(self.results['tomatometer'],self.results['average_rating'],self.results['number_of_reviews'],self.results['citation'])
		if self.results['consensus'] != 'No consensus yet.':
			self.results['all_in_one_plus_consensus'] = 'The [[review aggregator]] website [[Rotten Tomatoes]] reported a {0}% approval rating with an average rating of {1} based on {2} reviews. The website\'s consensus reads, "{3}"<includeonly><ref>{4}</ref></includeonly>'.format(self.results['tomatometer'],self.results['average_rating'],self.results['number_of_reviews'],self.results['consensus'],self.results['citation'])
		else:
			self.results['all_in_one_plus_consensus'] = "{{error|There was no consensus data on Rotten Tomatoes for this title. Questions? [[User talk:Theopolisme|Contact Theopolisme]].}}"

	def wikipage_output(self):
		"""Updates the on-wiki template for this particular film."""
		contents = """{{#ifeq: {{{1|}}} |tomatometer|""" + unicode(self.results['tomatometer']) + """|}}<!--
-->{{#ifeq: {{{1|}}} |citation|""" + self.results['citation'] + """|}}<!--
-->{{#ifeq: {{{1|}}} |average_rating|""" + unicode(self.results['average_rating']) + """|}}<!--
-->{{#ifeq: {{{1|}}} |number_of_reviews|""" + unicode(self.results['number_of_reviews']) + """|}}<!--
-->{{#ifeq: {{{1|}}} |consensus|""" + unicode(self.results['consensus']) + """|}}<!--
-->{{#ifeq: {{{1|}}} |fresh|""" + unicode(self.results['fresh']) + """|}}<!--
-->{{#ifeq: {{{1|}}} |rotten|""" + unicode(self.results['rotten']) + """|}}<!--
-->{{#ifeq: {{{1|}}} |all_in_one_plus_consensus|""" + unicode(self.results['all_in_one_plus_consensus']) + """|}}<!--
-->{{#ifeq: {{{1|}}} |all_in_one|""" + self.results['all_in_one']  + """|}}"""
		self.page.save(contents,"[[WP:BOT|Bot]]: Updating Rotten Tomatoes data")

def process_page(page):
	"""Parse a page for all of its IMDB ids."""
	contents = page.edit()
	wikicode = mwparserfromhell.parse(contents)
	for template in wikicode.filter_templates():
		if "rotten tomatoes score" in template.name.lower().strip():
			try:
				imdbid = unicode(template.get(1).value)
			except ValueError:
				continue # if it doesn't designate an IMDB id, we don't want it
			update_id(imdbid)

def update_id(imdbid):
	"""If the id hasn't been updated in the past 5 days, re-calculate and update
	its information.
	"""
	try:
		if UPDATED_IDS[imdbid] + 432000 < time.time(): # 5 days in seconds
			UPDATED_IDS[imdbid] = time.time()
			RotTomMovie(imdbid=imdbid)
		else:
			print "IMDB id #{} has already been updated in the past 5 days.".format(imdbid)
	except KeyError:
		print "IMDB id #{} wasn't listed in the pickle, so adding it.".format(imdbid)
		UPDATED_IDS[imdbid] = time.time()
		RotTomMovie(imdbid=imdbid)

def main():
	"""Uses a maintenance category on wikipedia to 
	get a list of pages and then processes them.
	"""
	print "Updating articles already using {{Rotten Tomatoes score}}"
	for imdbid in UPDATED_IDS:
		update_id(imdbid)

	print "Processing new articles using {{Rotten Tomatoes score}}"
	cat = mwclient.listing.Category(site, 'Category:Pages with incomplete Rotten Tomatoes embeds')
	for page in cat:
		process_page(page)

	print "And we're done -- pickling!"
	pickle.dump(UPDATED_IDS,open("rotten_tomatoes_updated.p","wb"))
	pickle.dump(UPDATED_SCORES,open("rotten_tomatoes_scores.p","wb"))

print "Powered on."
global site
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

if __name__ == '__main__':
	main()
