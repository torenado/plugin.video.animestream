import urllib,urllib2,re,sys,httplib
import gzip, io
import xbmc,xbmcplugin,xbmcgui,xbmcaddon,urlresolver
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging
from datetime import datetime
try:
	import json
except ImportError:
	import simplejson as json


import utils
import anidbQuick

streamSiteList = ['anilinkz',
				'anime44',
				'animecrazy',
				'animeflavor',
				'animefreak',
				'animefushigi',
				'animetip',
				'myanimelinks']

for module in streamSiteList:
	vars()[module]=__import__(module)

try:
	import StorageServer
except:
	import storageserverdummy as StorageServer
cache = StorageServer.StorageServer("animestream", 24) # (Your plugin name, Cache time in hours)
cache7 = StorageServer.StorageServer("animestream", 24*7) # (Your plugin name, Cache time in hours)
	
#animestream
# modded from --> <addon id="plugin.video.animecrazy" name="Anime Crazy" version="1.0.9" provider-name="AJ">

dc=xbmcaddon.Addon(id='plugin.video.animestream')
addonPath=os.getcwd()

mozilla_user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
base_txt = 'animestream: '

# aniDB Login
uname = dc.getSetting('username')
passwd = dc.getSetting('pass')

# aniDB Public Wishlist
unid = dc.getSetting('uid')
pubpass = dc.getSetting('pubpass')

# Cartoon List URLs
cartoonUrls = ['http://www.animeflavor.com/index.php?q=cartoons',
				'http://anilinkz.com/cartoons-list']
				
# Most Poular/Recent List URLs
mostUrls = ['http://www.animecrazy.net/most-popular/',
			'http://www.animecrazy.net/most-recent/']

THUMBNAIL_VIEW_IDS = {'skin.confluence': 504,
					  'skin.aeon.nox': 551,
					  'skin.confluence-vertical': 500,
					  'skin.jx720': 52,
					  'skin.pm3-hd': 53,
					  'skin.rapier': 50,
					  'skin.simplicity': 500,
					  'skin.slik': 53,
					  'skin.touched': 500,
					  'skin.transparency': 53,
					  'skin.xeebo': 55}

def HOME():
	# XBMC: Default screen
	print base_txt + 'Create Home Screen'
	addDir('Anime','',10,'',numItems=3)
	addDir('Cartoons','',11,'',numItems=3)
	addDir('Search','',7,'',numItems=3)
	
	# searchRes = cache.cacheFunction(allAnimeList)

def ANIME():
	# XBMC: Anime screen
	print base_txt + 'Create Anime Screen'
	
	if (len(unid)>0 and len(pubpass)>0) :
		addDir('aniDB: Wishlist','',12,'')
	if (len(uname)>0 and len(passwd)>0) :
		addDir('aniDB: MyList - In Progress','',14,'')
		addDir('aniDB: MyList','',13,'')
	addDir('Most Popular','',1,'')
	addDir('Most Recent','',8,'')
	addDir('A-Z List','',6,'')
	addDir('Search','',7,'')

def CARTOON():
	# XBMC: Cartoon screen
	print base_txt + 'Create Cartoon Screen'
	addDir('Cartoons','',9,'')
	addDir('Search','',7,'')

def ANIDB_WISHLIST(url=''):
	# MODE 12 = ANIDB_WISHLIST

	print base_txt + 'Create Wishlist Screen'
	
	# content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
	# xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
		
	getSeriesList(watchWishlist,url,'1')
	
def ANIDB_MYLIST(url=''):
	# MODE 13 = ANIDB_MYLIST

	print base_txt + 'Create Mylist Screen'
	
	# content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
	# xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	
	myList = []
	mode = 1
	dirLength = len(watchMylistSummary)	
	print base_txt + '# of items: ' + str(dirLength)
	
	pb = xbmcgui.DialogProgress()
	pb.create('Generating List', 'aniDB MyList')
	
	ii=0
	for aidDB, name, eps in watchMylistSummary:
		ii += 1
		[searchText, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,'',str(aidDB))
		if len(searchText)>0:
			myList.append([aid,searchText,searchText.split()[0]])
		
		pb.update(int(ii/float(dirLength)*100), searchText)
	
	pb.close()
	myList.sort(key=lambda name: name[0], reverse=True) 
	myList.sort(key=lambda name: name[2]) 
	
	getSeriesList(myList,url,'1')
	
def ANIDB_MYLIST_WATCHING(url=''):
	# MODE 14 = ANIDB_MYLIST_WATCHING	

	print base_txt + 'Create In-Progress Screen'
	
	# content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
	# xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	
	myList = []
	mode = 1
	dirLength = len(watchMylistSummary)	
	print base_txt + '# of items to check: ' + str(dirLength)
	
	
	pb = xbmcgui.DialogProgress()
	pb.create('Generating List', 'aniDB MyList')
	
	ii=0
	for aidDB, name, eps in watchMylistSummary:
		ii += 1
		[searchText, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,'',str(aidDB))
		if len(searchText) > 0 and int(eptot) > int(epwatch):
			myList.append([aid,searchText,searchText.split()[0]])
			pb.update(int(ii/float(dirLength)*100), searchText)		
	
	pb.close()
	
	myList.sort(key=lambda name: name[0], reverse=True) 
	myList.sort(key=lambda name: name[2]) 
	
	getSeriesList(myList,url,'1')

def ANIDB_SIMILAR(aid_org):
	# MODE 121 = ANIDB_SIMILAR

	print base_txt + 'Create Similar Title(s) Screen'
	
	# content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
	# xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	
	# [searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_all_data(aid=aid_org)
	# [searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache.cacheFunction(get_all_data,'',aid_org)
	[searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,'',aid_org)
	
	dirLength = len(simAniList)
	print base_txt + '# of items: ' + str(dirLength)
	
	name = ''
	url = ''
	mode = 2
	iconimage = ''
	
	searchRes = []
	for aid, name in simAniList:
		searchRes.append([int(aid), name, ''])
		aid = None
		
	
	searchRes.sort(key=lambda name: name[0], reverse=True) 
	searchRes.sort(key=lambda name: name[1]) 
		
	getSeriesList(searchRes)
	
	skin = xbmc.getSkinDir()
	thumbnail_view = THUMBNAIL_VIEW_IDS.get(skin)
	if thumbnail_view:
		cmd = 'Container.SetViewMode(%s)' % thumbnail_view
		xbmc.executebuiltin(cmd)

def MOST_POPULAR(url=''):
	# Hardcoded to use animecrazy.net
	# MODE 1 = MOST_POPULAR
	
	print base_txt + 'Create Most Popular Screen'
	# content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	
	if url == '':
		url = 'http://www.animecrazy.net/most-popular/'
	mostPop = cache7.cacheFunction(animecrazy.Video_List_And_Pagination, url)
	
	returnMode = 1
	getSeriesList(mostPop,url,returnMode)

def CARTOON_LIST(url=''):
	# Hardcoded to use animeflavor.com
	# MODE 9 = CARTOON_LIST
	
	# content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	mostPop = []
	
	if url == '':
		for url in cartoonUrls:
			for streamList in streamSiteList:
				if streamList in url:
					siteBase = 'cache7.cacheFunction(' + streamList + '.Video_List_And_Pagination, url)'
					mostPop = mostPop + eval(siteBase)
			
	# mostPop = animeflavor.Video_List_And_Pagination(url)
	# mostPop = cache.cacheFunction(animeflavor.Video_List_And_Pagination, url)	
	
	
	name = ''
	nameTest = ''
	mostPop2 = []
	for iconimage, name, urls in mostPop:
		if name.startswith('The '):
			name = name[4:] + ', The'
		mostPop2.append([str(iconimage), name, urls])
	
	mostPop2.sort(key=lambda name: name[1])
	returnMode = 1
	
	getSeriesList(mostPop2,url,returnMode)

def MOST_RECENT(url=''):
	# Hardcoded to use animecrazy.net
	# MODE 8 = MOST_RECENT
	
	print base_txt + 'Create Most Recent Screen'
	# content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	
	if url == '':
		url = 'http://www.animecrazy.net/most-recent/'
	# mostRecent = animecrazy.Video_List_And_Pagination(url)
	# mostRecent = cache.cacheFunction(animecrazy.Video_List_And_Pagination, url)
	mostRecent = cache7.cacheFunction(animecrazy.Video_List_And_Pagination, url)
	returnMode = 8
	
	getSeriesList(mostRecent,url,returnMode)

