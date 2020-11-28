import xbmcaddon
import xbmcgui
import requests
import html5lib
import xbmc
import re
import base64
import os

addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')

options = ['Subbed Anime','Dubbed Anime','Cartoons', 'Movies']
selection = xbmcgui.Dialog().select('Select a genre', options)

if selection == 0:
  r = requests.get('https://www.wcostream.com/subbed-anime-list')
elif selection == 1:
  r = requests.get('https://www.wcostream.com/dubbed-anime-list')
elif selection == 2:
  r = requests.get('https://www.wcostream.com/cartoon-list')
elif selection == 3:
  r = requests.get('https://www.wcostream.com/movie-list')

document = html5lib.parse(r.content).find(".//*[@class='ddmcc']")

options = ["All"]

filters = document.findall("./{http://www.w3.org/1999/xhtml}ul/{http://www.w3.org/1999/xhtml}a")

for child in filters:
  options.append(child.attrib['name'])

selection = xbmcgui.Dialog().select('Select a filter', options)

if selection == 0:
  titles = document.findall("./{http://www.w3.org/1999/xhtml}ul/{http://www.w3.org/1999/xhtml}ul/{http://www.w3.org/1999/xhtml}li/{http://www.w3.org/1999/xhtml}a")
else:
  things = document.findall("./{http://www.w3.org/1999/xhtml}ul/{http://www.w3.org/1999/xhtml}ul")
  selected_things = things[selection - 1]
  titles = selected_things.findall("./{http://www.w3.org/1999/xhtml}li/{http://www.w3.org/1999/xhtml}a")

options = []

for child in titles:
  options.append(child.text)

selection = xbmcgui.Dialog().select('Select an option', options)

url = titles[selection].attrib['href']

series_name = titles[selection].text

try:
  os.makedirs("/Users/michaeldegraw/Downloads/%s" % (series_name))
except OSError:
  if not os.path.isdir("/Users/michaeldegraw/Downloads/%s" % (series_name)):
    raise

r = requests.get('https://www.wcostream.com/%s' % (url))

document = html5lib.parse(r.content).find(".//*[@id='catlist-listview']")

episodes = document.findall("./{http://www.w3.org/1999/xhtml}ul/{http://www.w3.org/1999/xhtml}li/{http://www.w3.org/1999/xhtml}a")

options = ["Entire Series"]

for episode in episodes:
  options.append(episode.text)

selection = xbmcgui.Dialog().select('Select an episode', options)

urls = []
episode_names = []
if selection == 0:
  for episode in episodes:
    urls.append(episode.attrib['href'])
    episode_names.append(episode.text)
else:
  urls.append(episodes[selection - 1].attrib['href'])
  episode_names.append(episodes[selection - 1].text)

for i in range(len(urls)):
  url = urls[i]
  episode_name = episode_names[i]
  r = requests.get("%s" % (url))

  document = html5lib.parse(r.content).find(".//*[@itemtype='http://schema.org/VideoObject']")

  # document = document.findall("./{http://www.w3.org/1999/xhtml}b")[2]
  document = document.find(".//{http://www.w3.org/1999/xhtml}script")

  array = eval("[%s]" % (document.text.split('[')[1].split(']')[0]))

  offset = int(document.text.split('- ')[1].split(');')[0])

  iframe = ""

  for element in array:
    iframe += chr(int(re.sub('\D', '', base64.b64decode(element).decode())) - offset)

  document = html5lib.parse(iframe).findall(".//*{http://www.w3.org/1999/xhtml}iframe")[0]

  url = document.attrib['src']

  r = requests.get("https://www.wcostream.com%s" % (url))

  document = html5lib.parse(r.content)

  document = document.findall(".//{http://www.w3.org/1999/xhtml}script")

  for script in document:
    if script.text and "/inc/embed/getvidlink.php" in script.text:
      document = script
      break

  url = document.text.split('get("')[1].split('"')[0]

  r = requests.get("https://www.wcostream.com%s" % (url), headers={'X-Requested-With': 'XMLHttpRequest'})

  response = r.json()

  if response['hd']:
    url = "%s/getvid?evid=%s" % (response['server'], response['hd'])
  else:
    url = "%s/getvid?evid=%s" % (response['server'], response['enc'])

  r = requests.get(url)

  open("/Users/michaeldegraw/Downloads/%s/%s.mp4" % (series_name, episode_name), 'wb').write(r.content)

xbmcgui.Dialog().ok(addonname, 'Test worked?')