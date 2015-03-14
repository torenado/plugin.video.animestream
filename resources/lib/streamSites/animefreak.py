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
# python -c "execfile('animefreak.py'); Episode_Listing_Pages('http://www.animefreak.tv/watch/fairy-tail-online')"
#TEST2
# python -c "execfile('animefreak.py'); Episode_Page('http://www.animefreak.tv/watch/fairy-tail-episode-90-online')"
	
#animestream
# modded from --> <addon id="plugin.video.animecrazy" name="Anime Crazy" version="1.0.9" provider-name="AJ">

BASE_URL = 'http://www.animefreak.tv'

base_url_name = BASE_URL.split('www.')[1]
base_txt = base_url_name + ': '

aniUrls = ['http://www.animefreak.tv/book']

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

	match1=re.compile('<div class="blockcontent"><ul class="menu">(.+?)</ul>').findall(link)
	match=re.compile('<a href="(.+?)">(.+?)</a>').findall(match1[0])
	epList = []

	if(len(match) >= 1):
		for episodePageLink, episodePageName in match:
			season = '1'
			epNum = 0
			episodePageLink = BASE_URL + episodePageLink
			if epNum == 0:
				epNumPart = episodePageName.strip().split()
				for  epNumTest in reversed(epNumPart):
					if epNumTest.isdigit():
						epNum = int(epNumTest)
						break
			
			if 'season' in episodePageLink:
				season=re.compile('season-(.+?)-').findall(episodePageLink)[0]
			elif 'Season' in episodePageName.title():
				season=re.compile('Season (.+?) ').findall(episodePageName.title())[0]
			
			season = int(season)			
			episodePageName = episodePageName.title().replace(' Episode','').replace(' - ',' ').replace(':',' ').replace('-',' ').strip()
			epList.append([episodePageLink, episodePageName, '', epNum, season])
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
	mirrorTotal = re.compile('javascript:loadParts\(\'(.+?)\'').findall(link)
	
	epMedia = []
	if len(mirrorTotal)>0:
		for streamingPlayer in mirrorTotal:
			frame = urllib.unquote_plus(streamingPlayer.lower()).replace('\'','"').replace(' =','=').replace('= ','=')
			match=re.compile('<(iframe|embed)(.+?)src="(.+?)"').findall(frame)
			part = 1

			if(len(match) >= 1):
				for garbage, garbage1, episodeMediaLink in match:
					if (not ('http://ads.' in episodeMediaLink or 'http://ad.' in episodeMediaLink or 'advertising' in episodeMediaLink or 'adserving' in episodeMediaLink) ):
						if (base_url_name in episodeMediaLink):
							episodeMediaLink = Media_Link_Finder(episodeMediaLink)
							
						epMedia.append([base_url_name,episodeMediaLink, mirror, part])
			mirror = mirror + 1
	
	if(len(epMedia) < 1):
		print base_txt +  'Nothing was parsed from Episode_Media_Link: ' + url
	
	return epMedia
	
def Media_Link_Finder(url):
	# Extracts the URL for the content media file
	
	link = grabUrlSource(url)
	link = link.replace(' ','')

	match = re.compile('(iframe|embed)src="(.+?)"').findall(link)
	match1 = re.compile('(iframe|embed)src=\'(.+?)\'').findall(link)
	epMediaFound = []
	
	if(len(match) >= 1):
		epMediaFound = match[0][1]
		
	if(len(match1) >= 1):
		epMediaFound = match1[0][1]
		
	if (len(epMediaFound) < 1):
		epMediaFound = url
		print base_txt +  'Nothing was parsed from Media_Link_Finder: ' + url
		
	return epMediaFound
	
		
def Video_List_Searched(searchText, link):
	# Generate list of shows/movies based on the provide keyword(s)
	# url = 'http://www.myanimelinks.com/full-anime-list/'
	
	searchRes = []
	match=re.compile('<a(.+?)>'+searchText).findall(link)
	videoName = searchText
	if(len(match) >= 1):
		for linkFound in match:
			videoInfo = re.compile('href="(.+?)"').findall(linkFound)
			videoLink = videoInfo[-1]
			videoNameSplit = videoLink.split('/')
			videoName = videoNameSplit[-2].replace('-',' ').replace('_',' ').title().strip()
			videoName = urllib.unquote(videoName)
			if (not 'http://ads.' in videoLink and not 'episode' in videoLink):
				searchRes.append([BASE_URL + videoLink, videoName])
	# else:
		# print base_txt +  'Nothing was parsed from Video_List_Searched' 
				
	return searchRes

		
def Total_Video_List(link):
	# Generate list of shows/movies
	
	searchRes = []
	match1=re.compile('<h1>Anime List</h1>(.+?)</ul></div><div class="defaultblock">').findall(link)
	if(len(match1) > 0):
		match=re.compile('<a(.+?)>(.+?)</a>').findall(match1[0])
		if(len(match) > 0):
			for linkFound, videoName in match:
				videoInfo = re.compile('href="(.+?)"').findall(linkFound)
				if(len(videoInfo) >= 1):
					if not 'http' in videoInfo[-1]:
						videoLink = BASE_URL + videoInfo[-1]
					videoNameSplit = videoLink.split('/')[-1]
					# videoName = videoNameSplit.replace('-',' ').replace('_',' ').title().strip()
					if 'dubbed' in videoLink:
						videoName = videoName + ' (Dubbed)'
					if (not 'http://ads.' in videoLink and not 'episode' in videoLink and not videoName.startswith('<')):
						searchRes.append([videoLink, videoName])
		else:
			print base_txt +  'Nothing was parsed from Total_Video_List 1' 
	else:
		print base_txt +  'Nothing was parsed from Total_Video_List 2' 
	
	# searchRes.sort(key=lambda name: name[1]) 
	# searchRes = U2A_List(searchRes)
	# searchRes = f2(searchRes)
	return searchRes