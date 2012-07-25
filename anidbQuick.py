import urllib,urllib2,re,sys,httplib
#import xbmcplugin,xbmcgui,xbmcaddon,urlresolver
import gzip, io
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging
from datetime import datetime
from utils import *
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

BASE_URL = 'http://anidb.net'

base_url_name = BASE_URL.split('//')[1]
base_txt = base_url_name + ': '	
	
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
	
	aid=0
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
	
	episodecount=0
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
		simAni=re.compile('<title xml:lang="x-jat"(.+?)>(.+?)<').findall(match[0])
		simAni=simAni + re.compile('<title xml:lang="en"(.+?)>(.+?)<').findall(match[0])
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
			
	
	epList = []
	match=re.compile('<episode (.+?)</episode>').findall(linkAID)
	print base_txt + str(len(match)) + ' episodes were parsed'
	if(len(match)>=1):
		# simAni=re.compile('<episode>(.+?)</episode>').findall(match)
		for aniEp in match:
			epNum=''
			epName=''
			epAirdate=['','','']
			if 'epno' in aniEp:
				epNum1=re.compile('<epno (.+?)>(.+?)<').findall(aniEp)[0][-1]
				if epNum1.isdigit():
					epNum = int(epNum1)
				else:
					epNum = epNum1
			if '<title xml:lang="en">' in aniEp:
				epName=re.compile('<title xml:lang="en">(.+?)</title>').findall(aniEp)[0]
			if 'airdate' in aniEp:
				airdateM=re.compile('<airdate>(.+?)-(.+?)-(.+?)</airdate>').findall(aniEp)
				if(len(airdateM)>=1):
					epAirdate=airdateM[0]
			if not len(epName)>0 and '<title xml:lang="x-jat">' in aniEp:
				epName=re.compile('<title xml:lang="x-jat">(.+?)</title>').findall(aniEp)
			epList.append([epNum,epName,epAirdate])
			epNum = ''
			epName = ''
	
	category = []
	match=re.compile('<categories>(.+?)</categories>').findall(linkAID)
	if(len(match)>=1):
		category = re.compile('<name>(.+?)</name>').findall(match[0])
		# print category
		
	epList.sort(key=lambda name: name[0], reverse=True)
	return [aid, iconimage, description, startdate, episodecount, adult, simAniList, synAniList, epList, category]

def TVDBID_Resolution(aid,linkTVDB):
	# print base_txt +  'Grabbing TheTVDB id details'
	linkTVDB = linkTVDB.replace('></','> </')
	tvdbid=0
	banner=''
	fanart=''
	poster=''
	match=re.compile('<Series>(.+?)</Series>').findall(linkTVDB)
	if(len(match)>=1):
		tvdbid=re.compile('<id>(.+?)</id>').findall(match[0])[0]
		if '<banner>' in match[0]:
			banner='http://www.thetvdb.com/banners/'+re.compile('<banner>(.+?)</banner>').findall(match[0])[0]
		if '<fanart>' in match[0]:
			fanart='http://www.thetvdb.com/banners/'+re.compile('<fanart>(.+?)</fanart>').findall(match[0])[0]
		if '<poster>' in match[0]:
			poster='http://www.thetvdb.com/banners/'+re.compile('<poster>(.+?)</poster>').findall(match[0])[0]
		
	epList = []
	match=re.compile('<Episode>(.+?)</Episode>').findall(linkTVDB)
	print base_txt + str(len(match)) + ' episodes were parsed'
	if(len(match)>=1):
		# simAni=re.compile('<episode>(.+?)</episode>').findall(match)
		for TVDBEp in match:
			epName=''
			description=''
			iconimage=''
			epNum1=''
			if '<EpisodeName>' in TVDBEp:
				epName=re.compile('<EpisodeName>(.+?)</EpisodeName>').findall(TVDBEp)[0]
			if '<Overview>' in TVDBEp:
				description=re.compile('<Overview>(.+?)</Overview>').findall(TVDBEp)[0]
			if '<filename>' in TVDBEp:
				iconimage='http://www.thetvdb.com/banners/'+re.compile('<filename>(.+?)</filename>').findall(TVDBEp)[0]
				
			if '<absolute_number>' in TVDBEp:
				epNum1=re.compile('<absolute_number>(.+?)</absolute_number>').findall(TVDBEp)[0].replace(' ','')
			
			if len(epNum1)<1 and '<Combined_episodenumber>' in TVDBEp:
				epNum1=re.compile('<Combined_episodenumber>(.+?)</Combined_episodenumber>').findall(TVDBEp)[0].replace(' ','')
			
			if len(epNum1)<1 and '<EpisodeNumber>' in TVDBEp:
				epNum1=re.compile('<EpisodeNumber>(.+?)</EpisodeNumber>').findall(TVDBEp)[0].replace(' ','')
			
			if epNum1=='':
				epNum1 = 0
			
			if epNum1.isdigit():
				epNum = int(epNum1)
			else:
				epNum = epNum1
			epList.append([epNum,epName,iconimage,description])
	
	
	epList.sort(key=lambda name: name[0], reverse=True)

	return [aid, tvdbid, banner, fanart, poster, epList]
	
	
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
			name = urllib.unquote(name)
			print name
			watchWishlist.append([aniLine[0],name])
	
	if(len(watchWishlist) < 1):
		print base_txt +  'Nothing was parsed from aid2Name: '
	
	return watchWishlist