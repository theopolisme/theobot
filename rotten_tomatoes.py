#! /usr/bin/env python

from __future__ import unicode_literals
import datetime
import re

import mwclient
import requests
import mwparserfromhell

from theobot import password
from theobot import bot

# CC-BY-SA Theopolisme

global TODAY
TODAY = datetime.datetime.now().strftime("%d %B %Y")

class RotTomMovie():
	def __init__(self,movie):
		self.movie = movie
		self.results = {}
		self.page = site.Pages[u'Template:Rotten Tomatoes score/'+movie]
		self.collect_data_api()

	def collect_data_api(self):
		"""Uses the Rotten Tomatoes API to fetch data.
		This also starts up a bunch of other functions.
		"""
		payload = {'apikey':password.rottentomkey,'q':self.movie.replace('_',' '),'page_limit':1}
		r = requests.get('http://api.rottentomatoes.com/api/public/v1.0/movies.json', params=payload)
		jsonresults = r.json()
		try:
			self.url = jsonresults['movies'][0]['links']['alternate']
			if self.url.find(self.movie) != -1:
				ratings = jsonresults['movies'][0]["ratings"]
				self.results['tomatometer'] = ratings["critics_score"]
				self.collect_data_scraper(url=self.url)
				self.citation_generation(title=jsonresults['movies'][0]['title'],year=jsonresults['movies'][0]['year'],url=self.url)
				self.all_in_one()
				self.wikipage_output()
			else:
				print "Drat, wrong movie. ABORT!"
				self.page.save("{{error|The bot could not process this Rotten Tomatoes listing. Please [[User talk:Theopolisme|contact its operator]].",summary="[[WP:BOT|Bot]]: Updating Rotten Tomatoes data")
		except:
			print "There were no movies matching this title...ABORT!"
			self.page.save("{{error|There are no listings on Rotten Tomatoes for this title. Questions? [[User talk:Theopolisme|Contact Theopolisme]].",summary="[[WP:BOT|Bot]]: Updating Rotten Tomatoes data")

	def collect_data_scraper(self,url):
		"""This uses some good old-fashioned web scraping to get the date we're after."""
		r = requests.get(url)
		contents = r.text
		self.results['average_rating'] = re.findall(r"Average Rating: <span>(.*?)</span><br />",contents,flags=re.U|re.DOTALL)[0]
		self.results['number_of_reviews'] = re.findall(r"""Reviews Counted: <span itemprop="reviewCount">(.*?)</span><br />""",contents,flags=re.U|re.DOTALL)[0]

	def citation_generation(self,title,year,url):
		"""Creates a citation using the data."""
		self.results['citation'] = """{{{{cite web
|title={title} ({year})
|url={url}
|publisher=Rotten Tomatoes
|accessdate={date}
}}}}""".format(title=title,year=year,url=url,date=TODAY)

	def all_in_one(self):
		"""Wraps up all of the items in self.results in a pretty package."""
		self.results['all_in_one'] = 'The [[review aggregator]] website [[Rotten Tomatoes]] reported a {0}% approval rating with an average rating of {1} based on {2} reviews.<includeonly><ref>{3}</ref></includeonly>'.format(self.results['tomatometer'],self.results['average_rating'],self.results['number_of_reviews'],self.results['citation'])

	def wikipage_output(self):
		"""Updates the on-wiki template for this particular film."""
		contents = """{{#ifeq: {{{1|}}} |tomatometer|""" + unicode(self.results['tomatometer']) + """|}}<!--
-->{{#ifeq: {{{1|}}} |citation|""" + self.results['citation'] + """|}}<!--
-->{{#ifeq: {{{1|}}} |average_rating|""" + unicode(self.results['average_rating']) + """|}}<!--
-->{{#ifeq: {{{1|}}} |number_of_reviews|""" + unicode(self.results['number_of_reviews']) + """|}}<!--
-->{{#ifeq: {{{1|}}} |all_in_one|""" + self.results['all_in_one']  + """|}}"""
		self.page.save(contents,"[[WP:BOT|Bot]]: Updating Rotten Tomatoes data")

def process_page(page):
	contents = page.edit()
	wikicode = mwparserfromhell.parse(contents)
	for template in wikicode.filter_templates():
		if "rotten tomatoes score" in template.name.lower().strip():
			movie = unicode(template.get(1).value)
			RotTomMovie(movie=movie)

def get_pages():
	"""Uses a maintenance category on wikipedia to 
	get a list of pages and then processes them.
	"""
	print "Getting pages to process..."
	cat = mwclient.listing.Category(site, 'Category:Pages with incomplete Rotten Tomatoes embeds')
	for page in cat:
		process_page(page)

print "Powered on."
global site
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

if __name__ == '__main__':
	get_pages()
