import mwclient
from theobot import password

# CC-BY-SA Theopolisme
# Task 8 on [[User:Theo's Little Bot]]

def pages_in_cat(cat):
	cat = mwclient.listing.Category(site, cat)
	x = []
	for item in cat:
		x.append(item.page_title)
	return x

def generate_wikicode(year):
	var = """{{Year nav topic3|""" + year + """|protected areas established}}

This is a list of [[protected area]]s established in """ + year + """.

{| class="wikitable sortable"
|-
! Name
! Country
! data-sort-type="numeric" |Area (ha)
|-"""
	
	cats = pages_in_cat("Category:Protected areas established in " + year)

	for cat in cats:
		var = var + "\n| [[" + cat + """]] ||  ||\n|-"""

	var = var + """\n|}

==See also==
*[[""" + year + """ in the environment]]

[[Category:Protected areas established in """ + year + """| ]]"""

	return var
	
def main():
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)

	years_to_do = []

	for item in mwclient.listing.Category(site, 'Category:Protected areas by year of establishment'):
		if "Category" in str(item):
			try:
				int(item.page_title.split()[-1])
				year = item.page_title.split()[-1]
				years_to_do.append(year)
			except ValueError:
				print "Item " + str(item.page_title.split()[-1]) + " skipped."
	
	for year in years_to_do:
		pagename = "List of protected areas established in " + year
		if site.Pages[pagename].edit() == '':
			page_save_text = generate_wikicode(year)
			page = site.Pages[pagename]
			print "Saving page " + pagename + "."
			page.save(text,summary="Creating per [[WP:CLT]] for [[:Category:Protected areas by year of establishment]] ([[WP:BOT|bot]] - [[User:Theo's Little Bot/disable/tafi|disable]])")
		else:
			print "Page already created, skipping."
	
if __name__ == '__main__':
   main()