import mwclient
import mwparserfromhell
from theobot import bot
from theobot import password

# CC-BY-SA Theopolisme
# Task 4 on [[User:Theo's Little Bot]]

# Defining list.
pages = []

def cats_recursive(category):
	"""Recursively goes through
	categories. Almost TOO
	straightforward.
	"""
	for item in category:
		if "Category" in str(item):
			cats_recursive(item)
		else:
			x = item.page_title
			pages.append(x)

def editor(text):
	"""This function does the bulk of the
	work. Requires one parameter, text.
	"""
	code_compare = mwparserfromhell.parse(text)
	code = mwparserfromhell.parse(text)
	for template in code.filter_templates():
		if template.name in ('WP Australia', 'WP Australian music', 'WPAUS', 'WPAUSTRALIA', 'WPAustralia', 'WikiProject Australia') and not template.has_param("road"):
			template.add("road", "yes")
			print "Road value added."
		if template.name in ('WP Australia', 'WP Australian music', 'WPAUS', 'WPAUSTRALIA', 'WPAustralia', 'WikiProject Australia') and not template.has_param("road-importance"):
			try:
				xyz = template.get("importance").value
				template.add("road-importance", xyz)
				print "Road-importance value added."
			except:
				print "No importance to add."
		if template.name == 'WikiProjectBannerShell':
			x = template.get(1).value
			for template in x.filter_templates():
				if template.name in ('WP Australia', 'WP Australian music', 'WPAUS', 'WPAUSTRALIA', 'WPAustralia', 'WikiProject Australia') and not template.has_param("road"):
					template.add("road", "yes")
					print "Road value added."
				if template.name in ('WP Australia', 'WP Australian music', 'WPAUS', 'WPAUSTRALIA', 'WPAustralia', 'WikiProject Australia') and not template.has_param("road-importance"):
					try:
						xyz = template.get("importance").value
						template.add("road-importance", xyz)
						print "Road-importance value added."
					except:
						print "No importance to add."
	
	if code == code_compare:
		text = "{{WikiProject Australia|road=yes}}" + text
	else:
		text = unicode(code)
	
	return text	

def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)


	zam = mwclient.listing.Category(site, 'Category:Roads in Australia')
	cats_recursive(zam)

	print "Working on " + str(len(pages)) + " pages."

	for page in pages:
		talk = u'Talk:' + page
		page = site.Pages[talk]
		text = page.edit()
		y = editor(text)
		page.save(y, summary = "Adding road parameter to {{[[Template:WikiProject Australia|WikiProject Australia]]}} - testing script")
		print talk + " saved."
		
if __name__ == '__main__':
   main()