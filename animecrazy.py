import urllib,urllib2,re,sys,httplib
#import xbmcplugin,xbmcgui,xbmcaddon,urlresolver
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging
from datetime import datetime
from utils import grabUrlSource
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

BASE_URL = 'http://www.animecrazy.net'

base_url_name = BASE_URL.split('www.')[1]
base_txt = base_url_name + ': '
	
	
def Episode_Listing_Pages(url):
	# Identifies the number of pages attached to the original content page
	print base_txt +  url

	link = grabUrlSource(url)
	
	match=re.compile('bottomSide"><a href="(.+?)" class="floatRight"').findall(link)
	if not '-reviews' in match[0]:
		episodeListPage = BASE_URL + match[0]
	else:
		episodeListPage = url
	epList = Episode_Listing(episodeListPage)
	
	return epList
	
	
def Episode_Listing(url):
	# Extracts the URL and Page name of the various content pages

	link = grabUrlSource(url)
	
	epList = []
	
	epNum = 0	
	match=re.compile('<div class="row">   <a class="floatLeft"(.+?)href="(.+?)">(.+?)</a>').findall(link)
	print base_txt +  url
	if(len(match) >= 1):
		for garbage, episodePageLink, episodePageName in match:
			epNumPart = episodePageName.strip().split()
			for  epNum in reversed(epNumPart):
				if epNum.isdigit():
					epNum = int(epNum)
					break
			else:
				epNum = 0
				
			epList.append([BASE_URL + episodePageLink , episodePageName.title(), '', epNum])
			
	match=re.compile('<div class="row"><a class="floatLeft"(.+?)href="(.+?)">(.+?)</a>').findall(link)
	if(len(match) >= 1):
		for garbage, episodePageLink, episodePageName in match:
			epNumPart = episodePageName.strip().split()
			for  epNum in reversed(epNumPart):
				if epNum.isdigit():
					epNum = int(epNum)
					break
			else:
				epNum = 0
			episodePageName = episodePageName.title().replace(' - ',' ').replace(':','').replace('-',' ').strip()
			epList.append([BASE_URL + episodePageLink , episodePageName, '', epNum])
	
	if(len(epList) < 1):
		print base_txt +  'Nothing was parsed from Episode_Listing: ' + url
		
	return epList
	
def Episode_Page(url):
	# Identifies the number of mirrors for the content
	print base_txt +  url

	link = grabUrlSource(url)
	
	match1=re.compile("Small Div alternate streaming(.+?)End of alternate streaming").findall(link)
	epMedia = []
	ii = 0
	match=re.compile('return encLink\(\'(.+?)\'\)').findall(match1[0])
	if(len(match) >= 1):
		for episodeMediaMirrors in match:
			ii = ii + 1
			#print base_txt +  'MIRROR ' + str(ii)
			episodeMediaMirrors = BASE_URL + episodeMediaMirrors
			epMedia = epMedia + Episode_Media_Link(episodeMediaMirrors)
	else:
		print base_txt +  'No MIRRORS were parsed from Episode_Page: ' + url
	
	return epMedia
	
def Episode_Media_Link(url, mirror=1):
	# Extracts the URL for the content media file

	link = grabUrlSource(url)
	
	streamingPlayer = re.compile('document.write\(unescape\(\'(.+?)\'\)\);').findall(link)
	frame = urllib.unquote_plus(streamingPlayer[0]).replace('\'','"').replace(' =','=').replace('= ','=')
	epMedia = []
	
	part = 1
	if link.find('class="part focused"'):
		part = 1
	else:
		match=re.compile('class="currentPart"(.+?)>(.+?)</a>').findall(link)
		print base_txt +  'Multi-part content' 
		if(len(match) >= 1):
			for garbage, part in match:
				print base_txt +  'Multi-part content: Found - Part '  + part
				part = int(part)
	
	match=re.compile('src="(.+?)"').findall(frame)
	if(len(match) >= 1):
		for episodeMediaLink in match:
			if (not 'http://ads.' in episodeMediaLink):
				if (base_url_name in episodeMediaLink):
					episodeMediaLink = Media_Link_Finder(episodeMediaLink)
					
				epMedia.append([base_url_name,episodeMediaLink, mirror, part])
				
	if(len(epMedia) < 1):
		print base_txt +  'Nothing was parsed from Episode_Media_Link: ' + url
	
	return epMedia
		
