import urllib,urllib2,re,sys,httplib
#import xbmcplugin,xbmcgui,xbmcaddon,urlresolver
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
# python -c "execfile('default.py'); Episode_Listing_Pages('http://www.animefushigi.com/anime/fairy-tail')"
#TEST2
# python -c "execfile('default.py'); Episode_Media_Link('http://www.animefushigi.com/watch/fairy-tail-episode-90')"
	
#animestream
# modded from --> <addon id="plugin.video.animecrazy" name="Anime Crazy" version="1.0.9" provider-name="AJ">

BASE_URL = 'http://www.hentaiseries.net'

base_url_name = BASE_URL.split('www.')[1]
base_txt = base_url_name + ': '

aniUrls = ['http://www.hentaiseries.net/?genre=Uncensored']

	
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

	match=re.compile('<span class="epd"><a href="(.+?)" rel="bookmark" title="Watch (.+?) Episode (.+?) Online">').findall(link)
	# match=re.compile('href=/player(.+?)">').findall(match1[0])
	epList = []

	if(len(match) >= 1):
		for episodePageLink, episodePageName, epNum in match:
			season = 1	
			epNum = int(epNum)	
			episodePageName = episodePageName.title().replace(' - ',' ').replace(':',' ').replace('-',' ').replace('_',' ').strip()
			epList.append([episodePageLink, episodePageName, '', epNum, season])		
	else:
		print base_txt +  'Nothing was parsed from Episode_Listing: ' + url
		
	return epList

def Episode_Page(url):
	# Identifies the number of mirrors for the content
	print base_txt +  url
	
	episodeMediaMirrors = url
	epMedia = Episode_Media_Link(episodeMediaMirrors)
		
	return epMedia
	
def Episode_Media_Link(url, mirror=1, part=1):
	# Extracts the URL for the content media file
	link = grabUrlSource(url)
	
	match=re.compile('file: \'(.+?)\'};').findall(link)
	epMedia = []
	
	if(len(match) >= 1):
		for episodeMediaLink in match:
			if (not 'http://ads.' in episodeMediaLink and not episodeMediaLink.endswith(('.gif','.jpg'))  and not 'facebook.com/plugins/like.php' in episodeMediaLink):
				mirror += 1
				if (base_url_name in episodeMediaLink):
					episodeMediaLink = Media_Link_Finder(episodeMediaLink)
					
				epMedia.append([base_url_name,episodeMediaLink, mirror, part])
	
	if(len(epMedia) < 1):
		print base_txt +  'Nothing was parsed from Episode_Media_Link: ' + url
	
	
	epMedia = f2(epMedia)
	return epMedia
	
def Media_Link_Finder(url):
	# Extracts the URL for the content media file
	link = grabUrlSource(url).replace(' ','')

	match = re.compile('<location>(.+?)</location>').findall(link)
	epMediaFound = []
	
	if(len(match) >= 1):
		epMediaFound = match[0]
		
	if (len(epMediaFound) < 1):
		epMediaFound = url
		print base_txt +  'Nothing was parsed from Media_Link_Finder: ' + url
		
	return epMediaFound
		
def Video_List_Searched(searchText,link):
	# Generate list of shows/movies based on the provide keyword(s)
	# urls = ['http://www.animefushigi.com/full-anime-list/','http://www.animefushigi.com/anime/movies/']
	
	searchRes = []
	match=re.compile('<a(.+?)>'+searchText).findall(link)
	videoName = searchText
	if(len(match) >= 1):
		for linkFound in match:
			videoInfo = re.compile('href="(.+?)"').findall(linkFound)
			videoLink = videoInfo[-1]
			videoNameSplit = videoLink.split('/')
			videoName = videoNameSplit[-1].replace('-',' ').replace('_',' ').title().strip()
			if (not 'http://ads.' in videoLink):
				searchRes.append([videoLink, videoName])
	# else:
		# print base_txt +  'Nothing was parsed from Video_List_Searched' 
		
	
	return searchRes
	
def Total_Video_List(link):
	# Generate list of shows/movies 
	searchRes = []
	match=re.compile('<div class="updateinfo"><a href=\'(.+?)\'>(.+?)</a>').findall(link) 
	if(len(match) >= 1):
		for videoLink, videoName in match:
			if (not 'http://ads.' in videoLink):
				searchRes.append([videoLink, videoName.title()])
	else:
		print base_txt +  'Nothing was parsed from Total_Video_List' 
	
	# searchRes.sort(key=lambda name: name[1]) 
	searchRes = U2A_List(searchRes)
	searchRes = f2(searchRes)
	return searchRes