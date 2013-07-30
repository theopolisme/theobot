#! /usr/bin/env python
import mwclient
import re
import mwparserfromhell
import sys
import string
import datetime
import password
import time

# CC-BY-SA Theopolisme
# A series of functions useful to Theo's Little Bot.

"""This logs in to enwiki as [[User:Theo's Little Bot]]."""
global site
site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

def checkpage(page):
    """ Returns True if the given checkpage is still set to "ON";
    otherwise, returns false. Accepts one required argument, "page."
    """ 
    print "Checking checkpage."
    page = site.Pages[page]
    text = page.edit()
    
    regexp = re.compile('<!-- CHANGE THE FOLLOWING TEXT TO "OFF"  - - - --> ON <!-- - - - CHANGE THE PREVIOUS TEXT TO "OFF" -->')

    if regexp.search(text) is not None:
        print "We're good!"
        return True
    else:
        return False

def donenow(checkpagey,donenow=0,donenow_div=5,shutdown=0):
	"""This function wraps the above
	subfunction, checkpage().
	"""
	
	if shutdown != 0:
		if donenow >= shutdown:
			print "I've done {0}; all done!".format(str(donenow))
			return False
	
	if donenow % donenow_div == 0:
		if checkpage(checkpagey) == True:
			return True
		else:
			print "Shit, someone's disabled me."
			return False
	else:
		return True

def what_transcludes(template):
    """Returns a list of pages
    that transclude a given template.
    
    Example: what_transcludes('Description missing')
    """
    templatename = 'Template:' + template
    results = mwclient.listing.List(site=site,list_name='embeddedin',prefix='ei',eititle=templatename)
    return results

def nobots(page,user="Theo's Litle Bot",task=None):
    """Checks a page to make sure
    bot is not denied. Returns true
    if bot is allowed. Two parameters accepted,
    "page" and "bot."
    """
    print "Checking page!"
    page = site.Pages[page]
    text = page.edit()

    if task == None:
        task = user
    else:
        task = user+'-'+task

    text = mwparserfromhell.parse(text)
    for tl in text.filter_templates():
        if tl.name in ('bots', 'nobots'):
            break
    else:
        return True
    for param in tl.params:
        bots = [x.lower().strip() for x in param.value.split(",")]
        if param.name == 'allow':
            if ''.join(bots) == 'none': return False
            for bot in bots:
                if bot in (user, task, 'all'):
                    return True
        elif param.name == 'deny':
            if ''.join(bots) == 'none': return True
            for bot in bots:
                if bot in (user, task, 'all'):
                    return False
    return False

def cats_recursive(category,skip=[]):
	"""Recursively goes through
	categories. Almost TOO
	straightforward.
	"""
	category = mwclient.listing.Category(site, category)
	pages = []
	for item in category:
		if u"Category:" in unicode(item) and item not in skip:
			cats_recursive(item)
		else:
			x = item.page_title
			pages.append(x)
	return pages

def rollback(page,user,site):
	token = site.api(action='query',prop='revisions',rvtoken='rollback',titles=page)
	for key in token[u'query'][u'pages'].keys():
		var = key
	if token[u'query'][u'pages'][var][u'revisions'][0][u'user'] == user:
		rbtoken = token[u'query'][u'pages'][var][u'revisions'][0][u'rollbacktoken'] 
		site.api(action='rollback',title=page,user=user,token=rbtoken)
		print "Rollback success!"

def listpages(category,names=True,includeredirects=True):
    """Recursively goes through a category."""
    results = []
    for page in category:
        print page.name
        if page.namespace == 14:  # 14 is the category namespace
            results += listpages(page,names=names,includeredirects=includeredirects)
        else:
            if includeredirects == False:
                if page.redirect == True:
                    continue
            if names == True:
                results.append(page.name)
            else:
                results.append(page)
    return results

def redirects(name,namespace=None,pg_prefix='',output=None):
    """This little function returns redirects to a particular page.
    `output` can be defined as a particular detail about the pages you'd like
    to return, rather than simply a list of mwclient.page.Page objects -- for example:

    # DEFAULT BEHAVIOR; returns page objects
    >>> redirects('Foo')
    [<Page object 'Tra' for <Site object 'en.wikipedia.org/w/'>>, <Page object 'La' for <Site object 'en.wikipedia.org/w/'>>, <Page object 'Lalala' for <Site object 'en.wikipedia.org/w/'>>]

    # OPTIONAL OUTPUT PARAMETER can return just the page_title, for example
    >>> redirects('Foo',output='page_title')
    ['Tra', 'La', 'Lalala']

    """
    page = site.Pages[pg_prefix+name]
    backlinks = page.backlinks(filterredir="redirects",namespace=namespace)
    if output:
        results = []
        for page in backlinks:
            results.append(eval("page."+output))
        return results
    else:
        return backlinks
