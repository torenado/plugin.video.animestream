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

BASE_URL = 'http://www.animefushigi.com'

base_url_name = BASE_URL.split('www.')[1]
base_txt = base_url_name + ': '

aniUrls = ['http://www.animefushigi.com/full-anime-list/','http://www.animefushigi.com/anime/movies/']

def Episode_Listing_Pages(url):
	# Identifies the number of pages attached to the original content page
	print base_txt + url
	link = grabUrlSource(url)
	
	match=re.compile("class='pages'>Page 1 of (.+?)</span>").findall(link)
	epList = []
	episodeListPage = url
	if(len(match) >= 1):
		for ii in range(1,int(match[0])+1):
			episodeListPage = url + '/page/' + str(ii)
			epList = epList + Episode_Listing(episodeListPage)
	else:
		epList = epList + Episode_Listing(episodeListPage)
		
	return epList
	
	
def Episode_Listing(url):
	# Extracts the URL and Page name of the various content pages
	link = grabUrlSource(url)	
	
	match=re.compile('<divclass="content_ep"><ahref="(.+?)">(.+?)</a></div>').findall(link)
	match1=re.compile('<div class="content_ep"><a href="(.+?)">(.+?)</a></div>').findall(link)
	pageTitle = re.compile('<title>(.+?)</title>').findall(link)[0].replace('  ',' ').replace('Watch','').replace('Episode List | Anime Fushigi','').strip()
	epList = []	
	
	epNum = 0
	if(len(match) >= 1):
		for episodePageLink, episodePageName in match:
			epNumPart = episodePageName.strip().split()
			for  epNum in reversed(epNumPart):
				if epNum.isdigit():
					epNum = int(epNum)
					break
			else:
				epNum = 0
			epList.append([episodePageLink, episodePageName.title(),'', epNum])
	elif(len(match1) >= 1):
		for episodePageLink, episodePageName in match1:
			epNumPart = episodePageName.strip().split()
			for  epNum in reversed(epNumPart):
				if epNum.isdigit():
					epNum = int(epNum)
					break
			else:
				epNum = 0
			epList.append([episodePageLink, episodePageName.title(),'', epNum])
	elif pageTitle:
		subLoc = pageTitle.find('|')
		pageTitle = pageTitle[subLoc:].replace('|','').strip()
		epNumPart = pageTitle.split()
		for  epNum in reversed(epNumPart):
			if epNum.isdigit():
				epNum = int(epNum)
				break
		else:
			epNum = 0
		episodePageName = pageTitle
		episodePageLink = url
		episodePageName = episodePageName.title().replace(' - ',' ').replace(':',' ').replace('-',' ').strip()
		epList.append([episodePageLink, episodePageName,'', epNum])
	
	if(len(epList) < 1):
		print base_txt +  'Nothing was parsed from Episode_Listing: ' + url
		
	return epList
	
	
def Episode_Page(url):
	# Identifies the number of mirrors for the content
	print base_txt +  url
	link = grabUrlSource(url)
	
	match=re.compile('"sources">MIRROR (.+?)</span>').findall(link)
	epMedia = []
	episodeMediaMirrors = url
	
	if(len(match) >= 1):
		mirror = 0
		for ii in range(1,int(match[-1])+1):
			mirror = mirror + 1
			episodeMediaMirrors = url + '/' + str(ii)
			epMedia = epMedia + Episode_Media_Link(episodeMediaMirrors, mirror)
	else:
		epMedia = epMedia + Episode_Media_Link(episodeMediaMirrors)
		
	return epMedia
	
	
def Episode_Media_Link(url, mirror=1, part=1):
	# Extracts the URL for the content media file
	link = grabUrlSource(url).replace(' ','')
	
	match=re.compile('<iframe(.+?)src="(.+?)"').findall(link)
	match1=re.compile('<iframesrc="(.+?)"').findall(link)
	epMedia = []
	
	if(len(match) >= 1):
		part = 0
		for garbage, episodeMediaLink in match:
			if (not 'http://ads.' in episodeMediaLink and not episodeMediaLink.endswith(('.gif','.jpg'))  and not 'facebook.com/plugins/like.php' in episodeMediaLink):
				part = part + 1
				if (base_url_name in episodeMediaLink):
					episodeMediaLink = Media_Link_Finder(episodeMediaLink)
					
				epMedia.append([base_url_name,episodeMediaLink, mirror, part])
	
	if(len(match1) >= 1):
		part = 0
		for episodeMediaLink in match1:
			if (not 'http://ads.' in episodeMediaLink and not '.gif' in episodeMediaLink and not 'facebook.com/plugins/like.php' in episodeMediaLink):
				part = part + 1
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
	match=re.compile('<a(.+?)>(.+?)</a>').findall(link)
	if(len(match) >= 1):
		for linkFound, videoName in match:
			videoInfo = re.compile('href="(.+?)"').findall(linkFound)
			if(len(videoInfo) >= 1):
				videoLink = videoInfo[-1]
				videoNameSplit = videoLink.split('/')
				videoName = videoName.replace('-',' ').replace('_',' ').title().strip()
				if (not 'http://ads.' in videoLink):
					searchRes.append([videoLink, videoName])
					
					videoName = videoNameSplit[-1].replace('-',' ').replace('_',' ').title().strip()
					searchRes.append([videoLink, videoName])
	else:
		print base_txt +  'Nothing was parsed from Total_Video_List' 
	
	# searchRes.sort(key=lambda name: name[1]) 
	searchRes = f2(searchRes)
	return searchRes