def A_Z_LIST():
	# Hardcoded to use animecrazy.net
	# MODE 6 = A_Z_LIST
	
	url = 'http://www.animecrazy.net/alpha-'
	abc = [chr(i) for i in xrange(ord('A'), ord('Z')+1)]
	
	dirLength = len(abc)
	print base_txt + '# of items: ' + str(dirLength)
	for alphaB in abc:
		addDir(alphaB,url+alphaB.lower()+'/',61,'',numItems=dirLength)

def A_Z_LIST_VIDEOS(url):
	# Hardcoded to use animecrazy.net
	# MODE 61 = A_Z_LIST_VIDEOS
	
	# content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
	# xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	
	# azList = cache.cacheFunction(animecrazy.Video_List_And_Pagination, url)
	azList = cache7.cacheFunction(animecrazy.Video_List_And_Pagination, url)	
	returnMode = 61
	
	getSeriesList(azList,url,returnMode)

def TYPED_SEARCH():
		keyb = xbmc.Keyboard('', 'Enter search text')
		keyb.doModal()
		searchText = ''
		if (keyb.isConfirmed()):
				searchText = urllib.quote_plus(keyb.getText())
		
		searchText = searchText.title()
		SEARCH(searchText)

def SEARCH(searchText,aid='0'):
	# Searches the various websites for the searched content

	url = ''
	mode = 3
	searchRes = searchCollection(searchText,aid)	
	# print searchRes
	getSeriesList(searchRes,'',mode=mode)
	
	searchText = cleanSearchText(searchText)
	subLoc = searchText.rfind(':')
	if subLoc == -1:
		subLoc = searchText.rfind('-')
		if (subLoc > 0 and subLoc < len(searchText)):
			searchText =  searchText[:subLoc].strip() + ' [SEARCH]'
			addDir(searchText,'',2,'')
		else:
			subLoc = searchText.rfind(' ')
			if (subLoc > 0 and subLoc < len(searchText)):
				searchText =  searchText[:subLoc].strip() + ' [SEARCH]'
				addDir(searchText,'',2,'')
			elif searchText.rfind('-') > 0:
				searchText =  searchText.replace('-',' ').strip() + ' [SEARCH]'
				addDir(searchText,'',2,'')	
			elif searchText.rfind('!') > 0:
				searchText =  searchText.split('!')[0].strip() + ' [SEARCH]'
				addDir(searchText,'',2,'')	
			elif searchText.rfind('?') > 0:
				searchText =  searchText.split('?')[0].strip() + ' [SEARCH]'
				addDir(searchText,'',2,'')	
	elif (subLoc > 0 and subLoc < len(searchText)):
		searchText =  searchText[:subLoc].strip() + ' [SEARCH]'
		addDir(searchText,'',2,'')
		
	if (len(uname)>0 and len(passwd)>0) :
		if not aid.isdigit():
			aid = '0'
		if (int(aid)>0):
			addDir('-- SIMILAR TITLES --','',121,'',aid=aid)
	
	# if not cacheRefresh:
		# addDir('-- REFRESH -- ' + searchTextOrg,'',2,'',aid='REFRESH')

def cleanSearchText(searchText,skipEnc=False):
	# cleans up the text for easier searching
	# print base_txt + 'Clean up the search term: ' +searchText
	searchText = utils.unescape(searchText)
	
	if not skipEnc:
		subLoc = searchText.find('[')
		if subLoc > 0:
			searchText = searchText[:subLoc]
		subLoc = searchText.find('(')
		if subLoc > 0:
			searchText = searchText[:subLoc]
		
	searchText = searchText.replace('-- REFRESH -- ','')
	searchText = searchText.replace('(Movie/OVA)','').title().strip()
	searchText = searchText.replace('(Tv)','').title().strip()
	searchText = searchText.replace(' &Amp; ',' and ').title().strip()
	searchText = searchText.replace('((','(').replace('))',')')
	searchText = searchText.replace('(TV)','').replace('(OVA)','').replace('(Movie)','').replace('(Movie/OVA)','').title().strip()
	searchText = searchText.replace(':',' ').replace(' - ',' ').replace('_',' ').replace(' & ',' and ').strip()
	searchText = searchText.replace('~',' ').replace('?',' ').replace('!',' ').replace('.',' ').replace('  ',' ').replace('  ',' ').strip()
	searchText = searchText.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').title().strip()
	
	return searchText

def get_ani_detail(aid):
	linkAID = ' '
	if not aid.isdigit():
		aid = '0'
	if int(aid)>0 :
		time.sleep(2.1)
		urlPg = 'http://api.anidb.net:9001/httpapi?request=anime&client=xbmcscrap&clientver=1&protover=1&aid=%(aid)s' % {"aid": aid}
		linkAID = grabUrlSource(urlPg)
	
	return linkAID
		
def get_tvdb_detail(tvdbid):
	linkAID = ' '
	if int(tvdbid)>0 :
		time.sleep(2.1)
		urlPg = 'http://www.thetvdb.com/api/1D62F2F90030C444/series/%(tvdbid)s/all/en.xml' % {"tvdbid": tvdbid}
		linkAID = grabUrlSource(urlPg)
	
	return linkAID
		
def get_ani_aid(searchText):

	groupUrl = []
	groupUrl.append('https://sites.google.com/site/anidblist/anime-list.xml?attredirects=0')
	groupUrl.append('https://raw.github.com/torenado/plugin.video.animestream/master/anime-list_modded.xml')
	
	linkAID = ''
	for url in groupUrl:
		linkAID = linkAID + str(grabUrlSource(url))
	
	aid = '0'
	
	# aidList = get_ani_aid_list(linkAID)
	aidList = cache.cacheFunction(get_ani_aid_list,linkAID)

	print base_txt + 'Searching for aid: ' + searchText
	
	for aidFound, name, tvdbid, season in  aidList:
		name = cleanSearchText(name.replace(':',' ').replace('!',' ').replace('-',' ').replace('_',' ').replace('  ',' ').title().strip(),True)
		# name = name.replace(':',' ').replace('!',' ').replace('-',' ').replace('_',' ').replace('  ',' ').title().strip()
		if name == searchText:
			return str(aidFound)
	
	return aid
	
def search_aid_tvid(searchText, aidGet=False, tvdbGet=True):
	
	searchText = cleanSearchText(searchText)
	
	tvdbid = '0'
	aid = '0'
	
	tvdb_detail_search=[]
	if tvdbGet:			
		tvdbUrl = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='
		seachTitle = '+'.join(searchText.replace('.','').split())
		
		url = tvdbUrl + seachTitle
		linkTVDB = grabUrlSource(url)
	
		# tvdb_detail_search = anidbQuick.TVDBID_Search(linkTVDB)
		tvdb_detail_search = cache.cacheFunction(anidbQuick.TVDBID_Search,linkTVDB)
	
	if aidGet:
		tvdbUrl = 'http://anisearch.outrance.pl/?task=search&query='
		seachTitle = '+'.join(searchText.split())
		
		url = tvdbUrl + '%22' + seachTitle + '%22'
		linkAID = grabUrlSource(url)
		
		# tvdb_detail_search = anidbQuick.TVDBID_Search(linkTVDB)
		anidb_detail_search = cache.cacheFunction(anidbQuick.AID_Search,linkAID)
	
		for aidFound, name in anidb_detail_search:
			if cleanSearchText(name) == searchText:
				aid = aidFound
				break
	
	
	if len(tvdb_detail_search)==1 and int(aid)>0:
		tvdbid = str(tvdb_detail_search[0][1])
		name = str(tvdb_detail_search[0][0])
		print ' ---- '
		print '  <anime anidbid="' + aid + '" tvdbid="' + tvdbid + '" defaulttvdbseason="1">	<name>' + name + '</name>  </anime>'
		print ' ---- '
	elif len(tvdb_detail_search)==1:
		tvdbid = str(tvdb_detail_search[0][1])
		name = str(tvdb_detail_search[0][0])
		print ' ---- '
		print '  <anime anidbid="t' + tvdbid + '" tvdbid="' + tvdbid + '" defaulttvdbseason="1">	<name>' + name + '</name>  </anime>'
		print ' ---- '
		
	elif len(tvdb_detail_search)>1:
		print base_txt + 'Multiple matches found...Please choose one.'
		
	return aid,tvdbid
	
