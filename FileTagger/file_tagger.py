import mwclient, re, time, urllib, urllib2
from xml.dom import minidom
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme
# Task 3 on [[User:Theo's Little Bot]]

def tag_files(cat_input,project):
	"""The function requires two parameters,
	"cat_input," a list of categories to get
	pages from, and "project," the WikiProject
	name (as it appears in template to be added
	to the resulting talk pages. For example,
	"WikiProject Baseball" -> {{WikiProject Baseball}}
	"""
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)
	
	for category in cat_input:
		zam = mwclient.listing.Category(site, category)
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
			r = re.compile(r'\[\[(File|Image):(.*?\.)(jpg|png|gif|svg|JPG|PNG|GIF|SVG).*?\]\]')
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
				x = re.compile(project)
				if x.search(xtext, re.IGNORECASE) is None:
					xtext = "{{" + project + "}}\n" + xtext
					page.save(xtext, summary = "Tagging page for [[Wikipedia:" + project + "|" + project + "]]")
					print "Page saved!"
					time.sleep(2)
					print "Sleeping two seconds." 
				else:
					print "Page was already tagged; skipping."	

def main():
	cat_input = []
	project = "WikiProject Baseball"
	
	tag_files(cat_input,project)
	
	print "Run complete!"
	
if __name__ == '__main__':
   main()