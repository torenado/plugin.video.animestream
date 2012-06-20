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
# python -c "execfile('default.py'); Episode_Listing_Pages('http://www.animeflavor.com/index.php?q=node/4871')"
#TEST2
# python -c "execfile('default.py'); Episode_Media_Link('http://www.animeflavor.com/index.php?q=node/19518')"
	
#animestream
# modded from --> <addon id="plugin.video.animecrazy" name="Anime Crazy" version="1.0.9" provider-name="AJ">
#dc=xbmcaddon.Addon(id='plugin.video.animestream')
addonPath=os.getcwd()
#artPath=addonPath+'/resources/art'

BASE_URL = 'http://www.animeflavor.com'

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
	
	episodeListPage = url
	epList = Episode_Listing(episodeListPage)
	
	return epList
	
	
def Episode_Listing(url):
	# Extracts the URL and Page name of the various content pages
	link = grabUrlSource(url)	
	
	epBlockMatch=re.compile('<div class="relativity_child">(.+?)class="page-next"').findall(link)
	epBlockMatch1=re.compile('Watch episodes(.+?)Login</a> to post').findall(link)
	epBlockMatch2=re.compile('<div class="relativity_child">(.+?)<div class="block block-block"').findall(link)
	
	if len(epBlockMatch) >= 1:
		epBlock=epBlockMatch[0]
	elif len(epBlockMatch1) >= 1:
		epBlock=epBlockMatch1[0]
	elif len(epBlockMatch2) >= 1:
		epBlock=epBlockMatch2[0]
	else:
		print base_txt +  'Nothing was parsed from Episode_Listing (failed epBlock): ' + url
		return
			
	epList = []	
	
	epNum = 0
	episodeMediaThumb = ''
	
	match=re.compile('<a href="(.+?)">(.+?)</a>').findall(epBlock)
	if(len(match) >= 1):
		for episodePageLink, episodePageName in match:
			epNumPart = episodePageName.strip().split()
			for  epNum in reversed(epNumPart):
				if epNum.isdigit():
					epNum = int(epNum)
					break
			else:
				epNum = 0
			epList.append([BASE_URL + episodePageLink, episodePageName.title(), episodeMediaThumb.replace("'",""), epNum])
	else:
		print base_txt +  'Nothing was parsed from Episode_Listing: ' + url
		
	return epList
	
	
def Episode_Page(url):
	# Identifies the number of mirrors for the content
	print base_txt +  url
	link = grabUrlSource(url)	
	
	
	altBlock=re.compile('<div class="relativity_child">(.+?)</div>').findall(link)
	if(len(altBlock) >= 1):
		altBlock = altBlock[0]
	else:
		altBlock = ' '
		print base_txt +  'No Alternate videos found Episode_Page: ' + url
		
	epMedia = []
	episodeMediaMirrors = url
	# first video
	epMedia = epMedia + Episode_Media_Link(episodeMediaMirrors)
	
	#alternate video(s)
	match=re.compile('<a href="(.+?)">').findall(altBlock)
	if(len(match) >= 1):
		for episodeMediaMirrors in match:
			episodeMediaMirrors = BASE_URL + episodeMediaMirrors
			epMedia = epMedia + Episode_Media_Link(episodeMediaMirrors)

	return epMedia
	
	
def Episode_Media_Link(url, mirror=1):
	# Extracts the URL for the content media file
	link = grabUrlSource(url).lower().replace(' ','')
	
	epMedia = []
	part = 1

	match=re.compile('<(iframe|embed)src="(.+?)"').findall(link)
	if(len(match) >= 1):
		for garbage, episodeMediaLink in match:
			if ((not 'http://ads.' in episodeMediaLink) and (not 'animeflavor-gao-gamebox.swf' in episodeMediaLink)):
				if (base_url_name in episodeMediaLink):
					episodeMediaLink = Media_Link_Finder(episodeMediaLink)
					
				epMedia.append([base_url_name,episodeMediaLink, mirror, part])

	match=re.compile('<(iframe|embed)src=\'(.+?)\'').findall(link)
	if(len(match) >= 1):
		for garbage, episodeMediaLink in match:
			if ((not 'http://ads.' in episodeMediaLink) and (not 'animeflavor-gao-gamebox.swf' in episodeMediaLink)):
				if (base_url_name in episodeMediaLink):
					episodeMediaLink = Media_Link_Finder(episodeMediaLink)
					
				epMedia.append([base_url_name,episodeMediaLink, mirror, part])
				
	match=re.compile('config=flavor1\|file=(.+?)\|image').findall(link)
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
	videoImg = ''
	seriesBlock = re.compile('<table class="views-view-grid">(.+?)<div class="block block-block" id="block-block-17">').findall(link)[0]
	
	match=re.compile('<a href="(.+?)">(.+?)<').findall(seriesBlock)
	for videoImg, videoName in match:
		mostPop.append([BASE_URL + videoImg, videoName])
	
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
	
		
def Video_List_Searched(searchText,link):
	# Generate list of shows/movies based on the provide keyword(s)
	# urls = ['http://www.animeflavor.com/index.php?q=node/anime_list','http://www.animeflavor.com/index.php?q=anime_movies','http://www.animeflavor.com/index.php?q=cartoons']
	
	searchRes = []		
	videoName = searchText
	match=re.compile('<a(.+?)>'+searchText+'(.+?)<').findall(link)
	if(len(match) >= 1):
		for linkFound, videoName in match:
			videoInfo = re.compile('href="(.+?)"').findall(linkFound)
			videoLink = videoInfo[-1]
			videoNameSplit = videoLink.split('/')
			videoName = searchText + videoName.replace('</a>','')
			if (not 'http://ads.' in videoLink):
				searchRes.append([BASE_URL+videoLink, videoName])
	
	return searchRes