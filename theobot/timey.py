#! /usr/bin/env python
import re
import time

# CC-BY-SA Theopolisme

def ordinal(value):
    """
    Converts zero or a *postive* integer (or their string 
    representations) to an ordinal value.

    >>> for i in range(1,13):
    ...     ordinal(i)
    ...     
    u'1st'
    u'2nd'
    u'3rd'
    u'4th'
    u'5th'
    u'6th'
    u'7th'
    u'8th'
    u'9th'
    u'10th'
    u'11th'
    u'12th'

    >>> for i in (100, '111', '112',1011):
    ...     ordinal(i)
    ...     
    u'100th'
    u'111th'
    u'112th'
    u'1011th'

    """
    try:
        value = int(value)
    except ValueError:
        return value

    if value % 100//10 != 1:
        if value % 10 == 1:
            ordval = u"%d%s" % (value, "st")
        elif value % 10 == 2:
            ordval = u"%d%s" % (value, "nd")
        elif value % 10 == 3:
            ordval = u"%d%s" % (value, "rd")
        else:
            ordval = u"%d%s" % (value, "th")
    else:
        ordval = u"%d%s" % (value, "th")

    return ordval

def txt2timestamp(txt, format):
    """Attempts to convert the timestamp 'txt' according to given 'format'.
    On success, returns the time tuple; on failure, returns None."""
##    print txt, format
    try:
        return time.strptime(txt,format)
    except ValueError:
        try:
            return time.strptime(txt.encode('utf8'),format)
        except:
            pass
        return None

def str2time(str):
    """Accepts a string defining a time period:
    7d - 7 days
    36h - 36 hours
    Returns the corresponding time, measured in seconds."""
    if str[-1] == 'd':
        return int(str[:-1])*24*3600
    elif str[-1] == 'h':
        return int(str[:-1])*3600
    else:
        return int(str)

class DiscussionThread(object):
    """An object representing a discussion thread on a page, that is something of the form:

    == Title of thread ==

    Thread content here. ~~~~
    :Reply, etc. ~~~~
    """

    def __init__(self,howold):
        self.content = ""
        self.timestamp = None
        self.howold = howold

    def __repr__(self):
        return '%s("%s",%d bytes)' \
               % (self.__class__.__name__,self.title,len(self.content))

    def feedLine(self, line):
        if not self.content and not line:
            return
        self.content += line + '\n'
        #Update timestamp
# nnwiki:
# 19:42, 25 mars 2008 (CET)
# enwiki
# 16:36, 30 March 2008 (UTC)
# huwiki
# 2007. december 8., 13:42 (CET)
        TM = re.search(r'(\d\d):(\d\d), (\d\d?) (\S+) (\d\d\d\d) \(.*?\)', line)
        if not TM:
            TM = re.search(r'(\d\d):(\d\d), (\S+) (\d\d?), (\d\d\d\d) \(.*?\)', line)
        if not TM:
            TM = re.search(r'(\d{4})\. (\S+) (\d\d?)\., (\d\d:\d\d) \(.*?\)', line)
# 18. apr 2006 kl.18:39 (UTC)
# 4. nov 2006 kl. 20:46 (CET)
        if not TM:
            TM = re.search(r'(\d\d?)\. (\S+) (\d\d\d\d) kl\.\W*(\d\d):(\d\d) \(.*?\)', line)
#3. joulukuuta 2008 kello 16.26 (EET)
        if not TM:
            TM = re.search(r'(\d\d?)\. (\S+) (\d\d\d\d) kello \W*(\d\d).(\d\d) \(.*?\)', line)
        if not TM:
# 14:23, 12. Jan. 2009 (UTC)
            pat = re.compile(r'(\d\d):(\d\d), (\d\d?)\. (\S+)\.? (\d\d\d\d) \((?:UTC|CES?T)\)')
            TM = pat.search(line)
# ro.wiki: 4 august 2012 13:01 (EEST)
        if not TM:
            TM = re.search(r'(\d\d?) (\S+) (\d\d\d\d) (\d\d):(\d\d) \(.*?\)', line)
        if TM:
            TIME = txt2timestamp(TM.group(0),"%d. %b %Y kl. %H:%M (%Z)")
            if not TIME:
                TIME = txt2timestamp(TM.group(0), "%Y. %B %d., %H:%M (%Z)")
            if not TIME:
                TIME = txt2timestamp(TM.group(0), "%d. %b %Y kl.%H:%M (%Z)")
            if not TIME:
                TIME = txt2timestamp(re.sub(' *\([^ ]+\) *', '', TM.group(0)),
                                     "%H:%M, %d %B %Y")
            if not TIME:
                TIME = txt2timestamp(TM.group(0), "%H:%M, %d %b %Y (%Z)")
            if not TIME:
                TIME = txt2timestamp(re.sub(' *\([^ ]+\) *', '', TM.group(0)),
                                     "%H:%M, %d %b %Y")
            if not TIME:
                TIME = txt2timestamp(TM.group(0), "%H:%M, %b %d %Y (%Z)")
            if not TIME:
                TIME = txt2timestamp(TM.group(0), "%H:%M, %B %d %Y (%Z)")
            if not TIME:
                TIME = txt2timestamp(TM.group(0), "%H:%M, %b %d, %Y (%Z)")
            if not TIME:
                TIME = txt2timestamp(TM.group(0), "%H:%M, %B %d, %Y (%Z)")
            if not TIME:
                TIME = txt2timestamp(TM.group(0),"%d. %Bta %Y kello %H.%M (%Z)")
            if not TIME:
                TIME = txt2timestamp(TM.group(0), "%d %B %Y %H:%M (%Z)")
            if not TIME:
                TIME = txt2timestamp(re.sub(' *\([^ ]+\) *', '', TM.group(0)),
                                     "%H:%M, %d. %b. %Y")
            if TIME:
                self.timestamp = max(self.timestamp, time.mktime(TIME))
##                pywikibot.output(u'Time to be parsed: %s' % TM.group(0))
##                pywikibot.output(u'Parsed time: %s' % TIME)
##                pywikibot.output(u'Newest timestamp in thread: %s' % TIME)

    def size(self):
        return len(self.title) + len(self.content) + 12

    def toText(self):
        return "== " + self.title + ' ==\n\n' + self.content

    def shouldBeArchived(self):
        algo = self.howold
        reT = re.search(r'^old\((.*)\)$',algo)
        if reT:
            if not self.timestamp:
                return ''
            #TODO: handle this:
                #return 'unsigned'
            maxage = str2time(reT.group(1))
            if self.timestamp + maxage < time.time():
                # should be archived
                return True
            elif self.timestamp + maxage >= time.time():
                # shouldn't be archived
                return False
            else:
                return False