def get_tvdb_id(aid):

	groupUrl = []
	groupUrl.append('https://sites.google.com/site/anidblist/anime-list.xml?attredirects=0')
	groupUrl.append('https://raw.github.com/torenado/plugin.video.animestream/master/anime-list_modded.xml')
	
	linkAID = ''
	ll=''
	for url in groupUrl:
		linkAID = linkAID + str(grabUrlSource(url))
	
	tvdbid = ['0','1']
	
	# aidList = get_ani_aid_list(linkAID)
	aidList = cache.cacheFunction(get_ani_aid_list,linkAID)
	
	for aidFound, name, tvdbidFound, season in  aidList:
		if tvdbidFound.isdigit() and str(aidFound) == str(aid):
			return [tvdbidFound,season]	
	
	return tvdbid

def get_ani_aid_list(linkAID):

	# linkAID = linkAID.replace('> <','><').replace('>  <','><').replace('>   <','><').replace('>	<','><').replace('>	 <','><')
	linkAID = linkAID.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('> <','><')
	match=re.compile('<anime (.+?)</anime>').findall(linkAID)
	aniInfo = []
	aid = ''
	name = ''
	tvdbid = ''
	season='1'
	for aniInfoRaw in match:
		aniRow=re.compile('anidbid="(.+?)" tvdbid="(.+?)"(.+?)><name>(.+?)</name>').findall(aniInfoRaw)
		aid = aniRow[0][0]
		tvdbid = aniRow[0][1]
		aniRow=re.compile('defaulttvdbseason="(.+?)"').findall(aniInfoRaw)
		season = aniRow[0]
		aniRow=re.compile('<name>(.+?)</name>').findall(aniInfoRaw)
		if len(aniRow)>0:
			for name in aniRow:
				name = urllib.unquote(name).replace('-',' ').replace('_',' ').title().strip()
				aniInfo.append([aid, name, tvdbid, season])
		aid = ''
		name = ''
		tvdbid = ''
		season='1'
		
	aniInfo.sort(key=lambda aid: aid[0]) 
	return aniInfo

def get_aniDB_list(url=''):	
	
	
	xbmc.executebuiltin('XBMC.Notification(Retrieving Info!,aniDB Wishlist,5000)')
	
	if url == '':
		url = 'http://anidb.net/perl-bin/animedb.pl?show=mywishlist&uid=%(un)s&pass=%(pass)s' % {"un": unid, "pass": pubpass}
	
	multiPg = []	
	for pg in xrange(0,20):
		time.sleep(2.5)
		urlPg = url + '&page=' + str(pg)
		# print base_txt + urlPg
		linkPg = grabUrlSource(urlPg)
		if 'No results.' in linkPg:
			print base_txt + 'No more pages to parse'
			break
		else:
			multiPg.append(linkPg)
		
		link = ''.join(multiPg)
		
	watchWishlist = anidbQuick.Wishlist(link)	
	watchWishlist.sort(key=lambda name: name[0], reverse=True) 
	watchWishlist.sort(key=lambda name: name[1]) 
	
	return watchWishlist
	
def get_aniDB_mysummarylist(url=''):	
	
	xbmc.executebuiltin('XBMC.Notification(Retrieving Info!,aniDB MyList,5000)')
	
	if url == '':
		url = 'http://api.anidb.net:9001/httpapi?client=xbmcscrap&clientver=1&protover=1&request=mylistsummary&user=%(un)s&pass=%(pass)s' % {"un": uname, "pass": passwd}
	
	link = grabUrlSource(url)
		
	watchMylistSummary = anidbQuick.MyListSummaryAPI(link)	
	watchMylistSummary.sort(key=lambda name: name[1]) 
	
	return watchMylistSummary

def get_all_data(searchText='',aid='0',tvdbSer='0'):
	
	fanart = ''
	tvdbid = '0'
	description = ''
	year = 1902
	genre ='Animation'
	epwatch = '0'
	iconimage = ''
	epList = ['0','','','','1','']
	simAniList = []
	adult = 'No'
	synAniList = []
	eptot = ''
	season = '1'
	searchText1 = ''
	
	
	if searchText.endswith(', The'):
		searchText = 'The ' + searchText.replace(', The','')
	
	aidDB = '0'
	if aid.isdigit():
		aidDB = aid
	elif aid.startswith('t'):
		tvdbSer = aid[1:]
		
	if len(searchText)>0:
		aid = get_ani_aid(searchText)
		# aid = cache.cacheFunction(get_ani_aid,searchText)
		if aid.isdigit():
			aidDB = aid
		tvdbSer = get_tvdb_id(aid)[0]
		season = get_tvdb_id(aid)[1]
		
		if int(aidDB)==0 and int(tvdbSer)==0:			
			(aidDB , tvdbSer) = search_aid_tvid(searchText,True,True)
			# (aidDB , tvdbSer) = cache.cacheFunction(search_aid_tvid,searchText,True,True)
			if int(aidDB)>0:
				aid = aidDB
		elif int(aidDB)==0:			
			aidDB = search_aid_tvid(searchText,True,False)[0]
			# aidDB = cache.cacheFunction(search_aid_tvid,searchText,True,False)[0]
			if int(aidDB)>0:
				aid = aidDB
		elif int(tvdbSer)==0:			
			tvdbSer = search_aid_tvid(searchText)[1]
			# tvdbSer = cache.cacheFunction(search_aid_tvid,searchText)[1]
			
	elif (int(aidDB)>0 and len(uname)>0 and len(passwd)>0):
		tvdbSer = get_tvdb_id(aid)[0]
		season = get_tvdb_id(aid)[1]	
	
	if int(tvdbSer)>0:
		linkTVDB = get_tvdb_detail(tvdbSer)
		# linkTVDB = cache.cacheFunction(get_tvdb_detail,tvdbSer)
		
		tvdb_detail = anidbQuick.TVDBID_Resolution(aid,linkTVDB)
		# tvdb_detail = cache.cacheFunction(anidbQuick.TVDBID_Resolution,aid,linkTVDB)
		
		fanart = tvdb_detail[3]
		epList = tvdb_detail[5]
		iconimage = tvdb_detail[4]
		description = tvdb_detail[6]
		if len(tvdb_detail[7])>1:
			year = int(tvdb_detail[7][0])
		else:
			year = 1903			
		if len(tvdb_detail[8])>0:
			genre = " / ".join(tvdb_detail[8])
	
		if searchText=='':
			searchText1 = tvdb_detail[9]
	
	if (int(aidDB)>0 and len(uname)>0 and len(passwd)>0) :
		for aidWish, nameWish, epsWish in watchListTotal:
			if int(aidDB) == int(aidWish):
				epwatch = str(epsWish[0])
				break
				
		linkAID = get_ani_detail(aidDB)
		# linkAID = cache.cacheFunction(get_ani_detail,aidDB)
		
		ani_detail = anidbQuick.AID_Resolution(linkAID)
		# ani_detail = cache.cacheFunction(anidbQuick.AID_Resolution,linkAID)
	
		iconimage = ani_detail[1]
		if len(ani_detail[2])>0:
			description = ani_detail[2]
		if len(ani_detail[3])>1:
			year = int(ani_detail[3][0])
		else:
			year = 1904
				
		eptot = str(ani_detail[4])
		
		adult = ani_detail[5]
		
		simAniList = ani_detail[6]
		
		synAniList = ani_detail[7]
		
		if len(epList)<1:
			epList = ani_detail[8]
			
		if len(ani_detail[9])>0:
			genre = " / ".join(ani_detail[9])
			
		if searchText=='':
			searchText1 = ani_detail[10]
		
		
	if epwatch==eptot:
		playcount = 1
	else:
		playcount = 0
		
	if fanart=='':
		fanart=iconimage
	
	if searchText=='':
		searchText = searchText1
		
	allData = [searchText, aid, tvdbSer, description, fanart, iconimage, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount]
	
	return allData
	
