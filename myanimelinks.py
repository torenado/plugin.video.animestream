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
# python -c "execfile('default.py'); Episode_Listing_Pages('http://www.myanimelinks.com/category/fairy-tail/')"
#TEST2
# python -c "execfile('default.py'); Episode_Media_Link('http://www.myanimelinks.com/fairy-tail-episode-90/')"
	
#animestream
# modded from --> <addon id="plugin.video.animecrazy" name="Anime Crazy" version="1.0.9" provider-name="AJ">
#dc=xbmcaddon.Addon(id='plugin.video.animestream')
addonPath=os.getcwd()
#artPath=addonPath+'/resources/art'
mozilla_user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

BASE_URL = 'http://myanimelinks.com'

base_url_name = BASE_URL.split('//')[1]
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
	req = urllib2.Request(url)
	req.add_header('User-Agent', mozilla_user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	link = ''.join(link.splitlines()).replace('\t','')
	
	match=re.compile("class='pages'>Page 1 of (.+?)</span>").findall(link)
	epList = []
	episodeListPage = url
	if(len(match) >= 1):
		for ii in range(1,int(match[0])+1):
			episodeListPage = url + '/page/' + str(ii)
			Episode_Listing(episodeListPage)
			epList = epList + Episode_Listing(episodeListPage)
	else:
		epList = epList + Episode_Listing(episodeListPage)
		
	return epList
	
	
def Episode_Listing(url):
	# Extracts the URL and Page name of the various content pages
	req = urllib2.Request(url)
	req.add_header('User-Agent', mozilla_user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	link = ''.join(link.splitlines()).replace('\t','')	
	
	match=re.compile('<h5><CENTER><a href="(.+?)">(.+?)</a>(.+?)background-image:url\((.+?)&amp;').findall(link)
	epList = []
	
	epNum = 0
	if(len(match) >= 1):
		for episodePageLink, episodePageName, garbage, episodeMediaThumb in match:
			epNumPart = episodePageName.strip().split()
			for  epNum in reversed(epNumPart):
				if epNum.isdigit():
					epNum = int(epNum)
					break
			else:
				epNum = 0

			epList.append([episodePageLink, episodePageName.title(), episodeMediaThumb.replace("'",""), epNum])
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
	
	match=re.compile('<br /><(iframe|embed) src="(.+?)"').findall(link)
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
			videoName = videoNameSplit[-2].replace('-',' ').title()
			if (not 'http://ads.' in videoLink and not 'episode' in videoLink):
				searchRes.append([videoLink, videoName])
				
	return searchRes