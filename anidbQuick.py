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
	base_txt = 'anidb.net: '
	print base_txt +  'Parsing anidb wishlist info'
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
				anidbWishlist.append([int(aid),name,eps])
	
	if(len(anidbWishlist) < 1):
		print base_txt +  'Nothing was parsed from Wishlist: '
	return anidbWishlist

def AID_Resolution(linkAID):
	base_txt = 'anidb.net: '	
	# print base_txt +  'Parsing anidb aid details'
	
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
			epNum='0'
			epName=''
			epAirdate=['','','']
			epIconimage=''
			description=''
			seasonNum='1'
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
				
			epNumAb = epNum
			epList.append([epNumAb,epName,epIconimage,description,seasonNum,epAirdate,epNum])
			epNum = ''
			epName = ''
	
	category = []
	match=re.compile('<categories>(.+?)</categories>').findall(linkAID)
	if(len(match)>=1):
		category = re.compile('<name>(.+?)</name>').findall(match[0])
		# print category
		
	epList.sort(key=lambda name: name[0], reverse=True)
	return [aid, iconimage, description, startdate, episodecount, adult, simAniList, synAniList, epList, category]

def AID_Search(linkAID='',searchText=''):
	base_txt = 'anidb.net: '	
	
	if len(searchText)>0:
		tvdbUrl = 'http://anisearch.outrance.pl/?task=search&query='
		seachTitle = '+'.join(searchText.split())

		url = tvdbUrl + '%22' + seachTitle + '%22'
		linkAID = grabUrlSource(url)
	
	serList = []
	
	match=re.compile('<anime (.+?)</anime>').findall(linkAID)
	if(len(match)>=1):
		# simAni=re.compile('<episode>(.+?)</episode>').findall(match)
		for aniSer in match:
			
			aid = re.compile('aid="(.+?)"').findall(aniSer)[0]
			match1=re.compile('CDATA\[(.+?)\]').findall(aniSer)
			if(len(match1)>=1):
				for name in match1:
					serList.append([aid, name])
	
	if len(serList)>0:
		print base_txt + 'anisearch.outrance.pl found mathces for: ' + searchText
		print serList
	else:
		print base_txt + 'anisearch.outrance.pl search revealed no matches for: ' + searchText
	
	return serList
	
def TVDBID_Resolution(aid,linkTVDB):
	base_txt = 'thetvdb.com: '	
	# print base_txt +  'Parsing TheTVDB id details'
	
	linkTVDB = linkTVDB.replace('></','> </')
	tvdbid=0
	banner=''
	fanart=''
	poster=''
	seriesdescr=''
	startdate=''
	genre = ''
	name = ''
	match=re.compile('<Series>(.+?)</Series>').findall(linkTVDB)
	if(len(match)>=1):
		tvdbid=re.compile('<id>(.+?)</id>').findall(match[0])[0]
		
		if '<SeriesName>' in match[0]:
			name=re.compile('<SeriesName>(.+?)</SeriesName>').findall(match[0])[0]
		if '<banner>' in match[0]:
			banner='http://www.thetvdb.com/banners/'+re.compile('<banner>(.+?)</banner>').findall(match[0])[0]
		if '<fanart>' in match[0]:
			fanart='http://www.thetvdb.com/banners/'+re.compile('<fanart>(.+?)</fanart>').findall(match[0])[0]
		if '<poster>' in match[0]:
			poster='http://www.thetvdb.com/banners/'+re.compile('<poster>(.+?)</poster>').findall(match[0])[0]
		if '<Overview>' in match[0]:
			seriesdescr=re.compile('<Overview>(.+?)</Overview>').findall(match[0])[0]
		if '<Genre>' in match[0]:
			genre=re.compile('<Genre>(.+?)</Genre>').findall(match[0])[0].split('|')
		if '<FirstAired>' in match[0]:
			try:
				startdate=re.compile('<FirstAired>(.+?)-(.+?)-(.+?)</FirstAired>').findall(match[0])[0]
			except:
				pass
				
	epList = []
	match=re.compile('<Episode>(.+?)</Episode>').findall(linkTVDB)
	print base_txt + str(len(match)) + ' episodes were parsed'
	if(len(match)>=1):
		# simAni=re.compile('<episode>(.+?)</episode>').findall(match)
		for TVDBEp in match:
			epName=''
			description=''
			epIconimage=''
			epNum1='0'
			seasonNum='1'
			epAirdate=['','','']
			if '<EpisodeName>' in TVDBEp:
				epName=re.compile('<EpisodeName>(.+?)</EpisodeName>').findall(TVDBEp)[0]
			if '<Overview>' in TVDBEp:
				description=re.compile('<Overview>(.+?)</Overview>').findall(TVDBEp)[0]
			if '<filename>' in TVDBEp:
				epIconimage='http://www.thetvdb.com/banners/'+re.compile('<filename>(.+?)</filename>').findall(TVDBEp)[0]
				
			if '<SeasonNumber>' in TVDBEp:
				seasonNum=re.compile('<SeasonNumber>(.+?)</SeasonNumber>').findall(TVDBEp)[0].replace(' ','')
				
			if '<absolute_number>' in TVDBEp:
				epNum1=re.compile('<absolute_number>(.+?)</absolute_number>').findall(TVDBEp)[0].replace(' ','')
			
			if  '<EpisodeNumber>' in TVDBEp:
				epNum2=re.compile('<EpisodeNumber>(.+?)</EpisodeNumber>').findall(TVDBEp)[0].replace(' ','')
				
			if len(epNum1)<1 and '<Combined_episodenumber>' in TVDBEp:
				epNum1=re.compile('<Combined_episodenumber>(.+?)</Combined_episodenumber>').findall(TVDBEp)[0].replace(' ','')
			
			
			if epNum1=='':
				epNum1 = '0'
			
			if epNum1.isdigit():
				epNumAb = int(epNum1)
			else:
				epNumAb = epNum1		
				
			if epNum2=='':
				epNum2 = '0'
			
			if epNum2.isdigit():
				epNum = int(epNum2)
			else:
				epNum = epNum2				
				
			if '<FirstAired>' in TVDBEp:
				try:
					airdateM=re.compile('<FirstAired>(.+?)-(.+?)-(.+?)</FirstAired>').findall(TVDBEp)
					if(len(airdateM)>=1):
						epAirdate=airdateM[0]
				except:
					pass
					
			epList.append([epNumAb,epName,epIconimage,description,seasonNum,epAirdate,epNum])
	
	
	epList.sort(key=lambda name: name[0], reverse=True)

	return [aid, tvdbid, banner, fanart, poster, epList, seriesdescr, startdate, genre, name]
	