def getSeriesList(mostPop,url='',returnMode='1',mode=2):

	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	
	name = ''
	nameTest = ''
	mostPop2 = []
	for iconimage, name, urls in mostPop:
		if not name=='':
			searchText = cleanSearchText(name)		
			if not nameTest == searchText:
				mostPop2.append([str(iconimage), name, urls])
			nameTest = cleanSearchText(name)
		else:
			mostPop2.append([str(iconimage), name, urls])
			
	
	dirLength = len(mostPop2)
	print base_txt + url
	print base_txt + '# of items: ' + str(dirLength)
	
	name = ''
	url = ''
	iconimage = ''
	for iconimage, name, url in mostPop2:
		searchText = cleanSearchText(name,True)
		
		aidDB = '0'
		if iconimage.isdigit():
			aidDB = iconimage
			
		# print base_txt + iconimage + ' ' + searchText
		if int(aidDB)>0:
			# [searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_all_data('',aidDB)
			# [searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache.cacheFunction(get_all_data,'',aidDB)
			[searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,'',aidDB)
			if name=='' or name.isspace():
				name = searchText2
				searchText = searchText2
		else:
			# [searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_all_data(searchText)
			# [searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache.cacheFunction(get_all_data,searchText)
			[searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,searchText)
		
		if not iconimage2 == '':
			iconimage = iconimage2
			
		if not 'http' in iconimage:
			iconimage = ''
		
		if searchText == '-- NEXT PAGE --' or searchText == '-- Next Page --':
			mode = int(returnMode)
			url = iconimage
			iconimage = ''
		
		if not 'http' in url:
			url = ''
		
		if (int(aidDB)>0 and len(uname)>0 and len(passwd)>0) :
			for aidWish, nameWish, epsWish in watchListTotal:
				if int(aidDB) == int(aidWish):
					epwatch = str(epsWish[0])
					break
		
		if int(epwatch)>0:
			print base_txt + str(searchText) + ' [' + epwatch + ' of ' + eptot + '] (aid=' + str(aid) + ', tvdbid='+ str(tvdbSer) +')'
			searchText = str(searchText) + ' [' + epwatch + ' of ' + eptot + ']'
			
			if str(aid)=='0' and int(tvdbSer)>0:
				aid = 't' + str(tvdbSer)
			
			if adult=='Yes':
				searchText = '[I]' + searchText + '[/I]'
			
			addDir(searchText,url,mode,iconimage,numItems=dirLength,aid=aid,descr=description,yr=year,genre=genre,totep=eptot, watchep=epwatch, fanart=fanart, plycnt=playcount)
		else:
			if str(aid)=='0' and tvdbSer==0:
				print base_txt + '---- ' + str(searchText) + ' (aid=' + str(aid) + ', tvdbid='+ str(tvdbSer) +')'
			else:
				print base_txt + str(searchText) + ' (aid=' + str(aid) + ', tvdbid='+ str(tvdbSer) +')'
				
			if str(aid)=='0' and int(tvdbSer)>0:
				aid = 't' + str(tvdbSer)
			
			if adult=='Yes':
				searchText = '[I]' + searchText + '[/I]'
				
			addDir(searchText,url,mode,iconimage,numItems=dirLength,aid=aid,descr=description,yr=year,genre=genre,fanart=fanart)
		
		
	skin = xbmc.getSkinDir()
	thumbnail_view = THUMBNAIL_VIEW_IDS.get(skin)
	if thumbnail_view:
		cmd = 'Container.SetViewMode(%s)' % thumbnail_view
		xbmc.executebuiltin(cmd)
	
def getEpisode_Listing_Pages(groupUrl,aid='0'):
	# Extracts the URL and Page name of the various content pages
	# MODE 3 = getEpisode_Listing_Pages
	
	# content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
	# xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
	
	iconimageSeries = ''
	epWishWatch = '0'
	tvdbSer = '0'
	fanart = ''
	
	aidDB = '0'
	if aid.isdigit():
		aidDB = aid
	
	# if int(aidDB)>0:
	[searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList1, season, adult, epwatch, eptot, playcount] = get_all_data(aid=aid)	
	# [searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList1, season, adult, epwatch, eptot, playcount] = cache.cacheFunction(get_all_data,'',aid)
	# [searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList1, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,'',aid)

	iconimageSeries = fanart
	epWishWatch = '0'
	
	if (int(aidDB)>0 and len(uname)>0 and len(passwd)>0) :
		for aidWish, nameWish, epsWish in watchListTotal:
			if int(aidDB) == int(aidWish):
				epWishWatch = int(epsWish[0])
				break	
	
	print base_txt + '... Season ' + season	
		
	epTvDetail = []
	try:
		for epNumAb,epName,epIconimage,description,seasonNum,epAirdate,epNum in epList1:
			# if int(season)==int(seasonNum):
			# print [epNum,epName,epIconimage,description,seasonNum,epAirdate]
			epTvDetail.append([epNumAb,epName,epIconimage,description,seasonNum,epAirdate,epNum])
	except:
		pass

	# print epTvDetail	
	# print epList1	
	
	try:
		urls = groupUrl.split(' <--> ')
	except:
		urls = groupUrl
		
	epListAll = []
	epList = []
	
	
	dirLength = len(urls)	
	print base_txt + '# of items: ' + str(dirLength)
	
	pb = xbmcgui.DialogProgress()
	pb.create('Generating List', 'Episodes')
	
	ii=0	
	for url in urls:
		ii += 1
		for streamList in streamSiteList:
			siteBase = streamList + '.base_url_name'
			site_base_url_name = eval(siteBase)
			if (site_base_url_name in url):
				# siteBase = streamList + '.Episode_Listing_Pages(url)'
				siteBase = 'cache.cacheFunction(' + streamList + '.Episode_Listing_Pages, url)'
				epList = eval(siteBase)		
			pb.update(int(ii/float(dirLength)*100), 'Grabbing Episodes from: ' + streamList)		
		epListAll = epListAll + epList
	
	pb.close()
		
	epListAllClean = []
	for episodePageLink, episodePageName, episodeMediaThumb, epNum, epSeason in epListAll:		
		episodePageName = episodePageName.title().replace(' Episode','').replace('#','').replace(' - ',' ').replace(':',' ').replace('-',' ').strip()
		epListAllClean.append([episodePageLink, episodePageName, '', int(epNum), int(epSeason)])
	
	epListAll = epListAllClean
	epListAll.sort(key=lambda a:(a[4],a[3]), reverse=True) 
	epListAll = f2(epListAll)
	epListAll.append(['','END','','',''])
	epListAll = utils.U2A_List(epListAll)
	
	# print epListAll
	
	dirLength = len(epListAll)
	print base_txt + '# of items: ' + str(dirLength)
	
	if int(aidDB)>0 and len(uname)>0 and len(passwd)>0:
		print base_txt + 'WATCHED ' + str(epsWish[0]) + ' of ' + str(epsWish[1])
	else:		
		print base_txt 
		
	epSeasonTest = ''
	epNumTest = ''
	iconimageTest = ''
	seaEpNumTest = ''
	name = ''
	url = ''
	mode = 4
	iconimage = ''
	for url, name, iconimage, epNum, epSeason in epListAll:
		name = name.title().replace('Episode','').replace('#','').replace(':',' ').replace('  ',' ').strip()
		if not epSeason == '':
			epSeason = int(epSeason) + int(season) - 1
		seaEpNum = str(epSeason) + 'x' + str(epNum)
		# try:
		if not seaEpNumTest == seaEpNum:
			if not epNumTest == '':
				if int(epWishWatch) >= int(epNumTest):
					playcount = 1
					try:
						print base_txt + nameTest + ' - Season:' + seasonNum + ' [WATCHED] ' + groupUrl
					except:
						print nameTest
				else:
					try:
						print base_txt + nameTest + ' - Season:' + seasonNum + groupUrl
					except:
						print nameTest
						
					nameTest = '[B]' + nameTest + '[/B]'
					
				addDir(nameTest,groupUrl,mode,iconimageTest,numItems=dirLength,descr=description,yr=yr,mo=mo,day=day,epSeason=epSeasonTest,epNum=epNumTest,fanart=fanart,plycnt=playcount)
			groupUrl = ''
			iconimageTest = ''
			description = ''
			seasonNum = ''
			fanart = iconimageSeries
			epSeasonTest = epSeason
			epNumTest = epNum
			seaEpNumTest = str(epSeasonTest) + 'x' + str(epNumTest)
			nameTest = name
			playcount = 0
			yr = 1900
			mo = 01
			day = 02
			# if not aid.isdigit():
				# aidDB = '0'
			# else:
				# aidDB = aid
				
			# if int(aidDB)>0 or int(tvdbSer)>0:
			if len(epTvDetail)>0:
				for epNumAb1,epName,epIconimage,description,seasonNum,epAirdate,epNum1 in epTvDetail:
					if str(epSeason) == '1':
						if str(epNum)==str(epNumAb1) and not str(seasonNum)=='0':
							nameTest = str(epSeason) + 'x' + str(epNum) + ' - ' + epName
							yr = epAirdate[0]
							mo = epAirdate[1]
							day = epAirdate[2]
							iconimageTest = epIconimage
							break
					elif not str(epSeason) == '0':
						if str(epNum)==str(epNumAb1) and str(epSeason)==str(seasonNum):
							nameTest = str(epSeason) + 'x' + str(epNum) + ' - ' + epName
							yr = epAirdate[0]
							mo = epAirdate[1]
							day = epAirdate[2]
							iconimageTest = epIconimage
							break
						
						if str(epNum)==str(epNum1) and str(epSeason)==str(seasonNum):
							nameTest = str(epSeason) + 'x' + str(epNum) + ' - ' + epName
							yr = epAirdate[0]
							mo = epAirdate[1]
							day = epAirdate[2]
							iconimageTest = epIconimage
							break
		
		if seaEpNumTest == seaEpNum:
			try:
				groupUrl = groupUrl +' <--> '+ url
			except:
				groupUrl = groupUrl
				print base_txt + 'URL not added in SEARCH() for ' + url + ' ' + str(epSeason) + 'x' + str(epNum)
				
			if len(iconimageTest)<1 and len(iconimage)>5:
				iconimageTest = iconimage
				
		# except:
			# print base_txt + 'Directory not created in SEARCH() for ' + url + ' ' + str(epNum)


	skin = xbmc.getSkinDir()
	thumbnail_view = THUMBNAIL_VIEW_IDS.get(skin)
	if thumbnail_view:
		cmd = 'Container.SetViewMode(%s)' % thumbnail_view
		xbmc.executebuiltin(cmd)			

