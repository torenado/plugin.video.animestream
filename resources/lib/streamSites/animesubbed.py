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
# python -c "execfile('animesubbed.py'); Episode_Listing_Pages('http://animesubbed.com/watch/series/fairy-tail')"
#TEST2
# python -c "execfile('animesubbed.py'); Episode_Page('http://animesubbed.com/watch/episodes/fairy-tail-episode-90')"
	
#animestream
# modded from --> <addon id="plugin.video.animecrazy" name="Anime Crazy" version="1.0.9" provider-name="AJ">

BASE_URL = 'http://animesubbed.com' # retired

base_url_name = BASE_URL.split('//')[1]
base_txt = base_url_name + ': '

# aniUrls = ['http://animesubbed.com/watch/animelist']
aniUrls = []
aniUrls.append(['http://animesubbed.com/watch/animelist','anime'])

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
	link = link.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('> <','><')

	match1=re.compile('<ul id="lcholder">(.+?)<div id="tab2" class="tab_content">').findall(link)	
	match=[]
	if(len(match1) >= 1):
		match=re.compile('<a href="(.+?)"').findall(match1[0])
	epList = []

	if(len(match) >= 1):
		for episodePageLink  in match:
			season = '1'
			
			episodeNameSplit = episodePageLink.split('/')
			# videoName = videoName.replace('-',' ').replace('_',' ').title().strip()
			episodePageName = episodeNameSplit[-1].replace('-',' ').replace('_',' ').title().strip()
			epNum = 0									
			if epNum == 0:
				epNumPart = episodePageName.strip().split()
				for  epNumTest in reversed(epNumPart):
					if epNumTest.isdigit():
						epNum = int(epNumTest)
						break						
			if epNum == 0:
				epNumPart = episodePageLink.strip().split('-')
				for  epNumTest in reversed(epNumPart):
					if epNumTest.isdigit():
						epNum = int(epNumTest)
						break
					
			
			if 'Season' in episodePageName.title():
				season=re.compile('Season (.+?) ').findall(episodePageName.title())[0]
			if '(S-' in episodePageName:
				season=re.compile('\(S-(.+?)\)').findall(episodePageName)[0]
			elif 'season' in episodePageLink:
				season=re.compile('season-(.+?)-').findall(episodePageLink)[0]
			
			
			season = int(season)
			episodePageName = episodePageName.title().replace(' Episode','').replace(' - ',' ').replace(':',' ').replace('-',' ').strip()
			epList.append([episodePageLink, episodePageName, '', epNum, season])
	else:
		print base_txt +  'Nothing was parsed from Episode_Listing: ' + url
		
	return epList
	
def Episode_Page(url):
	# Identifies the number of mirrors for the content
	print base_txt +  url
	
	link = grabUrlSource(url)

	match1=re.compile('<div class="tab_container">(.+?)<div class="adspl">').findall(link)
	match=re.compile('<(iframe|embed)(.+?)src="(.+?)"').findall(match1[0])		
	
	episodeMediaMirrors = url	
	epMedia = []
	ii=0
	if(len(match) >= 1):
		for garbage, garbage1, episodeMediaMirrors  in match:
			ii = ii + 1
			epMedia = epMedia + Episode_Media_Link(episodeMediaMirrors,ii)
	else:
		epMedia = epMedia + Episode_Media_Link(episodeMediaMirrors)
	
	return epMedia
		
def Episode_Media_Link(url, mirror=1):
	# Extracts the URL for the content media file
		
	episodeMediaLink = url
	epMedia = []
	part = 1
	if (not ('http://ads.' in episodeMediaLink or 'http://ad.' in episodeMediaLink or 'advertising' in episodeMediaLink or 'adserving' in episodeMediaLink or 'src="http://www.facebook.com/plugins/' in episodeMediaLink) ):
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
	
		
def Video_List_And_Pagination(url):
	link = grabUrlSource(url)	

	mostPop = []
	videoImg = ''
	if (not link == 'No Dice'):
		seriesBlock = re.compile('<div id="ddmcc_container">(.+?)<div style="clear:both;"><!-- --></div>').findall(link)[0]
		
		match=re.compile('<a href="(.+?)">(.+?)<').findall(seriesBlock)
		for videoLink, videoName in match:
			videoLink = BASE_URL + videoLink
			# videoName = urllib.unquote(videoName)
			videoNameSplit = videoLink.split('/')
			videoName = videoNameSplit[-1].replace('-',' ').replace('_',' ').title().strip()
			mostPop.append(['', videoName, videoLink])
	
	return mostPop
	
	
		
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
	match1=re.compile('<table(.+?)</table>').findall(link)	
	if(len(match1) > 0):
		match=re.compile('<a href="(.+?)"').findall(match1[0])
		if(len(match) >= 1):
			for videoLink in match:
				videoNameSplit = videoLink.split('/')
				# videoName = videoName.replace('-',' ').replace('_',' ').title().strip()
				videoName = videoNameSplit[-1].replace('-',' ').replace('_',' ').title().strip()
				if 'dubbed' in videoLink:
					videoName = videoName.replace('dubbed',' ').replace('Dubbed',' ').replace('  ',' ').strip() + ' (Dubbed)'
				if (not 'http://ads.' in videoLink and not 'episode' in videoLink):
					searchRes.append([videoLink, videoName])
		else:
			print base_txt +  'Nothing was parsed from Total_Video_List' 
	else:
		print base_txt +  'Nothing was parsed from Total_Video_List' 
	
	# searchRes.sort(key=lambda name: name[1]) 
	# searchRes = U2A_List(searchRes)
	# searchRes = f2(searchRes)
	return searchRes