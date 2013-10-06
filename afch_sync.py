#!/usr/bin/env python
"""
Copyright (C) 2013 Legoktm
Modifications copyright (C) 2013 Theopolisme

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
import git
import os
import sys
import mwclient
from theobot import password

#config
path = '~/afc_pusher/tmp'
path = os.path.expanduser(path)

if '--beta' in sys.argv:
    branch = 'beta'
elif '--master' in sys.argv:
    branch = 'master'
elif '--ffu' in sys.argv:
    branch = 'ffu'
else:
    branch = 'develop'

site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)

if os.path.exists(path):
    #Update it
    repo = git.Repo(path)
    origin = repo.remotes.origin
    try:
        origin.fetch()
    except AssertionError:
        # I swear, this works.
        origin.fetch()
    origin.pull()
else:
    print 'Cloning to tmp/'
    repo = git.Repo.clone_from('https://github.com/WPAFC/afch.git', path)

sha1 = repo.heads[branch].commit.hexsha
repo.heads[branch].checkout()


summary = '[[WP:BOT|Bot]]: Auto-updating to {0} ({1})'.format(sha1, branch)
print summary

header = '/* Uploaded from https://github.com/WPAFC/afch, commit: {0} ({1}) */\n'.format(sha1, branch)

prefix = "User:Theo's Little Bot/afch/afchelper"

mapping = {
    'MediaWiki:Gadget-afchelper.js': prefix + '.js',
    'MediaWiki:Gadget-afchelper.css': prefix + '.css',
    'core.js': prefix + '.js/core.js',
    'ffu.js': prefix + '.js/ffu.js',
    'prefs.js': prefix + '.js/prefs.js',
    'redirects.js': prefix + '.js/redirects.js',
    'submissions.js': prefix + '.js/submissions.js',
}
files = os.listdir(path + '/src')
print files
print mapping

def strip_first_line(text):
    return '\n'.join(text.splitlines()[1:])

for script in files:
    with open(path + '/src/' + script, 'r') as f:
        text = f.read()
    if prefix != 'MediaWiki:Gadget-afchelper.js':
        text = text.replace('MediaWiki:Gadget-afchelper', prefix.replace('\'',r'%27'))  # I hope this is ok.
        text = text.replace("""var afcHelper_advert = ' ([[WP:AFCH|AFCH]] beta)';""","""var afcHelper_advert = ' ([[WP:AFCH|AFCH]] develop)';""") # denote the develop script
    text = header + text  # Add our custom header
    pg = site.Pages[mapping[script]]
    old = pg.edit()
    if strip_first_line(text) != strip_first_line(old):
        pg.save(text, summary)