def get_epMediaAll_2(groupUrl):
	
	
	try:
		urls = groupUrl.split(' <--> ')
	except:
		urls = groupUrl
	
	urls = f2(urls)
	epMediaAll = []
	epMedia = []
	
	
	dirLength = len(urls)	
	print base_txt + '# of items: ' + str(dirLength)
	
	pb = xbmcgui.DialogProgress()
	pb.create('Generating List', 'Streaming Media')
	
	ii=0	
	for url in urls:
		print base_txt + url
		ii += 1
		for streamList in streamSiteList:
			siteBase = streamList + '.base_url_name'
			site_base_url_name = eval(siteBase)
			if (site_base_url_name in url):
				# siteBase = streamList + '.Episode_Page(url)'
				siteBase = 'cache.cacheFunction(' + streamList + '.Episode_Page, url)'
				epMedia = eval(siteBase)
			pb.update(int(ii/float(dirLength)*100), 'Streaming Media from: ' + streamList)
		epMediaAll = epMediaAll + epMedia
		
	
	pb.close()
		
	epMediaAll_2=[]
	siteNnameTest=''
	mirrorTest=0 
	partTest=0
	for siteNname, url, mirror, part in reversed(epMediaAll):
		if not(siteNnameTest==siteNname and mirrorTest==mirror):
			totParts = part
			siteNnameTest = siteNname 
			mirrorTest = mirror
		epMediaAll_2.append([siteNname, url, mirror, part, totParts])
		
	epMediaAll_2.sort(key=lambda a:(a[0],a[2],a[3]))
	return epMediaAll_2
		
def getEpisode_PageMerged(groupUrl):
	# Extracts the URL for the content media file
	# MODE 4 = getEpisode_Page
	
	
	# epMediaAll_2 = get_epMediaAll_2(groupUrl)
	epMediaAll_2 = cache.cacheFunction(get_epMediaAll_2,groupUrl)
	
	url = ''
	mode = 5
	iconimage = ''
	mediaValid = []
	mediaInValid = []
	
	for siteNname, url, mirror, part, totParts in epMediaAll_2:
		name = ''
		# media_url = urlresolver.HostedMediaFile(url).resolve()
		try:
			media_url = urlresolver.HostedMediaFile(url).resolve()
			
			if not('http' in media_url):
				media_url = False
		except:
			media_url = False
			
		if (media_url == False and url.endswith('.flv')):
			media_url = url
		
		print 'Mirror: ' + str(mirror) + ' Part: ' + str(part)
		url = urllib.unquote(url)
		if media_url:
			media_url = urllib.unquote(media_url)
			print base_txt + media_url
			hostName = urlresolver.HostedMediaFile(url).get_host()
			if len(hostName)<1:
				hostName = media_url.split('/')[2]
			name = name + siteNname + ' -- Mirror ' + str(mirror) + ' - Part ' + str(part) + ' of ' + str(totParts) + ' (' + hostName + ')' 
			mediaValid.append([name,media_url,iconimage,siteNname,mirror])
		else:
			print base_txt + url + ' <-- VIDEO MAY NOT WORK'
			if len(url.split('/')) > 2:
				name = name + siteNname + ' -- Mirror ' + str(mirror) + ' - Part ' + str(part) + ' of ' + str(totParts) + ' (' + url.split('/')[2] + ') -- X'	
			else:
				name = name + siteNname + ' -- Mirror ' + str(mirror) + ' - Part ' + str(part) + ' of ' + str(totParts) + ' (' + url.split('/')[0] + ') -- X'
			mediaInValid.append([name,url,iconimage,siteNname,mirror])
	
	
	mediaValid.append(['','','','',''])
	
	mediaList = mediaValid + mediaInValid
	
	if len(mediaValid)>1:
		nameTest = mediaValid[0][0]
		siteNnameTest = mediaValid[0][3]
		mirrorTest = mediaValid[0][4]
		epPlaylist = '' 
		for name, media_url, iconimage, siteNname, mirror in mediaValid:
			if siteNnameTest==siteNname and mirrorTest==mirror:
				if not epPlaylist=='':
					epPlaylist = epPlaylist + ' <--> ' + media_url
				else:
					epPlaylist = media_url
			else:
				
				subLoc = nameTest.find('(')
				subLoc1 = nameTest.find(' -- ')
				if subLoc > 0:
					nameTest1 = nameTest[:subLoc1]
					nameTest = nameTest[subLoc:]
				nameTest = nameTest1 + ' -- Mirror ' + str(mirrorTest) + ' ' + nameTest + ' [' + str(len(epPlaylist.split(' <--> '))) +']'
				print base_txt + nameTest
				print base_txt + epPlaylist
				addPlaylist(nameTest,epPlaylist,42,'')
				nameTest = name
				siteNnameTest = siteNname 
				mirrorTest = mirror
				epPlaylist = media_url
	
	
	
	if(len(mediaValid) > 0):
		name = 'View List of -- INDIVIDUAL VIDEOS'
		url = ''
		mode = 43
		iconimage = ''
		addDir(name,groupUrl,mode,iconimage)
		
	if(len(mediaInValid) > 0):
		name = 'View List of -- POSSIBLY BROKEN VIDEOS'
		url = ''
		mode = 41
		iconimage = ''
		addDir(name,groupUrl,mode,iconimage)
		
