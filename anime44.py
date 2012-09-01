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
# python -c "execfile('anime44.py'); Episode_Listing_Pages('http://www.anime44.com/category/fairy-tail')"
#TEST2
# python -c "execfile('anime44.py'); Episode_Media_Link('http://www.anime44.com/fairy-tail-90-fairy-tail-90')"
	
#animestream
# modded from --> <addon id="plugin.video.animecrazy" name="Anime Crazy" version="1.0.9" provider-name="AJ">

BASE_URL = 'http://anime44.com'

base_url_name = BASE_URL.split('//')[1]
base_txt = base_url_name + ': '

aniUrls = ['http://www.anime44.com/anime-list','http://www.anime44.com/category/anime-movies']

def Episode_Listing_Pages(url):
	# Identifies the number of pages attached to the original content page
	print base_txt + url
	
	link = grabUrlSource(url)
	
	match=re.compile('/page/(.+?)"').findall(link)
	intNumPage = [0]
	if(len(match) >= 1):
		for numPage in match:
			intNumPage.append(int(numPage))
	
	numPage = max(intNumPage) + 1
	
	epList = []
	episodeListPage = url
	if(len(match) >= 1):
		for ii in range(1,numPage):
			episodeListPage = url + '/page/' + str(ii)
			Episode_Listing(episodeListPage)
			epList = epList + Episode_Listing(episodeListPage)
	else:
		epList = epList + Episode_Listing(episodeListPage)
	
	return epList
	
	
def Episode_Listing(url):
	# Extracts the URL and Page name of the various content pages
	
	link = grabUrlSource(url)
	link = link.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('> <','><')

	match=re.compile('<div class="postlist"><a href="(.+?)"(.+?)title="(.+?)">').findall(link)
	epList = []

	if(len(match) >= 1):
		for episodePageLink, garbage, episodePageName in match:
			season = '1'
			episodePageName.replace('# ','#')
			epNum = 0					
			if epNum == 0:					
				epNumPart = episodePageName.strip().split('#')
				for  epNumTest in reversed(epNumPart):
					if epNumTest.isdigit():
						epNum = int(epNumTest)
						break	
						
			if epNum == 0:
				epNumPart = episodePageName.strip().split()
				for  epNumTest in reversed(epNumPart):
					if epNumTest.isdigit():
						epNum = int(epNumTest)
						break
			
			if 'season' in episodePageLink:
				season=re.compile('http://(.+?)-season-(.+?)-').findall(link)[0][1]
			
			episodePageName = episodePageName.title().replace(' Episode','').replace(' - ',' ').replace(':',' ').replace('-',' ').strip()
			epList.append([episodePageLink, episodePageName, '', epNum])
	else:
		print base_txt +  'Nothing was parsed from Episode_Listing: ' + url
		
	return epList
	
	
def Episode_Page(url):
	# Identifies the number of mirrors for the content
	print base_txt +  url
	
	link = grabUrlSource(url)
	
	episodeMediaMirrors = url
	epMedia = Episode_Media_Link(episodeMediaMirrors)
		
	return epMedia
	
	
def Episode_Media_Link(url, mirror=1):
	# Extracts the URL for the content media file
	
	link = grabUrlSource(url)
	
	match=re.compile('<(iframe|embed)(.+?)src="(.+?)"').findall(link)
	epMedia = []
	part = 1

	if(len(match) >= 1):
		for garbage, garbage1, episodeMediaLink in match:
			if (not 'http://ads.' in episodeMediaLink):
				if (base_url_name in episodeMediaLink):
					episodeMediaLink = Media_Link_Finder(episodeMediaLink)
					
				epMedia.append([base_url_name,episodeMediaLink, mirror, part])
	
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
				searchRes.append([videoLink, videoName])
	# else:
		# print base_txt +  'Nothing was parsed from Video_List_Searched' 
				
	return searchRes

		
def Total_Video_List(link):
	# Generate list of shows/movies
	
	searchRes = []
	match=re.compile('<a(.+?)>(.+?)</a>').findall(link)
	if(len(match) >= 1):
		for linkFound, videoName in match:
			videoInfo = re.compile('href="(.+?)"').findall(linkFound)
			if(len(videoInfo) >= 1):
				videoLink = videoInfo[-1]
				videoNameSplit = videoLink.split('/')
				videoName = videoName.replace('-',' ').replace('_',' ').title().strip()
				if (not 'http://ads.' in videoLink and not 'episode' in videoLink):
					searchRes.append([videoLink, videoName])
					
					videoName = videoNameSplit[-1].replace('-',' ').replace('_',' ').title().strip()
					searchRes.append([videoLink, videoName])
	else:
		print base_txt +  'Nothing was parsed from Total_Video_List' 
	
	# searchRes.sort(key=lambda name: name[1]) 
	searchRes = f2(searchRes)
	return searchRes