def Video_List_And_Pagination(url):

	link = grabUrlSource(url)

	mostPop = []
	# try:
		# numShows=re.compile('<div class="paginationDiv">(.+?)Last').findall(link)[0]
		# numShows=re.compile('offset/(.+?)">').findall(numShows)[-1]
		# numShows = int(numShows)
	# except:
		# numShows=90

	numShowsStart = 0
	match = re.compile('offset/(.+?)/').findall(url)
	if len(match) >= 1:
		numShowsStart = int(match[-1])
		
	numShowsEnd = 90
	if (numShowsStart < numShowsEnd):
		numShowsStart = 0
	else:
		numShowsEnd = numShowsStart + numShowsEnd
		
	print base_txt +  'numShowsStart: ' + str(numShowsStart)
	print base_txt +  'numShowsEnd: ' + str(numShowsEnd)
	
	url = url.split('offset/')[0]
	for ii in xrange(numShowsStart, numShowsEnd+30 , 15):
		mod_url = url + 'offset/' + str(ii) + '/'
		if ii > numShowsEnd:
			nextPage = mod_url
			videoName = '-- NEXT PAGE --'
			mostPop.append([nextPage, videoName])
		else:
			print base_txt +  mod_url
			link = grabUrlSource(url)
			match=re.compile('<img src="http://i.animecrazy.net/(.+?)"(.+?)<h1><a href="(.+?)">(.+?)</a></h1>').findall(link)
			#xbmc.executebuiltin("XBMC.Notification(Please Wait!,Retrieving video info and image,5000)")
			for videoImg, garbage, videoLink, videoName in match:
				mostPop.append(['http://i.animecrazy.net/' + videoImg, videoName])
	
	return mostPop
	
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

def Video_List_Searched_Direct(searchText, link):
	# Generate list of shows/movies based on the provide keyword(s)
	# url = 'http://www.animecrazy.net/search/' + searchText.replace(' ','_')

	# link = grabUrlSource(url)
	
	match=re.compile('<div class="top4">(.+?)<div class="clear"> </div></div>').findall(link)
	searchRes =[]
	if(len(match) >= 1):
		videoInfo=re.compile('<a href="/(.+?)"><p>(.+?)</p><img src="(.+?)" alt="" width="150px" /></a>').findall(match[0])
		#xbmc.executebuiltin("XBMC.Notification(Please Wait!,Retrieving video info and image,5000)")
		for videoLink, videoName, imgSrc in videoInfo:
			searchRes.append(['http://www.animecrazy.net/' + videoLink, videoName.strip()])
	
	match=re.compile('<div class="moreActionResults contentModule">(.+?)</div><div class="clear"></div></div>').findall(link)
	if(len(match) >= 1):
		videoInfo=re.compile('<p class="longTitle floatLeft"><a href="/(.+?)">(.+?)</p>').findall(match[0])
		for videoLink, videoName in videoInfo:
			searchRes.append(['http://www.animecrazy.net/' + videoLink, videoName.strip()])
	
	return searchRes
	
		
def Video_List_Searched(searchText, link):
	# Generate list of shows/movies based on the provide keyword(s)
	# url = 'http://www.animecrazy.net/anime-index/'
	
	searchRes = []
	match=re.compile('<a(.+?)>'+searchText).findall(link)
	videoName = searchText
	if(len(match) >= 1):
		for linkFound in match:
			videoInfo = re.compile('href="(.+?)"').findall(linkFound)
			videoLink = videoInfo[-1]
			videoNameSplit = videoLink.split('/')
			videoName = videoNameSplit[-2].replace('-',' ').replace('_',' ').title().strip()
			if (not 'http://ads.' in videoLink and not 'episode' in videoLink):
				searchRes.append([BASE_URL + videoLink, videoName.replace('Anime','').strip()])
	# else:
		# print base_txt +  'Nothing was parsed from Video_List_Searched' 
				
	return searchRes

		
def Total_Video_List(link):
	# Generate list of shows/movies
	
	searchRes = []
	match=re.compile('<a(.+?)>(.+?)</a>').findall(link)
	if(len(match) >= 1):
		for linkFound in match:
			videoInfo = re.compile('href="(.+?)"').findall(linkFound[0])
			if(len(videoInfo) >= 1):
				videoLink = videoInfo[-1]
				videoNameSplit = videoLink.split('/')
				if(len(videoNameSplit) > 1):
					videoName = videoNameSplit[-2].replace('-',' ').replace('_',' ').title().strip()
					if (not 'http://ads.' in videoLink):
						searchRes.append([BASE_URL + videoLink, videoName.replace('Anime','').strip()])
	else:
		print base_txt +  'Nothing was parsed from Total_Video_List' 
		
	return searchRes