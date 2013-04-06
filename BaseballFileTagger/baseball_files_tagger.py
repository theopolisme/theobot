import mwclient, re, time, urllib, urllib2
from xml.dom import minidom
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme
# Task 3 on [[User:Theo's Little Bot]]

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)
	
	zam = mwclient.listing.Category(site, "Category:Baseball culture")
	glob = zam.members()
	flub = []
	for file in glob:
		zip = file.page_title
		print zip.encode('ascii', 'ignore')
		flub.append(zip)

	pages_to_search = []
	
	for member in flub:
		"""The reason this loop exists is so we
		can start midway through if interrupted
		for some reason.
		"""
		pages_to_search.append(member)
		
	for thisisapage in pages_to_search:
		page = site.Pages[thisisapage]
		text = page.edit()
		r=re.compile(r'\[\[(File|Image):(.*?\.)(jpg|png|gif|svg|JPG|PNG|GIF|SVG).*?\]\]')
		try:
			l = re.findall(r, text)
		except:
			continue
		for set in l:
			filename = set[1] + set[2]
			print filename.encode('UTF-8', 'ignore')
			pg = "File talk:" + filename
			page = site.Pages[pg]
			xtext = page.edit()
			x = re.compile(r'[Bb]aseball')
			if x.search(xtext) is None:
				xtext = "{{WikiProject Baseball}}\n" + xtext
				page.save(xtext, summary = "Tagging page for [[Wikipedia:WikiProject Baseball|WikiProject Baseball]]")
				print "Page saved!"
				time.sleep(2)
				print "Sleeping two seconds." 
			else:
				print "Page was already tagged; skipping."	
	
main()
