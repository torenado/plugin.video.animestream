import urllib,urllib2,re,sys,httplib
#import xbmcplugin,xbmcgui,xbmcaddon,urlresolver
import gzip, io
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json
    
	
#animestream
# modded from --> <addon id="plugin.video.animecrazy" name="Anime Crazy" version="1.0.9" provider-name="AJ">
#dc=xbmcaddon.Addon(id='plugin.video.animestream')
addonPath=os.getcwd()
#artPath=addonPath+'/resources/art'
# https://sites.google.com/site/anidblist/anime-list.xml?attredirects=0
# http://www.thetvdb.com/api/1D62F2F90030C444/series/114801/all/en.zip <-- TheTVdb.com
mozilla_user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

BASE_URL = 'http://anidb.net'

base_url_name = BASE_URL.split('//')[1]
base_txt = base_url_name + ': '
   
def grabUrlSource(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', mozilla_user_agent)
	response = urllib2.urlopen(req)	
	link=response.read()
	if link[:2]=='\x1f\x8b':
		bi = io.BytesIO(link)
		gf = gzip.GzipFile(fileobj=bi, mode="rb")
		link = gf.read()
	response.close()
	link = ''.join(link.splitlines()).replace('\t','')
	
	return link
	
	
def Wishlist(link):
	# Grabs and parses the wishlist from anidb.  User must set username and password in settings
	# ***WARNING: both this addon and anidb sends this password in the clear (plain text)
	print base_txt +  'Grabbing anidb wishlist info'
	anidbWishlist = []
	link = link.replace('http://static.anidb.net/pics/anidb_pri_low.gif','')
	match=re.compile('<tr (.+?)</tr>').findall(link)
	if(len(match) >= 1):
		for aniLine in match:
			aid=re.compile('id="a(.+?)"').findall(aniLine)
			if(len(aid) >= 1):
				aid=re.compile('id="a(.+?)"').findall(aniLine)[0]
				name=re.compile('<label><a href=(.+?)>(.+?)</a></label>').findall(aniLine)[0][1]
				eps=re.compile('<td class="stats eps">(.+?)/(.+?)</td>').findall(aniLine)[0]
				
				if 'TBC' in eps[1]:
					gg = eps[0]
					eps=[]
					eps=(gg,'TBC')
				anidbWishlist.append([aid,name,eps])
	
	if(len(anidbWishlist) < 1):
		print base_txt +  'Nothing was parsed from Wishlist: '
	return anidbWishlist

def AID_Resolution(linkAID):
	# print base_txt +  'Grabbing anidb aid details'
	
	aid=''
	match=re.compile('<anime id="(.+?)"').findall(linkAID)
	if(len(match)>=1):
		aid=match[0]
	
	# print base_txt +  aid
		
	iconimage=''
	match=re.compile('<picture>(.+?)</picture>').findall(linkAID)
	if(len(match)>=1):
		iconimage='http://img7.anidb.net/pics/anime/' + match[0]
	
	# print base_txt +  iconimage
	
	description=''
	match=re.compile('<description>(.+?)</description>').findall(linkAID)
	if(len(match)>=1):
		description=match[0]
	
	# print base_txt +  description
	
	episodecount=''
	match=re.compile('<episodecount>(.+?)</episodecount>').findall(linkAID)
	if(len(match)>=1):
		episodecount=match[0]
	
	startdate=''
	match=re.compile('<startdate>(.+?)-(.+?)-(.+?)</startdate>').findall(linkAID)
	if(len(match)>=1):
		startdate=match[0]
	
	adult=''
	if ('18 Restricted' in linkAID):
		adult='Yes'
	else:
		adult='No'		
	
		
	synAniList = []
	match=re.compile('<titles>(.+?)</titles>').findall(linkAID)
	if(len(match)>=1):
		simAni=re.compile('<title xml:lang="en"(.+?)>(.+?)<').findall(match[0])
		for garbage, name in simAni:
			simAid = aid
			synAniList.append([simAid,name])	
	
		
	simAniList = []
	match=re.compile('<relatedanime>(.+?)</relatedanime>').findall(linkAID)
	if(len(match)>=1):
		simAni=re.compile('<anime id="(.+?)"(.+?)>(.+?)<').findall(match[0])
		for simAid, garbage, name in simAni:
			simAniList.append([simAid,name])	
	
	match=re.compile('<similaranime>(.+?)</similaranime>').findall(linkAID)
	if(len(match)>=1):
		simAni=re.compile('<anime id="(.+?)"(.+?)>(.+?)<').findall(match[0])
		for simAid, garbage, name in simAni:
			simAniList.append([simAid,name])
		
	return [aid, iconimage, description, startdate, episodecount, adult, simAniList, synAniList]
	
	
def WishlistAPI(link):
	# Grabs and parses the wishlist from anidb api.  User must set username and password in settings
	# ***WARNING: both this addon and anidb sends this password in the clear (plain text)
	print base_txt +  'Grabbing anidb wishlist info'
	anidbWishlist = []
		
	match=re.compile('<wishlistitem (.+?)</wishlistitem>').findall(link)
	if(len(match) >= 1):
		for aniLine in match:
			aid=re.compile('aid="(.+?)"').findall(aniLine)[0]
			type=re.compile('<type>(.+?)</type>').findall(aniLine)[0]
			anidbWishlist.append([aid,type])
	
	if(len(anidbWishlist) < 1):
		print base_txt +  'Nothing was parsed from WishlistAPI: '
	
	return anidbWishlist
	
def aid2Name(link,anidbWishlist):
	# Resolves anidb anime id numbers into titles
	
	print base_txt +  'Grabbing anidb public wishlist info'
	watchWishlist = []
	
	if(len(anidbWishlist) >= 1):
		for aniLine in anidbWishlist:
			searchText = 'aid="' + aniLine[0] + '"'
			aniLocation=re.compile(searchText+'(.+?)</anime>').findall(link)[0]
			aniLocation=re.compile('type="main" (.+?)/title>').findall(aniLocation)[0]
			name=re.compile('>(.+?)<').findall(aniLocation)[0]
			print name
			watchWishlist.append([aniLine[0],name])
	
	if(len(watchWishlist) < 1):
		print base_txt +  'Nothing was parsed from aid2Name: '
	
	return watchWishlist