def getEpisode_Page(groupUrl):
	# Extracts the URL for the content media file
	# MODE 43 = getEpisode_Page
	

	# epMediaAll_2 = get_epMediaAll_2(groupUrl)
	epMediaAll_2 = cache.cacheFunction(get_epMediaAll_2,groupUrl)
	
	url = ''
	mode = 5
	iconimage = ''
	mediaValid = []
	mediaInValid = []
	for siteNname, url, mirror, part, totParts in epMediaAll_2:
		name = ''
		# media_url = urlresolver.HostedMediaFile(url).resolve()
		try:
			media_url = urlresolver.HostedMediaFile(url).resolve()
			
			if not('http' in media_url):
				media_url = False
		except:
			media_url = False
			
		if (media_url == False and url.endswith('.flv')):
			media_url = url
		
		print 'Mirror: ' + str(mirror) + ' Part: ' + str(part)
		url = urllib.unquote(url)
		if media_url:
			media_url = urllib.unquote(media_url)
			print base_txt + media_url
			hostName = urlresolver.HostedMediaFile(url).get_host()
			if len(hostName)<1:
				hostName = media_url.split('/')[2]
			name = name + siteNname + ' -- Mirror ' + str(mirror) + ' - Part ' + str(part) + ' of ' + str(totParts) + ' (' + hostName + ')' 
			mediaValid.append([name,media_url,iconimage,siteNname,mirror])
		else:
			print base_txt + url + ' <-- VIDEO MAY NOT WORK'
			name = name + siteNname + ' -- Mirror ' + str(mirror) + ' - Part ' + str(part) + ' of ' + str(totParts) + ' (' + url.split('/')[2] + ') -- X'		
			mediaInValid.append([name,url,iconimage,siteNname,mirror])
			
	mediaList = mediaValid + mediaInValid
	for name, media_url, iconimage, siteNname, mirror in mediaValid:
		addLink(name,media_url,iconimage)
	
	if(len(mediaInValid) >= 1):
		name = 'View List of -- POSSIBLY BROKEN VIDEOS'
		url = ''
		mode = 41
		iconimage = ''
		addDir(name,groupUrl,mode,iconimage)

def getEpisode_Page_Fail(groupUrl):
	# Extracts the URL for the content media file
	# MODE 4 = getEpisode_Page
	

	# epMediaAll_2 = get_epMediaAll_2(groupUrl)
	epMediaAll_2 = cache.cacheFunction(get_epMediaAll_2,groupUrl)
	
	url = ''
	mode = 5
	iconimage = ''
	mediaValid = []
	mediaInValid = []
	for siteNname, url, mirror, part, totParts in epMediaAll_2:
		name = ''
		# media_url = urlresolver.HostedMediaFile(url).resolve()
		try:
			media_url = urlresolver.HostedMediaFile(url).resolve()
		except:
			media_url = False
			
		if (media_url == False and url.endswith('.flv')):
			media_url = url
		
		print 'Mirror: ' + str(mirror) + ' Part: ' + str(part)
		url = urllib.unquote(url)
		if media_url:
			media_url = urllib.unquote(media_url)
			print base_txt + media_url
			hostName = urlresolver.HostedMediaFile(url).get_host()
			if len(hostName)<1:
				hostName = media_url.split('/')[2]
			name = name + siteNname + ' -- Mirror ' + str(mirror) + ' - Part ' + str(part) + ' of ' + str(totParts) + ' (' + hostName + ')' 
			mediaValid.append([name,media_url,iconimage,siteNname,mirror])
		else:
			print base_txt + url + ' <-- VIDEO MAY NOT WORK'
			name = name + siteNname + ' -- Mirror ' + str(mirror) + ' - Part ' + str(part) + ' of ' + str(totParts) + ' (' + url.split('/')[2] + ') -- X'			
			mediaInValid.append([name,url,iconimage])
			
	for name, media_url, iconimage in mediaInValid:
		addLink(name,media_url,iconimage)

def allAnimeList(url=''):
	# Searches the various websites for the searched content
	
	searchSiteList = []
	
	for streamList in streamSiteList:
		siteOn = streamList + '_on'
		if (dc.getSetting(siteOn) == 'true'):
			siteBase = streamList + '.base_url_name'
			site_base_url = eval(siteBase)
			searchSiteList.append([streamList, site_base_url])
	
	
	if(len(searchSiteList) < 1):
		searchSiteList = [animecrazy.base_url_name]
		print base_txt +  'No sites choosen in the settings.  Using animecrazy.net'
		
	
	searchRes = []
	for streamList, url in searchSiteList:
		xbmc.executebuiltin('XBMC.Notification(Retrieving Info!,'+ url +',5000)')
		link = ''
		siteBase = streamList + '.base_url_name'
		site_base_url = eval(siteBase)
		if (site_base_url in url):
				siteBase = streamList + '.aniUrls'
				site_aniUrls = eval(siteBase)
				for aniUrl in site_aniUrls:
					print base_txt + aniUrl
					link = grabUrlSource(aniUrl)	
					try:					
						siteBase = streamList + '.Total_Video_List(link)'
						searchRes = searchRes + eval(siteBase)
					except:
						print base_txt + 'FAILED - ' + aniUrl + ' failed to load allAnimeList()'
					searchRes = utils.U2A_List(searchRes)
	
	try:
		searchRes.sort(key=lambda name: name[1]) 
	except:
		print base_txt + 'FAILED - Sorting in allAnimeList()'
		
	searchRes = f2(searchRes)
			
	return searchRes
	
def allSearchList(searchText):
	
	searchText_mod1 = searchText + ' '
	searchText_mod2 = ' ' + searchText
	url = ''
	# searchRes = allAnimeList()
	searchRes = cache.cacheFunction(allAnimeList)
	# print searchRes
	searchResults = []
	for possLink in searchRes:
		
		if not possLink[1]==None and not possLink[1].startswith('<') and possLink[0].startswith('http'):
			if len(searchText)==1:
				if searchText_mod1 in possLink[1]:
					searchResults.append(possLink)
					
				if searchText_mod2 in possLink[1]:
					searchResults.append(possLink)
			
			else:
				if searchText in possLink[1]:
					searchResults.append(possLink)
	
	return searchResults
	
