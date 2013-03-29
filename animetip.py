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
# python -c "execfile('animetip.py'); Episode_Listing_Pages('http://www.animetip.com/watch-anime/f/fairy-tail')"
#TEST2
# python -c "execfile('animetip.py'); Episode_Media_Link('http://www.animetip.com/watch-anime/f/fairy-tail/fairy-tail-episode-90.html')"
	
#animestream
# modded from --> <addon id="plugin.video.animecrazy" name="Anime Crazy" version="1.0.9" provider-name="AJ">

BASE_URL = 'http://www.animetip.com'

base_url_name = BASE_URL.split('www.')[1]
base_txt = base_url_name + ': '

aniUrls = ['http://www.animetip.com/watch-anime','http://www.animetip.com/anime-movies']

def Episode_Listing_Pages(url):
	# Identifies the number of pages attached to the original content page
	print base_txt + url
	link = grabUrlSource(url)	
	
	episodeListPage = url
	epList = Episode_Listing(episodeListPage)
	
	return epList
	
	
def Episode_Listing(url):
	# Extracts the URL and Page name of the various content pages
	link = grabUrlSource(url)	
	
	match=re.compile('<div class="title"><a href="(.+?)" rel="bookmark">(.+?)</a></div>').findall(link)	
	epList = []
	
	epNum = 0
	if(len(match) >= 1):
		for episodePageLink, episodePageName in match:
			season = '1'
			epNumPart = episodePageName.strip().split()
			for  epNum in reversed(epNumPart):
				if epNum.isdigit():
					epNum = int(epNum)
					break
			else:
				epNum = 0
			
			if 'season' in episodePageLink:
				season=re.compile('season-(.+?)-').findall(episodePageLink)[0]
			elif 'Season' in episodePageName.title():
				season=re.compile('Season (.+?) ').findall(episodePageName.title())[0]
			
			season = int(season)	
			episodePageName = episodePageName.title().replace(' - ',' ').replace(':',' ').replace('-',' ').strip()
			epList.append([episodePageLink , episodePageName, '', epNum, season])
	else:
		print base_txt +  'Nothing was parsed from Episode_Listing: ' + url
		
	return epList
	
	
def Episode_Page(url):
	# Identifies the number of mirrors for the content
	print base_txt +  url
	# link = grabUrlSource(url)	
	
	episodeMediaMirrors = url
	epMedia = Episode_Media_Link(episodeMediaMirrors)
		
	return epMedia
	
	
def Episode_Media_Link(url, mirror=1, part=1):
	# Extracts the URL for the content media file
	link = grabUrlSource(url).replace('<strong>','').replace('</strong>','').replace('</span>','').replace('\'','"')
	
	match=re.compile('<span class="postTabs_titles"><b>(.+?)</b><center><(.+?)src="(.+?)"').findall(link)
	epMedia = []
	
	if(len(match) >= 1):
		for mirrorPart, garbage, episodeMediaLink in match:
			if (not 'http://ads.' in episodeMediaLink):
				if (base_url_name in episodeMediaLink):
					episodeMediaLink = Media_Link_Finder(episodeMediaLink)
				
				
				mP_split = mirrorPart.split()
				if len(mP_split)>1:
					mirrorTxt = mP_split[0]
					partTxt = mP_split[1]
					
					if partTxt[0]=='p' and part > partTxt[1:]:
						mirror = mirror + 1
						
					if partTxt[0]=='p' and partTxt[1:].isdigit():
						part = int(partTxt[1:])
								
					
				else:				
					mirror = mirror + 1
					part = 1
						
				mirrorTxt = ''
				partTxt = ''
					
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


def Video_List_Searched(searchText,link):
	# Generate list of shows/movies based on the provide keyword(s)
	# urls = ['http://www.animetip.com/watch-anime','http://www.animetip.com/anime-movies']	
	
	searchRes = []		
	# match1=re.compile('<div id="ddmcc_container">(.+?)<div style="clear:both;"><!-- --></div>').findall(link)
	match=re.compile('<a(.+?)>'+searchText).findall(link)
	videoName = searchText
	if(len(match) >= 1):
		for linkFound in match:
			videoInfo = re.compile('href="(.+?)"').findall(linkFound)
			videoLink = videoInfo[-1]
			videoNameSplit = videoLink.split('/')
			videoName = videoNameSplit[-1].replace('-',' ').replace('_',' ').replace('.html','').title().strip()
			if (not 'http://ads.' in videoLink):
				searchRes.append([videoLink, videoName])
	# else:
		# print base_txt +  'Nothing was parsed from Video_List_Searched' 
					
	return searchRes

		
# def Total_Video_List(link):
	# Generate list of shows/movies
	
	# searchRes = []
	# match=re.compile('<a(.+?)>(.+?)</a>').findall(link)
	# if(len(match) >= 1):
		# for linkFound in match:
			# videoInfo = re.compile('href="(.+?)"').findall(linkFound[0])
			# if(len(videoInfo) >= 1):
				# videoLink = videoInfo[-1]
				# videoNameSplit = videoLink.split('/')
				# videoName = videoNameSplit[-1].replace('-',' ').replace('_',' ').replace('.html','').title().strip()
				# videoName = urllib.unquote(videoName)
				# if (not 'http://ads.' in videoLink):
					# searchRes.append([videoLink, videoName])
	# else:
		# print base_txt +  'Nothing was parsed from Total_Video_List' 
		
	# return searchRes
def Total_Video_List(link):
	# Generate list of shows/movies
	
	searchRes = []
	match1=re.compile('<div id="ddmcc_container">(.+?)<div id="sectionRight">').findall(link)
	if(len(match1) == 0):
		match1=re.compile('--><div class="block rounded">(.+?)<div id="sectionRight">').findall(link)

	match=re.compile('<a(.+?)>(.+?)</a>').findall(match1[0])
	if(len(match) >= 1):
		for linkFound, videoName in match:
			videoInfo = re.compile('href="(.+?)"').findall(linkFound)
			if(len(videoInfo) >= 1):
				videoLink = videoInfo[-1]
				videoNameSplit = videoLink.split('/')
				videoName = videoName.replace('-',' ').replace('_',' ').replace('.html','').replace('(Movie)','Movie').title().strip()
				if (not 'http://ads.' in videoLink):
					searchRes.append([videoLink, videoName])
					
					videoName = videoNameSplit[-1].replace('-',' ').replace('_',' ').replace('.html','').title().strip()
					searchRes.append([videoLink, videoName])
	else:
		print base_txt +  'Nothing was parsed from Total_Video_List' 
	
	# searchRes.sort(key=lambda name: name[1]) 
	searchRes = U2A_List(searchRes)
	searchRes = f2(searchRes)
	return searchRes