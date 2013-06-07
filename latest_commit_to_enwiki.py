import requests
import mwclient
from theobot import password
from datetime import datetime

r = requests.get('https://api.github.com/repos/theopolisme/theobot/commits', auth=(password.githubuser, password.githubpassword))
contents = r.json()
message = contents[0][u'commit'][u'message'].replace('\n\n','; ')
committer = contents[0][u'commit'][u'committer'][u'name']
date_str = contents[0][u'commit'][u'committer'][u'date']
date = datetime.strptime(date_str,'%Y-%m-%dT%H:%M:%SZ')
date = date.strftime('%d %B %Y')
url = contents[0][u'html_url']

output = """\'\'\'Most recent update\'\'\': [{url} {message}] ({committer} - {date})""".format(url=url,message=message,committer=committer,date=date)

site = mwclient.Site('en.wikipedia.org')
site.login(password.username, password.password)
page = site.Pages["User:Theo's Little Bot/github"]
page.save(output,summary="[[WP:BOT|Bot]]: Updating my github log")