def searchCollection(searchText,aid='0'):
	# Searches the various websites for the searched content
	searchText = cleanSearchText(searchText)
	print base_txt + 'Searching for ... ' + searchText
	
	# searchRes = allSearchList(searchText)
	searchRes = cache.cacheFunction(allSearchList,searchText)
	
	searchTextOrg = searchText
	
	if (len(uname)>0 and len(passwd)>0):
	
		# linkAID = get_ani_detail(aid_org)
		# linkAID = cache.cacheFunction(get_ani_detail,aid)
		
		# ani_detail_org = anidbQuick.AID_Resolution(linkAID)
		# ani_detail_org = cache.cacheFunction(anidbQuick.AID_Resolution,linkAID)
		
		
		cacheRefresh = False
		aidDB = '0'
		if aid.isdigit():
			aidDB = aid
		# elif aid == 'REFRESH':
			# print base_txt + 'Refreshing: ' + searchText
			# cacheRefresh = True
			# name = cache._generateKey(get_all_data,'',aidDB)
			# print base_txt + 'Refreshing: ' + name
			# cache.cacheDelete(name)
			
		# [searchText1, aid1, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList1, epList, season, adult, epwatch, eptot, playcount] = get_all_data('',aidDB)
		# [searchText1, aid1, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList1, epList, season, adult, epwatch, eptot, playcount] = cache.cacheFunction(get_all_data,'',aidDB)
		[searchText1, aid1, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList1, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,'',aidDB)
		
		searchAlts = []
		if (int(aidDB)>0 and len(synAniList1)>0):
			for aidAlt, name in synAniList1:
				subLoc = name.find('(')
				if subLoc > 0:
					name = name[:subLoc]
				name = urllib.unquote(name).title()
				print base_txt + 'Searching for ... ' + name
				searchRes = searchRes + cache.cacheFunction(allSearchList,name)
				searchAlts.append(name)
				if name.find(' ') > 0:
					searchAlts.append(name.replace(' ',''))
				if name.find(':') > 0:
					searchAlts.append(name.replace(':',' '))
					searchAlts.append(name.replace(':',' ').replace('  ',' '))
					searchAlts.append(name.replace(':',''))
					searchAlts.append(name.replace(':','').replace('!',''))
				if name.find('\'') > 0 or name.find('`') > 0:
					searchAlts.append(name.replace('\'','').replace('`','').replace(':',' ').title())
					searchAlts.append(name.replace('\'','').replace('`','').replace(':',' ').replace('  ',' ').title())
					searchAlts.append(name.replace('\'','').replace('`','').replace(':','').title())
				if name.find('?') > 0 or name.find('!') > 0:
					searchAlts.append(name.replace('?','').replace('!',''))
				if name.find('-') > 0:
					searchAlts.append(name.replace('-',' '))
					searchAlts.append(name.replace('-',' ').replace('  ',' '))
					searchAlts.append(name.replace('-',''))
				if name.find('~') > 0:
					searchAlts.append(name.replace('~',''))
				if name.startswith('The'):
					searchAlts.append(name.replace('The ',''))
				if name.find('.') > 0 or name.find(',') > 0:
					searchAlts.append(name.replace('.','').replace(',',''))
					searchAlts.append(name.replace(',',''))
					searchAlts.append(name.replace('.',''))
		
			searchAlts = f2(searchAlts)
			print base_txt + 'Searching ' + str(len(searchAlts)) + ' alternate names + variations'
			for nameSearch in searchAlts:
				print base_txt + 'Searching for ... ' + nameSearch
				searchRes = searchRes + cache.cacheFunction(allSearchList,nameSearch)
		
	searchRes.append(['','zzzzzzEND'])
	
	tempsearchRes = searchRes
	searchRes = []
	for url, name in tempsearchRes:
		name = name.title().replace(' - ',' ').replace(':',' ').replace('2Nd','2').strip()
		if 'Movies' in name:
			name = name.replace(' Movies',' ').strip() + ' (Movie/OVA)'
		elif 'The Movie' in name:
			name = name.replace(' The Movie',' ').replace(' Movie',' ').strip() + ' (Movie/OVA)'
		elif 'Movie' in name:
			name = name.replace(' Movie',' ').replace(' Movie',' ').strip() + ' (Movie/OVA)'
		
		if 'movie' in url:
			name = name.strip() + ' (Movie/OVA)'
			
		if 'Ova' in name:
			name = name.replace(' Ova',' ').strip() + ' (Movie/OVA)'
		if 'Oav' in name:
			name = name.replace(' Oav',' ').strip() + ' (Movie/OVA)'
		if 'Featurettes' in name:
			name = name.replace(' Featurettes',' ').strip() + ' (Movie/OVA)'
		if 'ova' in url:
			name = name.strip() + ' (Movie/OVA)'
			
		if 'Tv Special' in name:
			name = name.replace(' Tv Special',' ').strip() + ' (Movie/OVA)'
			
		if ' Special ' in name:
			name = name.replace(' Special ',' ').strip() + ' (Movie/OVA)'
		
		name = name.replace('(Movie) (Movie)','(Movie/OVA)')
		name = name.replace('(Movies) (Movie)','(Movie/OVA)')
		name = name.replace('2 (Movie)','(Movie/OVA)')
		name = name.replace('(Oav)','(Movie/OVA)')
		name = name.replace('(Ova)','(Movie/OVA)')
		name = name.replace('(Movie) (OVA)','(Movie/OVA)')
		name = name.replace('(OVA) (Movie)','(Movie/OVA)')
		name = name.replace('(Ova) (Ova)','(Movie/OVA)')
		name = name.replace('(OVA) (OVA)','(OVA)').replace('(OVA) (OVA)','(Movie/OVA)')
		name = name.replace('(Movie/OVA) (Movie/OVA)','(Movie/OVA)').replace('(Movie/OVA) (Movie/OVA)','(Movie/OVA)')
		name = name.replace('2Nd Season','2')
		name = name.replace('Second Season','2')
		name = name.replace('2Season','2')
		name = name.replace('2season','2')
		name = name.replace('Iii','3')
		name = name.replace('Ii','2')
		name = name.replace(' Season',' ')
		name = name.replace(' Vs.',' Vs')
		name = name.replace('English Dubbed Online Free','(Dubbed)')
		name = name.replace('Dubbed','(Dubbed)')
		# name = name.replace('Shippuden','Shippuuden')
		# name = name.replace('Shipuden','Shippuuden')
		# name = name.replace('Shipuuden','Shippuuden')
		name = name.replace('Dragonball','Dragon Ball')
		name = name.replace('Diamonddust','Diamond Dust')
		name = name.replace('Highschool','High School')
		# name = name.replace('Piecedefeat','Piece Defeat')
		# name = name.replace('Pieceadventure','Piece Adventure')
		# name = name.replace('Pieceopen','Piece Open')
		# name = name.replace('Pieceproect','Piece Protect')
		# name = name.replace('Pieceromance','Piece Romance')
		# name = name.replace('Piecethe','Piece The')
		name = name.replace('&#039;',"'")
		name = name.replace('&#8217;',"'")
		name = name.replace('&#8211;',' ')
		name = name.replace("'",'')
		name = name.replace('`','')
		name = name.replace('~',' ')
		name = name.replace('^',' ')
		name = name.replace('!',' ')
		name = name.replace(',',' ')
		name = name.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ')
		name = name.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ')
		name = name.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ')
		searchRes.append([url,name])
	
	
	searchRes = utils.U2A_List(searchRes)
	try:
		searchRes.sort(key=lambda name: name[1]) 
	except:
		print base_txt + 'Sorting failed in SEARCH()'
	
	searchRes = f2(searchRes)
	
	nameTest = ''
	url = ''
	mode = 3
	iconimage = ''
	
	# print searchRes
	# searchRes = filter(None, searchRes)
	# print searchRes
	
	
	# watchWishlist = get_aniDB_list()
	# watchWishlist = cache.cacheFunction(get_aniDB_list)
	
	searchCollect = []
	dirLength = len(searchRes)
	print base_txt + '# of items: ' + str(dirLength)
	pb = xbmcgui.DialogProgress()
	pb.create('Generating List', '# of items: ' + str(dirLength))
	ii=0
	for url, name in searchRes:
		ii+=1
		name = name.title().strip()
		if not nameTest.replace(' ','').title() == name.replace(' ','').title():
			if not nameTest == '':
				nameTest2 = cleanSearchText(nameTest)
				# [searchText2, aidSer, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_all_data(nameTest2)
				# [searchText2, aidSer, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache.cacheFunction(get_all_data,nameTest2)
				[searchText2, aidSer, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,nameTest2)
					
				# if int(epwatch)>0:
					# print base_txt + nameTest + ' [' + epwatch + ' of ' + eptot + '] (aid=' + aidSer + ', tvdbid='+ str(tvdbSer) +') <--> ' + groupUrl
					# nameTest = nameTest + ' [' + epwatch + ' of ' + eptot + ']'
					# addDir(nameTest,groupUrl,mode,iconimage,numItems=dirLength,aid=aidSer,descr=description,yr=year,genre=genre,totep=eptot, watchep=epwatch, fanart=fanart, plycnt=playcount)
				# else:
					# print base_txt + nameTest + ' (aid=' + aidSer + ', tvdbid='+ str(tvdbSer) +') <--> ' + groupUrl
					# addDir(nameTest,groupUrl,mode,iconimage,numItems=dirLength,aid=aidSer,genre=genre,fanart=fanart)
				
				
				aidSerDB = aidSer
				if aidSer.isdigit():
					aidSerDB = int(aidSer)
					
				firstName = nameTest.split()
				searchCollect.append([aidSerDB, nameTest, groupUrl, firstName[0]])
				
			groupUrl = ''
			nameTest = name
		
		if nameTest == name:
			groupUrl = groupUrl +' <--> '+ url
		
		pb.update(int(ii/float(dirLength)*100), str(ii) + ' of ' + str(dirLength) + ': ' + nameTest)
	pb.close()
		
	searchCollect_2 = [] + searchCollect
	try:
		searchCollect_2.sort(key=lambda name: name[0], reverse=True) 
		searchCollect_2.sort(key=lambda name: name[3]) 
	except:
		print base_txt + 'Sorting failed in SEARCH() regarding searchCollect_2'
	searchCollect_2.append(['', 'Zzzzzzend', '',''])
	
	combinedSearchCollect=[]
	aidSerTest=''
	nameTest=''
	groupUrls=''
	for aidSer, name, groupUrl, firstName in searchCollect_2:
		# print base_txt + str(aidSer)
		if not aidSerTest == aidSer or str(aidSerTest) == '0':
			if not aidSerTest == '':		
				combinedSearchCollect.append([str(aidSerTest), nameTest, groupUrls])
				
			groupUrls = ''
			aidSerTest = aidSer
			nameTest = name
		if aidSerTest == aidSer and not str(aidSerTest) == '0':
			groupUrls = groupUrls +' <--> '+ groupUrl
		elif aidSerTest == aidSer and str(aidSerTest) == '0':
			combinedSearchCollect.append([str(aidSerTest), nameTest, groupUrl])
	
	print combinedSearchCollect
	# return searchCollect
	return combinedSearchCollect
	
