#!/usr/bin/python
from PIL import Image
from xml.dom import minidom
import cStringIO, mwclient, uuid, urllib, os.path, cgi, littleimage, sys, urllib2, re, theobot.bot
import logging # for, well, logs
from theobot import password

# CC-BY-SA Theopolisme
# Task 1 on [[User:Theo's Little Bot]]


logger = logging.getLogger('resizer_auto')
hdlr = logging.FileHandler('resizer_auto.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

def sokay(donenow):
	"""This function calls a subfunction
	of the theobot module, checkpage().
	"""
	if donenow % 5 == 0:
		if theobot.bot.checkpage("User:Theo's Little Bot/disable/resizer") == True:
			return True
		else:
			return False
	else:
		return True

def are_you_still_there(theimage):
	""" This function makes sure that
	a given image is still tagged with
	{{non-free reduce}}.
	"""
	img_name = "File:" + theimage
		
	page = site.Pages[img_name]
	text = page.edit()
	
	regexp = re.compile(r'\{\{[Nn]on-free reduce.*?\}\}')
	regexp2 = re.compile(r'\{\{[Rr]educe.*?\}\}')
	regexp3 = re.compile(r'\{\{[Nn]onfree reduce.*?\}\}')
	regexp4 = re.compile(r'\{\{[Cc]omic-ovrsize-img.*?\}\}')
	regexp5 = re.compile(r'\{\{[Ff]air Use reduce.*?\}\}')
	regexp6 = re.compile(r'\{\{[Ff]air use reduce.*?\}\}')
	regexp7 = re.compile(r'\{\{[Ff]air-use reduce.*?\}\}')
	regexp8 = re.compile(r'\{\{[Ff]airUse[Rr]educe.*?\}\}')
	regexp9 = re.compile(r'\{\{[Ff]airuse[Rr]educe.*?\}\}')
	regexp10 = re.compile(r'\{\{[Ii]mage-toobig.*?\}\}')
	regexp11 = re.compile(r'\{\{[Nn]fr.*?\}\}')
	regexp12 = re.compile(r'\{\{[Nn]on-free-[Rr]educe.*?\}\}')
	regexp13 = re.compile(r'\{\{[Nn]onfree [Rr]educe.*?\}\}')
	regexp14 = re.compile(r'\{\{[Rr]educe.*?\}\}')
	regexp15 = re.compile(r'\{\{[Rr]educe size.*?\}\}')
	regexp16 = re.compile(r'\{\{[Ss]maller image.*?\}\}')
	
	if img_name == "File:Avvo.com consumer logo, March 2013.png":
		return False
	elif regexp.search(text) is not None:
		return True
	elif regexp2.search(text) is not None:
		return True
	elif regexp3.search(text) is not None:
		return True
	elif regexp4.search(text) is not None:
		return True
	elif regexp5.search(text) is not None:
		return True
	elif regexp6.search(text) is not None:
		return True
	elif regexp7.search(text) is not None:
		return True
	elif regexp8.search(text) is not None:
		return True
	elif regexp9.search(text) is not None:
		return True
	elif regexp10.search(text) is not None:
		return True
	elif regexp11.search(text) is not None:
		return True
	elif regexp12.search(text) is not None:
		return True
	elif regexp13.search(text) is not None:
		return True
	elif regexp14.search(text) is not None:
		return True
	else:
		return False

def image_routine(images):
	""" This function does most of the work:
	* First, checks the checkpage using sokay()
	* Then makes sure the image file still exists using are_you_still_there()
	* Next it actually resizes the image.
	* As long as the resize works, we reupload the file.
	* Then we update the page with {{non-free reduced}}.
	* And repeat!
	"""
	donenow = 5
	for theimage in images:
		print "Working on " + theimage.encode('ascii', 'ignore')
		if sokay(donenow) == True:
			if are_you_still_there(theimage) == True:	
				desired_megapixel = float(0.1)
				pxl = desired_megapixel * 1000000
				compound_site = 'en.wikipedia.org'
				filename = str(uuid.uuid4())
				file = littleimage.gimme_image(filename,compound_site,pxl,theimage)
				
				if file == "PIXEL":
					print "Removing tag...already reduced..."
					img_name = "File:" + theimage
					page = site.Pages[img_name]
					text = page.edit()
					text = re.sub('\{\{[Nn]on-free reduce.*?\}\}', '', text)
					text = re.sub('\{\{[Nn]on-free reduce.*?\}\}', '', text)
					text = re.sub('\{\{[Rr]educe.*?\}\}', '', text)			
					text = re.sub(r'\{\{[Cc]omic-ovrsize-img.*?\}\}', '', text)
					text = re.sub(r'\{\{[Ff]air Use reduce.*?\}\}', '', text)
					text = re.sub(r'\{\{[Ff]air use reduce.*?\}\}', '', text)
					text = re.sub(r'\{\{[Ff]air-use reduce.*?\}\}', '', text)
					text = re.sub(r'\{\{[Ff]airUse[Rr]educe.*?\}\}', '', text)
					text = re.sub(r'\{\{[Ff]airuse[Rr]educe.*?\}\}', '', text)
					text = re.sub(r'\{\{[Ii]mage-toobig.*?\}\}', '', text)
					text = re.sub(r'\{\{[Nn]fr.*?\}\}', '', text)
					text = re.sub(r'\{\{[Nn]on-free-[Rr]educe.*?\}\}', '', text)
					text = re.sub(r'\{\{[Nn]onfree [Rr]educe.*?\}\}', '', text)
					text = re.sub(r'\{\{[Rr]educe.*?\}\}', '', text)
					text = re.sub(r'\{\{[Rr]educe size.*?\}\}', '', text)
					text = re.sub(r'\{\{[Ss]maller image.*?\}\}', '', text)		
					page.save(text, summary = "Removing {{[[Template:Non-free reduce|Non-free reduce]]}} since file is already adequately reduced ([[WP:BOT|BOT]] - [[User:Theo's Little Bot/disable/resizer|disable]])")				
					
				elif file not in ("ERROR", "PIXEL"):					
					try:
						site.upload(open(file), theimage, "Reduce size of non-free image ([[WP:BOT|BOT]] - [[User:Theo's Little Bot/disable/resizer|disable]])")
						
						print "Uploaded!"
						filelist = [ f for f in os.listdir(".") if f.startswith(filename) ]
						for fa in filelist: os.remove(fa)
						img_name = "File:" + theimage
						
						page = site.Pages[img_name]
						text = page.edit()
						glob = text
						text = re.sub('\{\{[Nn]on-free reduce.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub('\{\{[Rr]educe.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)			
						text = re.sub(r'\{\{[Cc]omic-ovrsize-img.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub(r'\{\{[Ff]air Use reduce.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub(r'\{\{[Ff]air use reduce.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub(r'\{\{[Ff]air-use reduce.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub(r'\{\{[Ff]airUse[Rr]educe.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub(r'\{\{[Ff]airuse[Rr]educe.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub(r'\{\{[Ii]mage-toobig.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub(r'\{\{[Nn]fr.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub(r'\{\{[Nn]on-free-[Rr]educe.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub(r'\{\{[Nn]onfree [Rr]educe.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub(r'\{\{[Rr]educe.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub(r'\{\{[Rr]educe size.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub(r'\{\{[Ss]maller image.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)							
						page.save(text, summary = "Tagging with {{[[Template:Non-free reduced|Non-free reduced]]}} ([[WP:BOT|BOT]] - [[User:Theo's Little Bot/disable/resizer|disable]])")
						
						print "Tagged!"
					except:
						print "Unknown error. Image skipped."
						messager12345 = "Unknown error; skipped " + theimage
						logger.error(messager12345)
						
				else:
					print "Image skipped."
					messager123 = "Skipped " + theimage
					logger.error(messager123)
			else:
				print "Gah, looks like someone removed the tag."
				messager1234 = "Tag removed on image; skipped " + theimage
				logger.error(messager1234)

		else:
			print "Ah, darn - looks like the bot was disabled."
			sys.exit()
		donenow = donenow+1

def main():
	"""This defines and fills a global
	variable for the site, and then calls
	get_images() to assemble an initial
	selection of images to work with. Then
	it runs image_rountine() on this selection.
	"""
	global site
	site = mwclient.Site('en.wikipedia.org')
	site.login(password.username, password.password)

	#work_with = get_images()	
	zam = mwclient.listing.Category(site, "Category:Wikipedia non-free file size reduction requests")
	glob = zam.members()
	flub = []
	for image in glob:
		zip = image.page_title
		print zip.encode('ascii', 'ignore')
		flub.append(zip)
	image_routine(flub)
	print "We're DONE!"
	
main()