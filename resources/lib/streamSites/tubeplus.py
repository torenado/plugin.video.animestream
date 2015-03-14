import urllib,urllib2,re,sys,httplib
#import xbmcplugin,xbmcgui,xbmcaddon,urlresolver
import urlresolver
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging
from datetime import datetime
from utils import *
try:
    import json
except ImportError:
    import simplejson as json
    
#testing in shell
#TEST 1
# python -c "execfile('tubeplus.py'); Episode_Listing_Pages('http://www.tubeplus.me/player/920680/Family_Guy/')"
#TEST2
# python -c "execfile('tubeplus.py'); Episode_Page('http://www.tubeplus.me/player/2114250/Family_Guy/season_11/episode_14/Call_Girl/')"
	
#animestream
# modded from --> <addon id="plugin.video.animecrazy" name="Anime Crazy" version="1.0.9" provider-name="AJ">

BASE_URL = 'http://www.tubeplus.me'

base_url_name = BASE_URL.split('www.')[1]
base_txt = base_url_name + ': '
	
aniUrls = ['http://www.tubeplus.me/browse/tv-shows/Animation/-/']
tube_url = 'http://www.tubeplus.me/browse/tv-shows/Animation/'
abc = [chr(i) for i in xrange(ord('A'), ord('Z')+1)]
for alphaB in abc:
	aniUrls.append(tube_url+alphaB.upper()+'/')
	
# aniUrls.append('http://www.tubeplus.me/browse/movies/Animation/-/')
# tube_url = 'http://www.tubeplus.me/browse/movies/Animation/'
# for alphaB in abc:
	# aniUrls.append(tube_url+alphaB.upper()+'/')
	
def Episode_Listing_Pages(url):
	# Identifies the number of pages attached to the original content page
	print base_txt +  url

	episodeListPage = url
	epList = Episode_Listing(episodeListPage)
	
	return epList
	
	
def Episode_Listing(url):
	# Extracts the URL and Page name of the various content pages
	
	link = grabUrlSource(url)
	link = link.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('> <','><')

	match1=re.compile('<div id="seasons">(.+?)<ul>').findall(link)
	match=re.compile('href=/player(.+?)">').findall(match1[0])
	epList = []

	if(len(match) >= 1 and 'javascript:show(' not in link):
		for episodePageLink in match:
			season = '1'
			epNum = '0'
			episodePageLink = BASE_URL + '/player' +episodePageLink
			if epNum == '0':
				if 'season' in episodePageLink:
					season=re.compile('/season_(.+?)/').findall(episodePageLink)[0]
				if 'episode' in episodePageLink:
					epNum=re.compile('/episode_(.+?)/').findall(episodePageLink)[0]
			
			season = int(season)	
			epNum = int(epNum)	
			
			episodePageName = ''
			name = episodePageLink.strip().split('/')
			for  nameTest in reversed(name):
				episodePageName = nameTest
				break
				
			episodePageName = episodePageName.title().replace(' - ',' ').replace(':',' ').replace('-',' ').replace('_',' ').strip()
			epList.append([episodePageLink, episodePageName, '', epNum, season])
	elif('javascript:show(' in link):
		season = 1
		epNum = 1
		episodePageLink = url
		episodePageName=re.compile('var main_title = "(.+?)"').findall(link)
		epList.append([episodePageLink, episodePageName[0], '', epNum, season])
		
	else:
		print base_txt +  'Nothing was parsed from Episode_Listing: ' + url
		
	return epList
	
	
def Episode_Page(url):
	# Identifies the number of mirrors for the content
	print base_txt +  url
	
	episodeMediaMirrors = url
	epMedia = Episode_Media_Link(episodeMediaMirrors)
	
	print epMedia
	return epMedia
	
	
def Episode_Media_Link(url, mirror=1):
	# Extracts the URL for the content media file
	
	link = grabUrlSource(url)
	mirrorTotal = re.compile('javascript:show\((.+?)\)').findall(link)
	
	epMedia = []
	if len(mirrorTotal)>0 and 'Sorry, we ' not in link:
		part = 1
		for streamingPlayer in mirrorTotal:
			stream_info = streamingPlayer.replace('\'','').strip().split(',')
			media_id = stream_info[0]
			host = stream_info[2]
			
			episodeMediaLink = urlresolver.HostedMediaFile(host=host, media_id=media_id).get_url()
			epMedia.append([base_url_name,episodeMediaLink, mirror, part])
			mirror += 1
	
	if(len(epMedia) < 1):
		print base_txt +  'Nothing was parsed from Episode_Media_Link: ' + url
	
	return epMedia

		
def Total_Video_List(link):
	# Generate list of shows/movies
	
	searchRes = []
	match=re.compile('<a target="_blank" title="Watch online: (.+?)" href="(.+?)"><img border=').findall(link)
	if(len(match) > 0):
		for videoName, videoInfo in match:
			videoLink = BASE_URL + videoInfo
			searchRes.append([videoLink, videoName])
	else:
		print base_txt +  'Nothing was parsed from Total_Video_List' 
	
	# searchRes.sort(key=lambda name: name[1]) 
	# searchRes = U2A_List(searchRes)
	# searchRes = f2(searchRes)
	return searchRes