def PLAYLIST_VIDEOLINKS(url,name):
	ok=True
	playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playList.clear()
	#time.sleep(2)
	links = url.split(' <--> ')
	pDialog = xbmcgui.DialogProgress()
	ret = pDialog.create('Loading playlist...')
	totalLinks = len(links)
	loadedLinks = 0
	remaining_display = 'Videos loaded :: [B]'+str(loadedLinks)+' / '+str(totalLinks)+'[/B] into XBMC player playlist.'
	pDialog.update(0,'Please wait for the process to retrieve video link.',remaining_display)
	
	iconimage=''
	
	for videoLink in links:
		name = name + ' (' + str(loadedLinks) + ')'
		liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
		liz.setInfo( type="Video", infoLabels={ "Title": name } )
		print base_txt + name + ' - ' + videoLink
		playList.add(url=videoLink, listitem=liz)
		loadedLinks = loadedLinks + 1
		percent = (loadedLinks * 100)/totalLinks
		#print percent
		remaining_display = 'Videos loaded :: [B]'+str(loadedLinks)+' / '+str(totalLinks)+'[/B] into XBMC player playlist.'
		pDialog.update(percent,'Please wait for the process to retrieve video link.',remaining_display)
		if (pDialog.iscanceled()):
			return False
		
	xbmcPlayer = xbmc.Player()
	xbmcPlayer.play(playList)
		
	if not xbmcPlayer.isPlayingVideo():
		d = xbmcgui.Dialog()
		d.ok('INVALID VIDEO PLAYLIST', 'The playlist videos are probably broken.','Check other links.')

	if xbmcPlayer.onPlayBackStopped():
		xbmcPlayer.stop()
		
	return ok
	
def addDir(name,url,mode,iconimage,numItems=1,aid='0',descr='',yr='1900',genre='',totep='0',watchep='0',epSeason=1, epNum=0, mo='01', day='01', fanart='', plycnt=0):
	# XBMC: create directory
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&aid="+str(aid)
	ok=True
	unwatchep = '0'
	airdate = str(yr)+'-'+str(mo).zfill(2)+'-'+str(day).zfill(2)
	if (len(totep)>0 and len(watchep)>0):
		unwatchep = str(int(totep)-int(watchep))
	
	if plycnt > 0:
		watched = True
	else:
		watched = False
		
	name = urllib.unquote(name)
	
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title":name, "Plot":descr, "Year":yr, "Genre":genre,"Season":epSeason,"Episode":epNum,"Aired":airdate,"PlayCount":plycnt,"Watched":watched} )
	liz.setProperty('Fanart_Image',fanart)
	liz.setProperty('TotalEpisodes',totep)
	liz.setProperty('WatchedEpisodes',watchep)
	liz.setProperty('UnWatchedEpisodes',unwatchep)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True, totalItems=numItems)
	return ok
		
def addLink(name,url,iconimage):
	# XBMC: Create playable links
	ok=True	
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	# adding context menus
	# contextMenuItems = []
	# contextMenuItems.append(('Download', 'XBMC.RunPlugin(%s?mode=13&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(name), urllib.quote_plus(url))))
	# contextMenuItems.append(('Download and Play', 'XBMC.RunPlugin(%s?mode=15&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(name), urllib.quote_plus(url))))
	# contextMenuItems.append(('Download Quietly', 'XBMC.RunPlugin(%s?mode=14&name=%s&url=%s)' % (sys.argv[0], urllib.quote_plus(name), urllib.quote_plus(url))))
	# contextMenuItems.append(('Download with jDownloader', 'XBMC.RunPlugin(plugin://plugin.program.jdownloader/?action=addlink&url=%s)' % (urllib.quote_plus(url))))
	
	# liz.addContextMenuItems(contextMenuItems, replaceItems=True)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
	return ok

def addPlaylist(name,url,mode,iconimage):
	# XBMC: create playlist link
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&aid="+str(aid)
	ok=True
	
	name = urllib.unquote(name)
	
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title":name} )
	liz.setProperty('Fanart_Image',iconimage)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	return ok
		
def f2(seq): 
	# order preserving uniqify --> http://www.peterbe.com/plog/uniqifiers-benchmark
	# checked = []
	# for e in seq:
		# if e not in checked:
			# checked.append(e)
	return utils.f2(seq)	
	 
def grabUrlSource(url):
	link = cache.cacheFunction(utils.grabUrlSource,url)
	# link = cache.cacheFunction(grabUrlSource_Src,url)
	return link
   
def grabUrlSource_Src(url):
	try:
		print base_txt + 'grabUrlSource - ' + url
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
	except urllib2.URLError, e:
		base_txt + '- got http error %d fetching %s' % (e.code, url)
		return False
		
		
def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
							
	return param	

params=get_params()
url=None
name=None
mode=None
aid=None

watchListTotal = []

# pre-cache aniDB MyWishlist
if (len(unid)>0 and len(pubpass)>0) :
	watchWishlist = cache.cacheFunction(get_aniDB_list)
	watchListTotal = f2(watchWishlist)

# pre-cache aniDB MyList
if (len(uname)>0 and len(passwd)>0) :
	watchMylistSummary = cache.cacheFunction(get_aniDB_mysummarylist)
	watchListTotal = f2(watchListTotal + watchMylistSummary)

if datetime.today().hour==3:
	
	# pre-cache all activated streaming website series lists 
	cache.cacheFunction(allAnimeList)
	
	# pre-cache all the aniDB MyWishlist and MyList series data
	dirLength = len(watchListTotal)	
	print base_txt + '# of items: ' + str(dirLength)
	pb = xbmcgui.DialogProgress()
	pb.create('Generating List', 'Total aniDB List')
	ii=0
	for aidDB, name1, ep1 in watchListTotal:
		ii+=1
		[searchText, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,'',str(aidDB))
		pb.update(int(ii/float(dirLength)*100), searchText)
	pb.close()
	
	# pre-cache cartoon list
	for url in cartoonUrls:
		for streamList in streamSiteList:
			if streamList in url:
				siteBase = 'cache7.cacheFunction(' + streamList + '.Video_List_And_Pagination, url)'
				eval(siteBase)
				
	# pre-cache most popular & most recent lists
	for url in mostUrls:
		cache7.cacheFunction(animecrazy.Video_List_And_Pagination, url)
	
	url = None
	

try:
	url=urllib.unquote_plus(params["url"])
except:
	pass
try:
	name=urllib.unquote_plus(params["name"])
except:
	pass
try:
	mode=int(params["mode"])
except:
	pass
try:
	aid=str(params["aid"])
except:
	pass

				

if mode==None:
	HOME()

elif mode==10:
	ANIME() 

elif mode==11:
	CARTOON() 

elif mode==1:
	MOST_POPULAR(url) 
		
elif mode==2:
	SEARCH(name,aid) 
		
elif mode==3:
	getEpisode_Listing_Pages(url,aid)
		
elif mode==4:
	getEpisode_PageMerged(url)

elif mode==41:
	getEpisode_Page_Fail(url)

elif mode==42:
	PLAYLIST_VIDEOLINKS(url,name)

elif mode==43:
	getEpisode_Page(url)
		
elif mode==5:
	LOAD_AND_PLAY_VIDEO(url,name)

elif mode==6:
	A_Z_LIST()

elif mode==61:
	A_Z_LIST_VIDEOS(url)
		
elif mode==7:
	TYPED_SEARCH() 

elif mode==8:
	MOST_RECENT(url)

elif mode==9:
	CARTOON_LIST()

elif mode==12:
	ANIDB_WISHLIST(url)

elif mode==121:
	ANIDB_SIMILAR(aid)

elif mode==13:
	ANIDB_MYLIST(url)
		
elif mode==14:
	ANIDB_MYLIST_WATCHING(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
