import urllib,urllib2,re,sys,httplib
#import xbmcplugin,xbmcgui,xbmcaddon,urlresolver
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging
from datetime import datetime
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
#dc=xbmcaddon.Addon(id='plugin.video.animestream')
addonPath=os.getcwd()
#artPath=addonPath+'/resources/art'

BASE_URL = 'http://www.animetip.com'

base_url_name = BASE_URL.split('www.')[1]
base_txt = base_url_name + ': '

	
mozilla_user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
def grabUrlSource(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', mozilla_user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	link = ''.join(link.splitlines()).replace('\t','')
	
	return link

def Episode_Listing_Pages(url):
	# Identifies the number of pages attached to the original content page
	print base_txt + url
	req = urllib2.Request(url)
	req.add_header('User-Agent', mozilla_user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	link = ''.join(link.splitlines()).replace('\t','')
	
	episodeListPage = url
	epList = Episode_Listing(episodeListPage)
	
	return epList
	
	
def Episode_Listing(url):
	# Extracts the URL and Page name of the various content pages
	req = urllib2.Request(url)
	req.add_header('User-Agent', mozilla_user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	link = ''.join(link.splitlines()).replace('\t','')	
	
	match=re.compile('<div class="title"><a href="(.+?)" rel="bookmark">(.+?)</a></div>').findall(link)	
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
			epList.append([episodePageLink , episodePageName.title(), '', epNum])
	else:
		print base_txt +  'Nothing was parsed from Episode_Listing: ' + url
		
	return epList
	
	
def Episode_Page(url):
	# Identifies the number of mirrors for the content
	print base_txt +  url
	req = urllib2.Request(url)
	req.add_header('User-Agent', mozilla_user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	link = ''.join(link.splitlines()).replace('\t','')
	
	episodeMediaMirrors = url
	epMedia = Episode_Media_Link(episodeMediaMirrors)
		
	return epMedia
	
	
def Episode_Media_Link(url, mirror=1):
	# Extracts the URL for the content media file
	req = urllib2.Request(url)
	req.add_header('User-Agent', mozilla_user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	link = ''.join(link.splitlines()).replace('\t','')
	
	match=re.compile('<center><(.+?)src="(.+?)"').findall(link)
	epMedia = []
	part = 1
	
	if(len(match) >= 1):
		for garbage, episodeMediaLink in match:
			if (not 'http://ads.' in episodeMediaLink):
				if (base_url_name in episodeMediaLink):
					episodeMediaLink = Media_Link_Finder(episodeMediaLink)
					
				epMedia.append([base_url_name,episodeMediaLink, mirror, part])
	
	if(len(epMedia) < 1):
		print base_txt +  'Nothing was parsed from Episode_Media_Link: ' + url
		
	return epMedia
	
def Media_Link_Finder(url):
	# Extracts the URL for the content media file
	req = urllib2.Request(url)
	req.add_header('User-Agent', mozilla_user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	link = ''.join(link.splitlines()).replace('\t','').replace(' ','')

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
			videoName = videoNameSplit[-1].replace('-',' ').replace('.html','').title()
			if (not 'http://ads.' in videoLink):
				searchRes.append([videoLink, videoName])
					
	return searchRes