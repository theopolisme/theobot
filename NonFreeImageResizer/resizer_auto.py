#!/usr/bin/python
from PIL import Image
from xml.dom import minidom
import cStringIO
import mwclient
import uuid
import urllib
import os.path
import cgi
import littleimage
import sys
import urllib2
import re
import logging
sys.path.append("/data/project/theoslittlebot/cgi-bin/theobot")
import theobot.password
import theobot.bot

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
	
	r1 = re.compile(r'\{\{[Nn]on.?free-?\s*[Rr]educe.*?\}\}')
	r2 = re.compile(r'\{\{[Rr]educe.*?\}\}')
	r3 = re.compile(r'\{\{[Cc]omic-ovrsize-img.*?\}\}')
	r4 = re.compile(r'\{\{[Ff]air.?[Uu]se.?[Rr]educe.*?\}\}')
	r5 = re.compile(r'\{\{[Ii]mage-toobig.*?\}\}')
	r6 = re.compile(r'\{\{[Nn]fr.*?\}\}')
	r7 = re.compile(r'\{\{[Ss]maller image.*?\}\}')
	
	if r1.search(text) is not None:
		return True
	elif r2.search(text) is not None:
		return True
	elif r3.search(text) is not None:
		return True
	elif r4.search(text) is not None:
		return True
	elif r5.search(text) is not None:
		return True
	elif r6.search(text) is not None:
		return True
	elif r7.search(text) is not None:
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
				
				if file == "SKIP":
					print "Skipping GIF."
					messager12345 = "Skipped gif: " + theimage
					logger.error(messager12345)
				
				if file == "PIXEL":
					print "Removing tag...already reduced..."
					img_name = "File:" + theimage
					page = site.Pages[img_name]
					text = page.edit()
					text = re.sub(r'\{\{[Nn]on.?free-?\s*[Rr]educe.*?\}\}', '', text)
					text = re.sub(r'\{\{[Rr]educe.*?\}\}', '', text)
					text = re.sub(r'\{\{[Cc]omic-ovrsize-img.*?\}\}', '', text)			
					text = re.sub(r'\{\{[Ff]air.?[Uu]se.?[Rr]educe.*?\}\}', '', text)			
					text = re.sub(r'\{\{[Ii]mage-toobig.*?\}\}', '', text)			
					text = re.sub(r'\{\{[Nn]fr.*?\}\}', '', text)			
					text = re.sub(r'\{\{[Ss]maller image.*?\}\}', '', text)			
					page.save(text, summary = "Removing {{[[Template:Non-free reduce|Non-free reduce]]}} since file is already adequately reduced ([[WP:BOT|BOT]] - [[User:Theo's Little Bot/disable/resizer|disable]])")				
					
				elif file not in ("ERROR", "PIXEL", "SKIP"):					
					try:
						site.upload(open(file), theimage, "Reduce size of non-free image ([[WP:BOT|BOT]] - [[User:Theo's Little Bot/disable/resizer|disable]])", ignore=True)
						
						print "Uploaded!"
						filelist = [ f for f in os.listdir(".") if f.startswith(filename) ]
						for fa in filelist: os.remove(fa)
						img_name = "File:" + theimage
						
						page = site.Pages[img_name]
						text = page.edit()
						text = re.sub(r'\{\{[Nn]on.?free-?\s*[Rr]educe.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub(r'\{\{[Rr]educe.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)
						text = re.sub(r'\{\{[Cc]omic-ovrsize-img.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)			
						text = re.sub(r'\{\{[Ff]air.?[Uu]se.?[Rr]educe.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)			
						text = re.sub(r'\{\{[Ii]mage-toobig.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)			
						text = re.sub(r'\{\{[Nn]fr.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)			
						text = re.sub(r'\{\{[Ss]maller image.*?\}\}', '{{non-free reduced|date=~~~~~}}', text)									
						page.save(text, summary = "Tagging with {{[[Template:Non-free reduced|Non-free reduced]]}} ([[WP:BOT|BOT]] - [[User:Theo's Little Bot/disable/resizer|disable]])")
						
						print "Tagged!"
					except:
						print "Unknown error. Image skipped."
						messager12345 = "Unknown error; skipped " + theimage
						logger.error(messager12345)
						filelist = [ f for f in os.listdir(".") if f.startswith(filename) ]
						for fa in filelist: os.remove(fa)
						
				else:
					print "Image skipped."
					messager123 = "Skipped " + theimage
					filelist = [ f for f in os.listdir(".") if f.startswith(filename) ]
					for fa in filelist: os.remove(fa)
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
	site.login(theobot.password.username, theobot.password.password)

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
	
if __name__ == '__main__':
   main()