def TVDBID_Search(linkTVDB='',searchText=''):
	base_txt = 'thetvdb.com: '	
	
	if len(searchText)>0:
		tvdbUrl = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='
		seachTitle = '+'.join(searchText.split())

		url = tvdbUrl + seachTitle
		linkTVDB = grabUrlSource(url)
	
	serList = []
	
	match=re.compile('<Series>(.+?)</Series>').findall(linkTVDB)
	if(len(match)>=1):
		# simAni=re.compile('<episode>(.+?)</episode>').findall(match)
		for TVDBEp in match:
			name = ''
			tvdbid = ''
			stardate = ''
			seriesdescr = ''
			banner = ''
			
			if '<SeriesName>' in TVDBEp:
				name=re.compile('<SeriesName>(.+?)</SeriesName>').findall(TVDBEp)[0]
			if '<seriesid>' in TVDBEp:
				tvdbid=re.compile('<seriesid>(.+?)</seriesid>').findall(TVDBEp)[0]
			# if '<Overview>' in TVDBEp:
				# seriesdescr=re.compile('<Overview>(.+?)</Overview>').findall(TVDBEp)[0]
			if '<FirstAired>' in TVDBEp:
				startdate=re.compile('<FirstAired>(.+?)-(.+?)-(.+?)</FirstAired>').findall(TVDBEp)[0]
			if '<banner>' in TVDBEp:
				banner='http://www.thetvdb.com/banners/'+re.compile('<banner>(.+?)</banner>').findall(TVDBEp)[0]
			
			serList.append([name, tvdbid, seriesdescr, stardate, banner ])
	
	if len(serList)>0:
		print base_txt + 'theTVDB.com found mathces for: ' + searchText
		print serList
	else:
		print base_txt + 'theTVDB.com search revealed no matches for: ' + searchText
	
	return serList
	
def WishlistAPI(link):
	# Grabs and parses the wishlist from anidb api.  User must set username and password in settings
	# ***WARNING: both this addon and anidb sends this password in the clear (plain text)
	base_txt = 'anidb.net: '
	print base_txt +  'Parsing anidb wishlist info'
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
	
def MyListSummaryAPI(link):
	# Grabs and parses the mylistsummary from anidb api.  User must set aniDB Login in settings
	# ***WARNING: both this addon and anidb sends this password in the clear (plain text)
	base_txt = 'anidb.net: '
	print base_txt +  'Parsing anidb mylistsummary info'
	anidbMylistsummary = []
		
	match=re.compile('<mylistitem (.+?)</mylistitem>').findall(link)
	if(len(match) >= 1):
		for aniLine in match:
			aid=re.compile('aid="(.+?)"').findall(aniLine)[0]			
			eps_wat=re.compile('<seencount>(.+?)</seencount>').findall(aniLine)
			
			if len(eps_wat)>0:
				eps_watched = eps_wat[0]
			else:
				eps_watched = 0
				
			anidbMylistsummary.append([aid,'',(eps_watched,'TBC')])
	
	if(len(anidbMylistsummary) < 1):
		print base_txt +  'Nothing was parsed from MyListSummaryAPI: '
	
	return anidbMylistsummary
	
def aid2Name(link,anidbWishlist):
	# Resolves anidb anime id numbers into titles
	base_txt = 'anidb.net: '
	
	print base_txt +  'Parsing anidb public wishlist info'
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