#! /usr/bin/env python
from PIL import Image
import pyexiv2
import cStringIO
import mwclient
import uuid
import urllib
import cgi
import littleimage
import sys
import urllib2
import requests
import math
import tempfile
import os

# CC-BY-SA Theopolisme
# Task 1 on [[User:Theo's Little Bot]] (subsidiary)

def metadata(source_path, dest_path, image):
	"""This function moves the metadata
	from the old image to the new, reduced
	image using pyexiv2.
	"""
	source_image = pyexiv2.metadata.ImageMetadata(source_path)
	source_image.read()
	dest_image = pyexiv2.metadata.ImageMetadata(dest_path)
	dest_image.read()
	source_image.copy(dest_image)
	dest_image["Exif.Photo.PixelXDimension"] = image.size[0]
	dest_image["Exif.Photo.PixelYDimension"] = image.size[1]
	dest_image.write()

def gimme_image(filename,compound_site,pxl,theimage):
	"""This function creates the new image, runs
	metadata(), and passes along the new image's
	filename.
	"""
	site = mwclient.Site(compound_site)
	
	extension = os.path.splitext(theimage)[1]
	extension_caps = extension[1:].upper()
		
	if extension_caps == "JPG":
		extension_caps = "JPEG"
	
	if extension_caps == "GIF":
		results = "SKIP"
		return results

	image_1 = site.Images[theimage] 
	image_2 = str(image_1.imageinfo['url'])
	
	response = requests.get(image_2)
	item10 = cStringIO.StringIO(response.content)

	temp_file = str(uuid.uuid4()) + extension
	f = open(temp_file,'w')
	f.write(item10.getvalue())
	
	try:
		img = Image.open(item10)
		basewidth = int(math.sqrt((pxl * float(img.size[0]))/(img.size[1])))
		wpercent = (basewidth/float(img.size[0]))
		hsize = int((float(img.size[1])*float(wpercent)))
		
		original_pixel = img.size[0] * img.size[1]
		modified_pixel = basewidth * hsize
		pct_chg = 100.0 *  (original_pixel - modified_pixel) / float(original_pixel)
		if pct_chg > 5:
			png_info = img.info
			img = img.resize((int(basewidth),int(hsize)), Image.ANTIALIAS)
			img.save(filename + extension, **png_info)
		else:
			print "Looks like we'd have a less than 5% change in pixel counts. Skipping."
			results = "PIXEL"
			return results
	except (IOError):
		print "Unable to open image " + theimage + " (aborting)"
		results = "ERROR"
		return results

	print "Image saved to disk at " + filename + extension
	results = filename + extension
	try:
		metadata(source_path=temp_file,dest_path=results,image=img)
		print "Image EXIF data copied!"
	except (IOError, ValueError):
		print "EXIF copy failed. Oh well - no pain, no gain."
	filelist = [ f for f in os.listdir(".") if f.startswith(temp_file) ]
	for fa in filelist: os.remove(fa)
	return results
