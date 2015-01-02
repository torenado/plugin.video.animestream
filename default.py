import urllib,urllib2,re,sys,httplib
import gzip, io
import xbmc,xbmcplugin,xbmcgui,xbmcaddon,urlresolver
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging
from datetime import datetime
from datetime import timedelta
try:
	import json
except ImportError:
	import simplejson as json
import sqlite3 as sqlite



base_txt = 'animestream: '
plugin_name = "animestream"
dc=xbmcaddon.Addon(id='plugin.video.animestream')
addonPath=os.getcwd()
sys.path = [dc.getAddonInfo('path') + "/lib"] + sys.path
sys.path = [dc.getAddonInfo('path') + "/lib/streamSites"] + sys.path

import utils
import anidbQuick

streamSiteList_general = ['anilinkz',
				'anime44',
				'animecrazy',
				'animeflavor',
				'animefreak',
				'animefushigi',
				'animereboot',
				'animesubbed',
				'animetip',
				'lovemyanime',
				'myanimelinks',
				'tubeplus']
streamSiteList_adult = ['hentaiseries',
				'hentaistream']
streamSiteList = streamSiteList_general + streamSiteList_adult

for module in streamSiteList:
	vars()[module]=__import__(module)

try:
	import StorageServer
except:
	import storageserverdummy as StorageServer
	
cache = StorageServer.StorageServer(plugin_name, 24) # (Your plugin name, Cache time in hours)
cache7 = StorageServer.StorageServer(plugin_name, 24*7) # (Your plugin name, Cache time in hours)
	
#animestream
# modded from --> <addon id="plugin.video.animecrazy" name="Anime Crazy" version="1.0.9" provider-name="AJ">

#SQLite querey to refresh data

#sql = 'delete from %s where data like "%mylist%";' % plugin_name
#sql = 'delete from %s where data like "%<anime-list>%";' % plugin_name
#sql = 'delete from %s where data like "%<error>%";' % plugin_name
#sql = 'delete from %s where name not like "%grab%";' % plugin_name


mozilla_user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
base_txt = 'animestream: '

plug_path = xbmc.translatePath(dc.getAddonInfo("profile")).decode("utf-8")
user_path = os.path.join(plug_path, plugin_name+'.db')
# cache_path= os.path.join(plug_path, '../script.common.plugin.cache/commoncache.db')
cache_path= os.path.join(plug_path, '../../../temp/commoncache.db')
con_us = sqlite.connect(user_path)
con_cache = sqlite.connect(cache_path)

# aniDB Login
uname = dc.getSetting('username')
passwd = dc.getSetting('pass')

# aniDB Public Wishlist
unid = dc.getSetting('uid')
pubpass = dc.getSetting('pubpass')

#aniDB Access
aniDB_access = dc.getSetting('aniDB_access')

# Cartoon List URLs
cartoonUrls = ['http://www.animeflavor.com/index.php?q=cartoons',
				'http://anilinkz.com/cartoons-list']
				
# Most Poular/Recent List URLs
mostUrls = ['http://www.animecrazy.net/most-popular/',
			'http://www.animecrazy.net/most-recent/']

THUMBNAIL_VIEW_IDS = {'skin.confluence': 515,
					  'skin.aeon.nox': 551,
					  'skin.confluence-vertical': 515,
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
	addDir('Streaming Site','',20,'')
	addDir('Search','',7,'',numItems=3)
	addDir('Settings','',16,'',numItems=3)

def ANIME():
	# XBMC: Anime screen
	print base_txt + 'Create Anime Screen'
	
	if (len(unid)>0 and len(pubpass)>0) :
		addDir('aniDB: Wishlist','',12,'')
	if (len(uname)>0 and len(passwd)>0) :
		addDir('aniDB: MyList - In Progress','',14,'')
		addDir('aniDB: MyList','',13,'')
	addDir('aniDB: Hot Anime','',15,'')
	addDir('Most Popular','',1,'')
	addDir('Most Recent','',8,'')
	# addDir('A-Z List','',6,'')
	addDir('A-Z List','',25,'')
	addDir('Search','',7,'')

def CARTOON():
	# XBMC: Cartoon screen
	print base_txt + 'Create Cartoon Screen'
	addDir('Cartoons','',9,'')
	addDir('Search','',7,'')

def STREAMING_SITE():
	# XBMC: Streaming Site screen
	print base_txt + 'Create Streaming Site Screen'
	
	searchSiteList = []
	
	
	dirLength = len(streamSiteList)	+2
	print base_txt + '# of items: ' + str(dirLength)
	pb = xbmcgui.DialogProgress()
	pb.create('Generating List', 'Streaming Site')
	
	ii=0
	for streamList in streamSiteList:
		ii += 1
		updateText = 'Streaming Site: ' + streamList
		print base_txt + str(ii) + ' of ' + str(dirLength) +' - '+ updateText
		pb.update(int(ii/float(dirLength)*100), updateText)
		siteOn = streamList + '_on'
		searchText = ''
		if (dc.getSetting(siteOn) == 'true'):
			siteBase = streamList + '.base_url_name'
			searchText = eval(siteBase)
			# mostPop2 = cache.cacheFunction(getStreamingSiteList,searchText)	
			mostPop2 = getStreamingSiteList(searchText)	
			name = searchText + ' [' + str(len(mostPop2)) + ']'
			addDir(name,searchText,21,'')
		if (pb.iscanceled()): return	
	
	ii += 1
	updateText = 'Streaming Site: ALL SITES'
	print base_txt + str(ii) + ' of ' + str(dirLength) +' - '+ updateText
	pb.update(int(ii/float(dirLength)*100), updateText)
	mostPop2 = getStreamingSiteList('')	
	name = 'ALL SITES [' + str(len(mostPop2)) + ']'
	addDir(name,'',21,'')
	if (pb.iscanceled()): return
	
	ii += 1
	updateText = 'Streaming Site: UNKNOWNS (Missing Meta)'
	print base_txt + str(ii) + ' of ' + str(dirLength) +' - '+ updateText
	pb.update(int(ii/float(dirLength)*100), updateText)
	mostPop2 = unknown_list()	
	name = 'UNKNOWNS (Missing Meta) [' + str(len(mostPop2)) + ']'
	addDir(name,'',24,'')	
	if (pb.iscanceled()): return
	pb.close()
	
	addDir('A-Z List','',25,'')
	addDir('REFRESH -- UNKNOWN Series Data','',23,'',numItems=3)
	addDir('REFRESH -- Streaming Sites Info','',22,'',numItems=3)

def ANIDB_WISHLIST(url=''):
	# MODE 12 = ANIDB_WISHLIST

	print base_txt + 'Create Wishlist Screen'
	
	watchWishlist = list_wishlist()
		
	getSeriesList(watchWishlist,url,'1')
	
	groupAid = ''
	for aid2,name,eps in watchWishlist:		
		if aid2 != '0':
			groupAid = groupAid + ' <--> ' + str(aid2)
			
	if (len(groupAid)>0):
		# addDir(name,url,mode,iconimage,aid='0') <-- overloaded variables used in special as follows
		# MAP: 
		# name = "-- REFRESH --",
		# url = searchText
		# mode = 121
		# iconimage = aid
		# aid=groupAid
		addDir('-- REFRESH (All Items) --','',122,'',aid=groupAid)	
	
def ANIDB_MYLIST(url=''):
	# MODE 13 = ANIDB_MYLIST

	print base_txt + 'Create Mylist Screen'
	
	watchMylistSummary_List = list_mylist()
	
	getSeriesList(watchMylistSummary_List,url,'1')
	
def ANIDB_MYLIST_WATCHING(url=''):
	# MODE 14 = ANIDB_MYLIST_WATCHING	

	print base_txt + 'Create In-Progress Screen'
	
	watchMylistSummary = list_mylistsummary()
	
	myList = []
	mode = 1
	dirLength = len(watchMylistSummary)	
	print base_txt + '# of items to check: ' + str(dirLength)
	
	
	pb = xbmcgui.DialogProgress()
	pb.create('Generating List', 'aniDB MyList')
	
	ii=0
	for aidDB, name, eps in watchMylistSummary:
		ii += 1
		# [searchText, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,'',str(aidDB))
		[searchText, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_detail_db('',str(aidDB))
		if int(eps[0]) > int(epwatch) :
			epwatch = eps[0]
					
		if len(searchText) > 0 and int(eptot) > int(epwatch):
			myList.append([aid,searchText,searchText.split()[0]])
			updateText = searchText
			print base_txt + str(ii) + ' of ' + str(dirLength) +' - '+ updateText
			pb.update(int(ii/float(dirLength)*100), updateText)	
		if (pb.iscanceled()): return	
	
	pb.close()
	
	myList.sort(key=lambda name: name[0], reverse=True) 
	myList.sort(key=lambda name: name[2]) 
	
	getSeriesList(myList,url,'1')
	
def ANIDB_HOTANIME(url=''):
	# MODE 13 = ANIDB_MYLIST

	print base_txt + 'Create Hot Anime Screen'
	
	mostPop = cache7.cacheFunction(get_aniDB_hotanime)
	getSeriesList(mostPop,url,'1')

def ANIDB_SIMILAR(aid_org):
	# MODE 121 = ANIDB_SIMILAR

	print base_txt + 'Create Similar Title(s) Screen'
	
	# [searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_all_data(aid=aid_org)
	# [searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache.cacheFunction(get_all_data,'',aid_org)
	# [searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,'',aid_org)
	[searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_detail_db('',aid_org)
	
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
	
	if url == '' or url == None:
		url = 'http://www.animecrazy.net/most-popular/'
	mostPop = cache7.cacheFunction(animecrazy.Video_List_And_Pagination, url)
	
	returnMode = 1
	getSeriesList(mostPop,url,returnMode)

def CARTOON_LIST(url=''):
	# Hardcoded to use animeflavor.com
	# MODE 9 = CARTOON_LIST
	
	mostPop = []
	
	if url == '' or url == None:
		for url in cartoonUrls:
			for streamList in streamSiteList:
				if streamList in url:
					siteBase = 'cache7.cacheFunction(' + streamList + '.Video_List_And_Pagination, url)'
					mostPop = mostPop + eval(siteBase)
			
	# mostPop = animeflavor.Video_List_And_Pagination(url)
	# mostPop = cache.cacheFunction(animeflavor.Video_List_And_Pagination, url)	
	
	
	# name = ''
	# nameTest = ''
	# mostPop2 = []
	# for iconimage, name, urls in mostPop:
		# if name.startswith('The '):
			# name = name[4:] + ', The'
		# mostPop2.append([str(iconimage), name, urls])
	
	# mostPop2.sort(key=lambda name: name[1])
	# returnMode = 1
	
	name = ''
	nameTest = ''
	mostPop2 = []
	for iconimage, name, urls in mostPop:
		if name.startswith('The '):
			name = name[4:] + ', The'
		mostPop2.append([urls, name])
	
	mostPop2.sort(key=lambda name: name[1])
	
	mostPop2 = combinedSearchCollect(mostPop2)
	returnMode = 3
	getSeriesList(mostPop2,'',returnMode)
	
def STREAMING_SITE_LIST(searchText,url=''):
	# MODE 21 = STREAMING_SITE_LIST
	
	mostPop = []	
	# mostPop2 = getStreamingSiteList(searchText)	
	# returnMode = 1
	# print len(mostPop2)
	mostPop2 = getStreamingSiteList2(searchText)	
	mostPop2 = combinedSearchCollect(mostPop2)
	returnMode = 3
	getSeriesList(mostPop2,'',returnMode)
	
	if not searchText==None:
		if len(searchText)>0:
			addDir('REFRESH -- This Site\'s Info',searchText,211,'')
	
def UNKNOWN_LIST():
	# MODE 24 = UNKNOWN_LIST
	
	mostPop = []	
	# mostPop2 = unknown_list()	
	# returnMode = 1
	# print len(mostPop2)
	mostPop2 = unknown_list3()
	mostPop2 = combinedSearchCollect(mostPop2)
	returnMode = 3
	getSeriesList(mostPop2,'',returnMode)	
	
def STREAMING_SITE_A_Z_LIST():
	# MODE 25 = STREAMING_SITE_A_Z_LIST
	
	abc = [chr(i) for i in xrange(ord('A'), ord('Z')+1)]
	
	dirLength = len(abc)
	print base_txt + '# of items: ' + str(dirLength)
	for alphaB in abc:
		addDir(alphaB,alphaB.lower(),251,'',numItems=dirLength)
	
def STREAMING_SITE_A_Z_LIST_SERIES(alpha='a'):
	# MODE 251 = STREAMING_SITE_A_Z_LIST_SERIES
	
	mostPop = []	
	# mostPop2 = alpha_list(alpha)	
	# returnMode = 1
	# print len(mostPop2)
	mostPop2 = alpha_list2(alpha)
	mostPop2 = combinedSearchCollect(mostPop2)
	returnMode = 3
	getSeriesList(mostPop2,'',returnMode)

def MOST_RECENT(url=''):
	# Hardcoded to use animecrazy.net
	# MODE 8 = MOST_RECENT
	
	print base_txt + 'Create Most Recent Screen'
	
	if url == '' or url == None:
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
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

	url = ''
	mode = 3
		
	# print searchRes
	print searchText + ' [' + str(aid) + ']'
	if aid==None:
		aid = '0'
		
	if ' <--> ' in searchText:
		searchRes = []
		try:
			name_mult = searchText.split(' <--> ')
		except:
			name_mult = searchText
			
		for nameSearch in name_mult:
			if nameSearch != '':
				searchRes = searchRes + searchCollection(nameSearch,aid)
		
	else:
		searchRes = searchCollection(searchText,aid)
	
	
	if len(searchRes)>0:
		getSeriesList(searchRes,'',mode=mode)
		searchText = auto_text_search(searchText)
	else:
		addDir('-- REFRESH (Re-Search w/ Name) --',searchText,212,'',aid=aid)	
		while ' ' in searchText:
			searchText = auto_text_search(searchText)
	
		
	if (len(uname)>0 and len(passwd)>0) :
		if not aid.isdigit():
			aid = '0'
		if (int(aid)>0):
			addDir('-- SIMILAR TITLES --','',121,'',aid=aid)
	
	# groupAid = ''
	# for aid2, name2, url2 in searchRes:		
		# if aid2 != '0':
			# groupAid = groupAid + ' <--> ' + aid2
			
	# if (len(groupAid)>0):
		# addDir(name,url,mode,iconimage,aid='0') <-- overloaded variables used in special as follows
		# MAP: 
		# name = "-- REFRESH --",
		# url = searchText_org
		# mode = 121
		# iconimage = aid
		# aid=groupAid
		# addDir('-- REFRESH (All Items) --',searchText_org,211,aid,aid=groupAid)	
		# addDir('-- REFRESH (Re-Search w/ Name) --',searchText_org,211,'0',aid=groupAid)	
	
	skin = xbmc.getSkinDir()
	thumbnail_view = THUMBNAIL_VIEW_IDS.get(skin)
	if thumbnail_view:
		cmd = 'Container.SetViewMode(%s)' % thumbnail_view
		xbmc.executebuiltin(cmd)
	
def SETTINGS():
	# Force update certain actions
	# MODE 6 = SETTINGS
	
	print base_txt + 'Create Settings Screen'
	addDir('REFRESH -- UNKNOWN Series Data','',163,'',numItems=3)
	addDir('REFRESH -- Streaming Sites Info','',161,'',numItems=3)
	addDir('REFRESH -- Print Unknown List to Command Line','',164,'',numItems=3)
	addDir('REFRESH -- aniDB Wishlist','',165,'',numItems=3)
		
def TOGGEL_CONTENT_VISIBILITY(content_type='general'):
	# toggle the content visibility
	
	if dc.getSetting(content_type + '_show') == 'true':
		dc.setSetting(content_type + '_show','false')
		xbmc.executebuiltin('XBMC.Notification(Content Visibility,Hide '+ content_type.title() +' Content,5000)')
		print base_txt + content_type.title() + ' Content is Hidden'
	else:
		dc.setSetting(content_type + '_show','true')
		xbmc.executebuiltin('XBMC.Notification(Content Visibility,Show '+ content_type.title() +' Content,5000)')
		print base_txt + content_type.title() + ' Content is Visible'
	
def cleanSearchText(searchText,skipEnc=False):
	# cleans up the text for easier searching
	# print base_txt + 'Clean up the search term: ' +searchText
	searchText = utils.unescape(searchText)
	searchText = utils.U2A(searchText)
	if not skipEnc:
		subLoc = searchText.find('[')		
		searchText_year = searchText[subLoc+1:subLoc+5]
		if searchText_year.isdigit():
			searchText_year = int(searchText_year)
		else:
			searchText_year = 0
			
		if subLoc > 0 and searchText_year>1900:
			searchText = searchText.replace('[',' ').replace(']',' ').replace('  ',' ').replace('  ',' ')
		elif subLoc > 0:
			searchText = searchText[:subLoc]
			
		subLoc = searchText.find('(')		
		searchText_year = searchText[subLoc+1:subLoc+5]
		if searchText_year.isdigit():
			searchText_year = int(searchText_year)
		else:
			searchText_year = 0
		if subLoc > 0 and searchText_year>1900:
			searchText = searchText.replace('(',' ').replace(')',' ').replace('  ',' ').replace('  ',' ')
		elif subLoc > 0:
			searchText = searchText[:subLoc]
		
	searchText = searchText.replace('-- REFRESH -- ','')
	searchText = searchText.replace('[I]','').replace('[/I]','')
	searchText = searchText.replace('(Movie/OVA)','').strip()
	searchText = searchText.replace('(TV)','').replace('(OVA)','').replace('(Movie)','').replace('(Movie/OVA)','').strip()
	searchText = searchText.replace('(Tv)','').strip()
	searchText = searchText.replace('(Dubbed)','').strip()
	searchText = searchText.replace('Dubbed','').strip()
	searchText = searchText.replace('(Raw)','').strip()
	searchText = searchText.replace('(Uncensored)','').strip()
	searchText = searchText.replace(' &Amp; ',' and ').strip()
	searchText = searchText.replace(' English Sub',' ').strip()
	searchText = searchText.replace('((','(').replace('))',')')
	searchText = searchText.replace('()','')
	searchText = searchText.replace(':',' ').replace(' - ',' ').replace('_',' ').replace(' & ',' and ').strip()
	searchText = searchText.replace('~',' ').replace('?',' ').replace('!',' ').replace('.',' ').replace('  ',' ').replace('  ',' ').strip()
	searchText = searchText.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').title().strip()
	
	return searchText

def list_wishlist():
	watchWishlist = []
	if (len(unid)>0 and len(pubpass)>0) :
		watchWishlist = cache.cacheFunction(get_aniDB_list)
	
	return watchWishlist
		
def list_mylist():
	watchMylistSummary_List =[]
	if (len(unid)>0 and len(pubpass)>0) :
		watchMylistSummary_List = cache.cacheFunction(get_aniDB_mysummarylist)
	
	return watchMylistSummary_List
		
def list_mylistsummary():
	watchMylistSummary = []

	if (len(uname)>0 and len(passwd)>0) :
		watchMylistSummary = cache.cacheFunction(get_aniDB_mysummarylist_OLD)
	
	return watchMylistSummary
		
def list_watchlisttotal():	
	watchListTotal = []
	watchListTotal = f2(list_wishlist())

	if (len(uname)>0 and len(passwd)>0) :
		watchMylistSummary = cache.cacheFunction(get_aniDB_mysummarylist_OLD)
		watchListTotal = watchListTotal + watchMylistSummary
		watchListTotal.sort(key=lambda name: name[2][1], reverse=True) 
		watchListTotal = f2(watchListTotal)
	
	return watchListTotal
	
def get_ani_detail(aid):
	
	time_now = datetime.now().isoformat(' ')
	time_then = dc.getSetting('aniDB_access')
	linkAID = ' '
	if time_now > time_then:
		if not aid.isdigit():
			aid = '0'
		if int(aid)>0 :
			time.sleep(2.5)
			urlPg = 'http://api.anidb.net:9001/httpapi?request=anime&client=xbmcscrap&clientver=1&protover=1&aid=%(aid)s' % {"aid": aid}
			linkAID = grabUrlSource(urlPg)
			
		if '<error>Banned</error>' in linkAID:
			aniDB_access_time = datetime.now() + timedelta(0,0,0,0,61) # access to aniDB API should be available again in 60 min
			dc.setSetting('aniDB_access',aniDB_access_time.isoformat(' '))
			xbmc.executebuiltin('XBMC.Notification(aniDB API Access,Banned for 60 minutes,5000)')
			print base_txt + 'access to aniDB API should be available again at ' + aniDB_access_time.isoformat(' ')
			return False
		
	return linkAID
		
def get_tvdb_detail(tvdbid):
	linkAID = ' '
	if int(tvdbid)>0 :
		time.sleep(2.5)
		urlPg = 'http://www.thetvdb.com/api/1D62F2F90030C444/series/%(tvdbid)s/all/en.xml' % {"tvdbid": tvdbid}
		linkAID = grabUrlSource(urlPg)
	
	return linkAID
	
def get_ani_aid(searchText):
	
	aid = '0'
	if not searchText=='':
		searchText_org = searchText
		con = sqlite.connect(user_path)
		with con:
			cur = con.cursor()
			con.text_factory = str
			searchAlts = []
			
			searchAlts.append(searchText)
			
			subLoc = searchText.find('(')
			if subLoc > 0:
				searchText = searchText[:subLoc]
			searchText = urllib.unquote(searchText).title()
			searchAlts.append(searchText)
			searchAlts.append(searchText)
				
			searchAlts = searchAlts + altName(searchText,' ')
			
			searchAlts = searchAlts + altName(searchText,']')
			searchAlts = searchAlts + altName(searchText,'[')
			searchAlts = searchAlts + altName(altName(searchText,'['),']')
			
			searchAlts = searchAlts + altName(searchText,')')
			searchAlts = searchAlts + altName(searchText,'(')
			searchAlts = searchAlts + altName(altName(searchText,'('),')')
			
			searchAlts = searchAlts + altName(searchText,':')
			searchAlts = searchAlts + altName(searchText,'!')
			ssearchAlts = searchAlts + altName(altName(searchText,':'),'!')
			
			searchAlts = searchAlts + altName(searchText,';')
			searchAlts = searchAlts + altName(searchText,'\'')
			searchAlts = searchAlts + altName(searchText,'`')
			searchAlts = searchAlts + altName(searchText,'?')
			searchAlts = searchAlts + altName(searchText,'-')
			searchAlts = searchAlts + altName(searchText,'~')
			searchAlts = searchAlts + altName(searchText,'.')
			searchAlts = searchAlts + altName(searchText,',')
			searchAlts = searchAlts + altName(searchText,'/')
			searchAlts = searchAlts + altName(searchText,'\\')
			
			if searchText.startswith('The'):
				searchAlts.append(searchText.replace('The ',''))
			
			searchAlts = searchAlts + altName(searchAlts,' ')
				
			searchAlts = searchAlts + utils.U2A_List_over(searchAlts) 
			searchAlts = f2(searchAlts) 
			searchAlts.sort(key=lambda name: name[0]) 
			print base_txt + 'Searching ' + str(len(searchAlts)) + ' alternate names + variations of:' + searchText_org	
			for nameSearch in searchAlts:			
				cur.execute('SELECT aid FROM SeriesNameAID WHERE name="%s"' % nameSearch)   
				rows = cur.fetchall()
				print rows
				if len(rows)>0:
					return str(rows[0][0])
	return aid	
	
def get_ani_searchText(aid):

	groupUrl = []
	groupUrl.append('https://sites.google.com/site/anidblist/anime-list.xml?attredirects=0')
	groupUrl.append('https://raw.github.com/torenado/plugin.video.animestream/master/anime-list_modded.xml')
	
	linkAID = ''
	for url in groupUrl:
		linkAID = linkAID + str(grabUrlSource(url))
	
	searchText = []
	
	# aidList = get_ani_aid_list(linkAID)
	aidList = cache.cacheFunction(get_ani_aid_list,linkAID)

	print base_txt + 'Searching anime-list for aid: ' + str(aid)
	
	for aidFound, name, tvdbid, season in  aidList:
		if aidFound == aid:
			searchText.append(name)
			
	return searchText
	
def search_aid_tvid(searchText, aidGet=False, tvdbGet=True):
	
	searchText = cleanSearchText(searchText)
	
	tvdbid = '0'
	aid = '0' 
	
	tvdb_detail_search=[]
	if tvdbGet:	
		time.sleep(2.5)		
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
		
		# anidb_detail_search = anidbQuick.AID_Search(linkAID)
		anidb_detail_search = cache.cacheFunction(anidbQuick.AID_Search,linkAID)
			
		for name, aidFound in anidb_detail_search:
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

def auto_text_search(searchText):
	# auto generate text searches from input
	searchText = cleanSearchText(searchText)
	searchText_org = cleanSearchText(searchText)
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
		
	return searchText
	
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
	for pg in xrange(0,30):
		time.sleep(2.5)
		urlPg = url + '&page=' + str(pg)
		print base_txt + urlPg
		linkPg = grabUrlSource(urlPg)
		if 'No results.' in linkPg:
			print base_txt + 'No more pages to parse'
			break
		else:
			multiPg.append(linkPg)
		
		link = ''.join(multiPg)
		
	# print link	
	watchWishlist = anidbQuick.Wishlist(link)	
	watchWishlist.sort(key=lambda name: name[0], reverse=True) 
	watchWishlist.sort(key=lambda name: name[1]) 
	
	return watchWishlist

def refresh_get_aniDB_list(url=''):	
	# remove entries related to a anidb Wishlist
	
	xbmc.executebuiltin('XBMC.Notification(Removing Info!,aniDB Wishlist,5000)')
	
	if url == '':
		url = 'http://anidb.net/perl-bin/animedb.pl?show=mywishlist&uid=%(un)s&pass=%(pass)s' % {"un": unid, "pass": pubpass}
	
	con = sqlite.connect(cache_path)
	with con:
		cur = con.cursor()
		
		for pg in xrange(0,30):
			urlPg = url + '&page=' + str(pg)
			print base_txt + urlPg
			cacheRemove = 'cache' + utils.commonCacheKey(grabUrlSource,urlPg)		
			sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
			print base_txt + sql
			cur.execute(sql)
			cacheRemove = 'cache' + utils.commonCacheKey(utils.grabUrlSource,urlPg)		
			sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
			print base_txt + sql
			cur.execute(sql)
			
	get_aniDB_list()
	
def get_aniDB_mysummarylist(url=''):		
	
	xbmc.executebuiltin('XBMC.Notification(Retrieving Info!,aniDB MyList,5000)')
	
	if url == '':
		url = 'http://anidb.net/perl-bin/animedb.pl?show=mylist&uid=%(un)s&pass=%(pass)s' % {"un": unid, "pass": pubpass}
	
	multiPg = []	
	for pg in xrange(0,30):
		time.sleep(3)
		urlPg = url + '&page=' + str(pg)
		# print base_txt + urlPg
		linkPg = grabUrlSource(urlPg)
		if 'No results.' in linkPg:
			print base_txt + 'No more pages to parse'
			break
		else:
			multiPg.append(linkPg)
		
		link = ''.join(multiPg)
		
	watchMylistSummary = anidbQuick.MyListSummary(link)	
	watchMylistSummary.sort(key=lambda name: name[0], reverse=True) 
	watchMylistSummary.sort(key=lambda name: name[1]) 
	
	return watchMylistSummary
	
def get_aniDB_hotanime(url=''):		
	
	xbmc.executebuiltin('XBMC.Notification(Retrieving Info!,aniDB Hot Anime,5000)')
	
	if url == '':
		url = 'http://api.anidb.net:9001/httpapi?request=main&client=xbmcscrap&clientver=1&protover=1'
	
	link = grabUrlSource(url)
		
	watchHotAnimeSummary = anidbQuick.HotAnimeSummary(link)	
	# watchHotAnimeSummary.sort(key=lambda name: name[0], reverse=True) 
	# watchHotAnimeSummary.sort(key=lambda name: name[1]) 
	
	return watchHotAnimeSummary
	
def get_aniDB_mysummarylist_OLD(url=''):	
	
	xbmc.executebuiltin('XBMC.Notification(Retrieving Info!,aniDB MyList,5000)')
	
	if url == '':
		url = 'http://api.anidb.net:9001/httpapi?client=xbmcscrap&clientver=1&protover=1&request=mylistsummary&user=%(un)s&pass=%(pass)s' % {"un": uname, "pass": passwd}
		link = grabUrlSource(url)
		
	if '<error>Banned</error>' in link:
		url = 'http://anidb.net/perl-bin/animedb.pl?show=mylist&uid=%(un)s&pass=%(pass)s' % {"un": unid, "pass": pubpass}
		link = grabUrlSource(url)
		watchMylistSummary = anidbQuick.MyListSummary(link)	
	else:
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
	epList = ['0','','','','1','','']
	simAniList = []
	adult = 'No'
	synAniList = []
	eptot = '00'
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
		if not get_tvdb_id(aid)[1] == '':
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
		if not get_tvdb_id(aid)[1] == '':
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
	
	watchListTotal = list_watchlisttotal()
	if (int(aidDB)>0 and len(uname)>0 and len(passwd)>0) :
		for aidWish, nameWish, epsWish in watchListTotal:
			if int(aidDB) == int(aidWish):
				epwatch = str(epsWish[0])
				break
				
		linkAID = get_ani_detail(aidDB)
		# linkAID = cache.cacheFunction(get_ani_detail,aidDB)
		
		if linkAID != False:
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
		searchText = utils.U2A(searchText1)
	
	allData = [searchText, aid, tvdbSer, description, fanart, iconimage, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount]
	
	return allData

def refresh_un_detail_db():
	# remove entries related to aid from the animestream DB	

	con = sqlite.connect(user_path)
	with con:
		cur = con.cursor()
		print base_txt + 'REMOVING un* data'
		
		sql = 'DELETE FROM Series WHERE aid LIKE "un%"'
		print base_txt + sql
		cur.execute(sql)
		
		sql = 'DELETE FROM SimilarSeries WHERE aid LIKE "un%"'
		print base_txt + sql
		cur.execute(sql)
		
		sql = 'DELETE FROM SynonymSeries WHERE aid LIKE "un%"'
		print base_txt + sql
		cur.execute(sql)
		
		sql = 'DELETE FROM EpisodeList WHERE aid LIKE "un%"'
		print base_txt + sql
		cur.execute(sql)
		
		sql = 'DELETE FROM SeriesNameAID WHERE aid LIKE "un%"'
		print base_txt + sql
		cur.execute(sql)	
		
	con = sqlite.connect(cache_path)
	with con:
		cur = con.cursor()
		for streamList in streamSiteList:
			siteOn = streamList + '_on'
			searchText = ''
			if (dc.getSetting(siteOn) == 'true'):
				siteBase = streamList + '.base_url_name'
				searchText = eval(siteBase)
				cacheRemove = 'cache' + utils.commonCacheKey(getStreamingSiteList,searchText)		
				sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
				print base_txt + sql
				cur.execute(sql)
				
		cacheRemove = 'cache' + utils.commonCacheKey(allAnimeList)		
		sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
		print base_txt + sql
		cur.execute(sql)
				
		cacheRemove = 'cache' + utils.commonCacheKey(name2aid)		
		sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
		print base_txt + sql
		cur.execute(sql)
		
def get_detail_db(searchText='',aid='0',tvdbSer='0'):
	
	if searchText.endswith(', The'):
		searchText = 'The ' + searchText.replace(', The','')
	searchText = cleanSearchText(searchText)
	
	con = sqlite.connect(user_path)
	con.row_factory = sqlite.Row
	cur = con.cursor()
	
	
	if aid == '0':	
		try:  
			print base_txt + 'No aid provided. Searching anime-list for ... ' + searchText
			aid = get_ani_aid(searchText)
			if aid == '0':
				searchText1 = searchText.replace('\'','')
				searchText1 = cleanSearchText(searchText1)
				print base_txt + 'NOT FOUND IN anime-list - Searching DB for ... ' + searchText1
				# sql = 'SELECT aid FROM Series WHERE searchText="%s"' % searchText1
				sql = 'SELECT aid FROM SeriesNameAID WHERE name="%s"' % searchText1
				cur.execute(sql)
				rows = cur.fetchall() 
				if len(rows)==0: 
					print base_txt + 'NOT FOUND IN DB - Searching aniDB and theTVDB for ... ' + searchText
					(aidDB , tvdbSer) = search_aid_tvid(searchText,True,True)
					if int(aidDB)!=0:
						aid = aidDB
					elif aidDB == '0' and int(tvdbSer)!=0 :
						aid ='t' + str(tvdbSer)
				else:
					aid = rows[0]['aid']
		except sqlite.Error, e:
			print base_txt + 'animestream DB path - ' + user_path
			[searchText, aid, tvdbSer, description, fanart, iconimage, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = set_detail_db(searchText,aid,tvdbSer)
			utils.U2A(searchText)
	if aid == '0' and int(tvdbSer)!=0 :
		aid ='t' + str(tvdbSer)
	
	# print aid
	# print aidDB
	# print tvdbSer
	
	try:  
		cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="Series";')   
		rows = cur.fetchall()   
		if len(rows)==0: 
			set_detail_db(searchText,aid,tvdbSer)
	except sqlite.Error, e:
		print base_txt + 'animestream DB path - ' + user_path
		set_detail_db(searchText,aid,tvdbSer)
	
	if aid != '0':
		with con:			
			con.text_factory = str
			sql = 'SELECT * FROM Series WHERE aid="%s"' % aid
			cur.execute(sql)
			rows = cur.fetchall()
			
			if len(rows)>0:
				epList = []
				simAniList = []
				synAniList = []
				row = rows[0]
				fanart = row['fanart']
				tvdbSer = row['tvdbSer']
				description = row['description']
				genre =row['genre']
				epwatch = row['epwatch']
				iconimage = row['iconimage']
				adult = row['adult']
				eptot = row['eptot']
				season = str(row['season'])
				searchText = row['searchText']
				playcount = row['playcount']
				year = row['year']
					
				con.row_factory = None
				cur = con.cursor()
				
				sql = 'SELECT simAid, name FROM SimilarSeries WHERE aid="%s"' % aid
				cur.execute(sql)
				simAniList = cur.fetchall()
				sql = 'SELECT simAid, name FROM SynonymSeries WHERE aid="%s"' % aid
				cur.execute(sql)
				synAniList = cur.fetchall()
				# print synAniList
				
				sql = 'SELECT epNumAb, epName, epIconimage, description, seasonNum, epAirdate_year, epAirdate_month, epAirdate_day, epNum FROM EpisodeList WHERE aid="%s"' % aid
				cur.execute(sql)
				rows = cur.fetchall()
				for epNumAb, epName, epIconimage, epDescription, seasonNum, epAirdate_year, epAirdate_month, epAirdate_day, epNum in rows:
					epAirdate = [1850,1,1]
					epAirdate[0] = epAirdate_year 
					epAirdate[1] = epAirdate_month
					epAirdate[2] = epAirdate_day
					epDescription = html_special(epDescription)
					epName = html_special(epName)
					epList.append([epNumAb,epName,epIconimage,epDescription,seasonNum,epAirdate,epNum])
			else:
				print base_txt + 'NOT FOUND IN DB - Attempting to place into DB ... aid = ' + aid
				[searchText, aid, tvdbSer, description, fanart, iconimage, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = set_detail_db(searchText,aid,tvdbSer)
	else:
		print base_txt + 'NOT FOUND IN DB - Attempting to place into DB ... searchText = ' + searchText
		[searchText, aid, tvdbSer, description, fanart, iconimage, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = set_detail_db(searchText,aid,tvdbSer)
	
	
	description = html_special(description)
	searchText = html_special(searchText)
	allData = [searchText, aid, tvdbSer, description, fanart, iconimage, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount]
	# print allData
	
	return allData

def set_detail_db(searchText='',aid='0',tvdbSer='0'):

	con = sqlite.connect(user_path)
	with con:
		cur = con.cursor()
		sql = 'CREATE TABLE IF NOT EXISTS Series(aid TEXT PRIMARY KEY, tvdbSer TEXT, searchText TEXT, description TEXT, fanart TEXT, iconimage TEXT, genre TEXT, year INT, season INT, adult TEXT, epwatch INT, eptot INT, playcount INT)'
		cur.execute(sql)
		sql = 'CREATE TABLE IF NOT EXISTS SimilarSeries(id INTEGER PRIMARY KEY, aid TEXT, simAid INT, name TEXT)'
		cur.execute(sql)
		sql = 'CREATE TABLE IF NOT EXISTS SynonymSeries(id INTEGER PRIMARY KEY, aid TEXT, simAid INT, name TEXT)'
		cur.execute(sql)
		sql = 'CREATE TABLE IF NOT EXISTS EpisodeList(id INTEGER PRIMARY KEY, aid TEXT, epNumAb INT, epName TEXT, epIconimage TEXT, description TEXT, seasonNum INT, epAirdate_year INT, epAirdate_month INT, epAirdate_day INT, epNum INT)'
		cur.execute(sql)		
		sql = 'CREATE TABLE IF NOT EXISTS ProfileWatch(aid TEXT PRIMARY KEY, epwatch INT, playcount INT)'
		cur.execute(sql)	
		sql = 'CREATE TABLE IF NOT EXISTS StreamMeadiaLink(url TEXT PRIMARY KEY,streamSource TEXT,aid TEXT,seasonNum INT, epNum INT)'
		cur.execute(sql)
		
		[searchText, aid, tvdbSer, description, fanart, iconimage, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_all_data(searchText,aid,tvdbSer)
	
		if int(tvdbSer)!=0 and aid == '0':
			print base_txt + 'aid NOT found...using tvdbID'
			aid ='t' + str(tvdbSer)
		
		if(aid==0 or aid =='0'):	
			print base_txt + 'aid NOT found...making one up'
			
			sql = 'SELECT aid FROM Series WHERE aid LIKE "un%" ORDER BY aid DESC'
			print base_txt + sql
			cur.execute(sql)
			rows = cur.fetchall() 
			if len(rows)==0:
				aid = 'un%07d' % (1,)
			else:
				# print str(rows[0][0]).split('un')
				last_un = str(rows[0][0]).split('un')[1]
				aid = 'un%07d' % (int(last_un)+1,)
				
		# print aid
		# print tvdbSer
		
		if aid != '0':
			description = description.replace('\'','&lsquo;')
			# sql = 'INSERT INTO Series VALUES("%s", "%s", "%s", \'%s\', "%s", "%s", "%s", %s, %s, "%s", %s, %s, %s)' % (aid, tvdbSer, searchText, description, fanart, iconimage, genre, year, season, adult, epwatch, eptot, playcount)
			sql = 'INSERT INTO Series VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)' 
			sql_para = (aid, tvdbSer, searchText, description, fanart, iconimage, genre, year, season, adult, epwatch, eptot, playcount)
			# print base_txt + sql
			con.text_factory = str
			
			cur.execute('SELECT * FROM Series WHERE aid="%s"' % aid)   
			rows = cur.fetchall()   
			if len(rows)==0: 
				cur.execute(sql,sql_para)
			else:
				print base_txt + 'RECORD ALREADY EXISTS - INSERT INTO Series ... searchText = ' + searchText
			# try:
				# sql = 'INSERT INTO Series VALUES("%s", "%s", "%s", \'%s\', "%s", "%s", "%s", %s, %s, "%s", %s, %s, %s)' % (aid, tvdbSer, searchText, description, fanart, iconimage, genre, year, season, adult, epwatch, eptot, playcount)
				# print base_txt + sql
				# cur.execute(sql)
			# except:
				# print base_txt + '**DB FAILED - INSERT INTO Series ... ' + searchText
				# pass
			
			for simAid,name in simAniList:
				try:
					name = name.replace('"',' ').replace('  ',' ').replace('  ',' ')
					sql = 'INSERT INTO SimilarSeries VALUES(%s, "%s", %s, "%s")' % (str(aid)+str(simAid),aid, simAid, name)
					print base_txt + sql
					cur.execute(sql)
				except:
					print base_txt + '**DB FAILED - INSERT INTO SimilarSeries ... ' + searchText
					pass
			
			for simAid,name in synAniList:
				try:
					name = name.replace('"',' ').replace('  ',' ').replace('  ',' ')
					sql = 'INSERT INTO SynonymSeries (aid, simAid, name) VALUES("%s", %s, "%s")' % (aid, simAid, name)
					cur.execute(sql)
				except:
					print base_txt + '**DB FAILED - INSERT INTO SynonymSeries ... ' + searchText
					pass
			
			# print epList
			if epList != ['0','','','','1','','']:
				for epNumAb,epName,epIconimage,description,seasonNum,epAirdate,epNum in epList:
					epAirdate_year = epAirdate[0]
					epAirdate_month = epAirdate[1]
					epAirdate_day = epAirdate[2]
					if epAirdate_year == '':
						epAirdate_year = 1905
					if epAirdate_month == '':
						epAirdate_month = 1
					if epAirdate_day == '':
						epAirdate_day = 1
					description = description.replace('\'','&lsquo;')
					epName = epName.replace('\'','&lsquo;')
					
					run_sql = True
					if isinstance(epNumAb, str) and run_sql:
						run_sql = False
						if epNumAb.isdigit():
							run_sql = True
							
					if isinstance(epNum, str) and run_sql:
						run_sql = False
						if epNum.isdigit():
							run_sql = True
						
					sql = 'INSERT INTO EpisodeList (aid, epNumAb, epName, epIconimage, description, seasonNum, epAirdate_year, epAirdate_month, epAirdate_day, epNum) VALUES("%s", %s, \'%s\', "%s", \'%s\', %s, %s, %s, %s, %s)' % (aid, epNumAb, epName, epIconimage, description, seasonNum, epAirdate_year, epAirdate_month, epAirdate_day, epNum)
					
					if run_sql:
						# print base_txt + sql
						cur.execute(sql)
				
	allData = [searchText, aid, tvdbSer, description, fanart, iconimage, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount]
	return allData
	
def refresh_detail_db(groupAid,clearCache=True):
	# remove entries related to aid from the animestream DB	

	try:
		aid_mult = groupAid.split(' <--> ')
	except:
		aid_mult = groupAid
		
	
	con = sqlite.connect(cache_path)
	with con:
		cur = con.cursor()
		print base_txt + 'REMOVING anime-list from cache'
		
		sql = 'DELETE FROM '+plugin_name+' WHERE data LIKE "%<anime-list%"'
		print base_txt + sql
		cur.execute(sql)
	
	dirLength = len(aid_mult)
	print base_txt + '# of items: ' + str(dirLength)
	ii=0	
	for aid in aid_mult:
		if aid != '' and aid != '0':
			con = sqlite.connect(user_path)
			with con:
				ii += 1
				cur = con.cursor()
				print base_txt + 'REMOVING Data item '+str(ii)+' of '+str(dirLength)+' - aid = ' + str(aid)
				
				sql = 'DELETE FROM Series WHERE aid="'+ str(aid) +'"'
				print base_txt + sql
				cur.execute(sql)
				
				sql = 'DELETE FROM SimilarSeries WHERE aid="'+ str(aid) +'"'
				print base_txt + sql
				cur.execute(sql)
				
				sql = 'DELETE FROM SynonymSeries WHERE aid="'+ str(aid) +'"'
				print base_txt + sql
				cur.execute(sql)
				
				sql = 'DELETE FROM EpisodeList WHERE aid="'+ str(aid) +'"'
				print base_txt + sql
				cur.execute(sql)
				
				sql = 'DELETE FROM SeriesNameAID WHERE aid="'+ str(aid) +'"'
				print base_txt + sql
				cur.execute(sql)	
			
			if clearCache:
				con = sqlite.connect(cache_path)
				with con:
					cur = con.cursor()
					
					cacheRemove = 'cache' + utils.commonCacheKey(get_detail_db,'',aid)
					sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
					print base_txt + sql
					cur.execute(sql)
					
					cacheRemove = 'cache7' + utils.commonCacheKey(get_detail_db,'',aid)
					sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
					print base_txt + sql
					cur.execute(sql)
				
					cacheRemove = 'cache' + utils.commonCacheKey(name2aid)		
					sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
					print base_txt + sql
					cur.execute(sql)
	
def getSeriesList(mostPop,url='',returnMode='1',mode=2):
	
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	
	show_general = dc.getSetting('general_show')
	show_adult = dc.getSetting('adult_show')
	print base_txt + 'Show General Content: ' + show_general
	print base_txt + 'Show Adult Content: ' + show_adult
	
	
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
	print base_txt + str(url)
	print base_txt + '# of items: ' + str(dirLength)
	
	pb = xbmcgui.DialogProgress()
	pb.create('Generating Series List', 'Series')
	
	ii=0	
	
	name = ''
	url = ''
	iconimage = ''
	for iconimage, name, url in mostPop2:
		ii += 1
		searchText = cleanSearchText(name,True)
		mpaa = ''
		aidDB = '0'
		if iconimage.isdigit():
			aidDB = iconimage
			
		# print base_txt + iconimage + '[' + aidDB +'] '+ searchText
		if int(aidDB)>0:
			# sql = select * from animestream where name like"%get_detail_db%"
			# [searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_all_data('',aidDB)
			# [searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache.cacheFunction(get_all_data,'',aidDB)
			# [searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,'',aidDB)
			# [searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_detail_db('',aidDB)
			[searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_detail_db,'',aidDB)
			if name=='' or name.isspace():
				name = searchText2
				searchText = searchText2
		else:
			# [searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_all_data(searchText)
			# [searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache.cacheFunction(get_all_data,searchText)
			# [searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,searchText)
			# [searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_detail_db(searchText)
			[searchText2, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_detail_db,searchText)
		
		show = False
		if show_general=='true' and show_adult=='true':
			show = True
		elif show_general=='true' and show_adult=='false' and not adult == 'Yes':
			show = True
		elif show_general=='false' and show_adult=='true' and adult == 'Yes':
			show = True
		
		if show:
			updateText = 'Series: ' + searchText
			print base_txt + str(ii) + ' of ' + str(dirLength) +' - '+ updateText
			pb.update(int(ii/float(dirLength)*100), updateText)
			
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
			
			watchListTotal = list_watchlisttotal()
			if (int(aidDB)>0 and len(uname)>0 and len(passwd)>0) :
				for aidWish, nameWish, epsWish in watchListTotal:
					if int(aidDB) == int(aidWish):
						epwatch = str(epsWish[0])
						break
			
			# searchText = html_special(searchText)
			print base_txt + str(searchText) + ' [' + str(epwatch) + ' of ' + str(eptot) + '] (aid=' + str(aid) + ', tvdbid='+ str(tvdbSer) +')'
			if int(epwatch)>0:
				# print base_txt + str(searchText) + ' [' + str(epwatch) + ' of ' + str(eptot) + '] (aid=' + str(aid) + ', tvdbid='+ str(tvdbSer) +')'
				print url
				searchText = str(searchText) + ' [' + str(epwatch) + ' of ' + str(eptot) + ']'
				
				if str(aid)=='0' and int(tvdbSer)>0:
					aid = 't' + str(tvdbSer)
				
				if adult=='Yes':
					searchText = '[I]' + searchText + '[/I]'
					mpaa = 'XXX'
					
				addDir(searchText,url,mode,iconimage,numItems=dirLength,aid=aid,descr=description,yr=year,genre=genre,totep=eptot, watchep=epwatch, fanart=fanart, plycnt=playcount, mpaa=mpaa)
			else:
				# if str(aid)=='0' and tvdbSer==0:
					# print base_txt + '---- ' + str(searchText) + ' (aid=' + str(aid) + ', tvdbid='+ str(tvdbSer) +')'
				# else:
					# print base_txt + str(searchText) + ' (aid=' + str(aid) + ', tvdbid='+ str(tvdbSer) +')'
					
				if str(aid)=='0' and int(tvdbSer)>0:
					aid = 't' + str(tvdbSer)
				
				if adult=='Yes':
					searchText = '[I]' + searchText + '[/I]'
					mpaa = 'XXX'
					
				addDir(searchText,url,mode,iconimage,numItems=dirLength,aid=aid,descr=description,yr=year,genre=genre,fanart=fanart, mpaa=mpaa)
		if (pb.iscanceled()): return
	pb.close()	
	
	groupAid = ''
	groupName = ''
	for aid2, name2, url2 in mostPop2:		
		groupName = groupName + ' <--> ' + name2
		if aid2 != '0':
			groupAid = groupAid + ' <--> ' + aid2
			
	if (len(groupAid)>0):
		# addDir(name,url,mode,iconimage,aid='0') <-- overloaded variables used in special as follows
		# MAP: 
		# name = "-- REFRESH --",
		# url = searchText_org *for searching
		# mode = 212
		# iconimage = aid *for searching
		# aid=groupAid
		addDir('-- REFRESH (Re-Search w/ Name) --',groupName,212,'',aid=groupAid)	
	
	skin = xbmc.getSkinDir()
	thumbnail_view = THUMBNAIL_VIEW_IDS.get(skin)
	if thumbnail_view:
		cmd = 'Container.SetViewMode(%s)' % thumbnail_view
		xbmc.executebuiltin(cmd)
	
def getEpisode_Listing_Pages(groupUrls,aid='0'):
	# Extracts the URL and Page name of the various content pages
	# MODE 3 = getEpisode_Listing_Pages
	
	# content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
	# xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	
	iconimageSeries = ''
	epWishWatch = '0'
	tvdbSer = '0'
	fanart = ''
	
	aidDB = '0'
	if aid.isdigit():
		aidDB = aid
	
	# if int(aidDB)>0:
	# [searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList1, season, adult, epwatch, eptot, playcount] = get_all_data(aid=aid)	
	# [searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList1, season, adult, epwatch, eptot, playcount] = cache.cacheFunction(get_all_data,'',aid)
	# [searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList1, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,'',aid)
	[searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList1, season, adult, epwatch, eptot, playcount] = get_detail_db('',aid)

	iconimageSeries = fanart
	epWishWatch = '0'
	watchListTotal = list_watchlisttotal()
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
		urls = groupUrls.split(' <--> ')
	except:
		urls = groupUrls
		
	epListAll = []
	epList = []
	
	
	dirLength = len(urls)	
	print base_txt + '# of items: ' + str(dirLength)
	
	pb = xbmcgui.DialogProgress()
	pb.create('Generating List', 'Episodes')
	
	ii=0	
	updateText = ''
	
	for url in urls:
		ii += 1
		for streamList in streamSiteList:
			siteBase = streamList + '.base_url_name'
			site_base_url_name = eval(siteBase)
			if (site_base_url_name in url):
				# siteBase = streamList + '.Episode_Listing_Pages(url)'
				siteBase = 'cache.cacheFunction(' + streamList + '.Episode_Listing_Pages, url)'
				try:
					epList = eval(siteBase)		
					updateText = 'Grabbing Episodes from: ' + streamList
					print base_txt + str(ii) + ' of ' + str(dirLength) +' - '+ updateText
				except:
					print base_txt + 'FAILED - ' + siteBase					
			pb.update(int(ii/float(dirLength)*100), updateText, url)		
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
				nameTest = html_special(nameTest)
				description = html_special(description)
				addDir(nameTest,groupUrl,mode,iconimageTest,aid=aid,numItems=dirLength,descr=description,yr=yr,mo=mo,day=day,epSeason=epSeasonTest,epNum=epNumTest,fanart=fanart,plycnt=playcount)
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
					epName = utils.U2A(epName)
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
			else:
				nameTest = str(epSeason) + 'x' + str(epNum) + ' - ' + nameTest
				
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

	# addDir('-- REFRESH (Media Sources)--',groupUrls,32,'',aid=aid)
	
	if (aid != '0'):
		# addDir('-- REFRESH (Episode Data) --',groupUrls,31,'',aid=aid)
		addDir('-- REFRESH --',groupUrls,33,'',aid=aid)
			
	skin = xbmc.getSkinDir()
	thumbnail_view = THUMBNAIL_VIEW_IDS.get(skin)
	if thumbnail_view:
		cmd = 'Container.SetViewMode(%s)' % thumbnail_view
		xbmc.executebuiltin(cmd)	
		
def refresh_getEpisode_Listing_Pages(groupUrl):
	# remove entries related to getEpisode_Listing_Pages	

	con = sqlite.connect(cache_path)
	with con:
		cur = con.cursor()
		
		try:
			urls = groupUrl.split(' <--> ')
		except:
			urls = groupUrl
		
		urls = f2(urls)
		
		# grab meida link from the streaming episode page
		for url in urls:
			for streamList in streamSiteList:
				siteBase = streamList + '.base_url_name'
				site_base_url_name = eval(siteBase)
				if (site_base_url_name in url):
					# siteBase = streamList + '.Episode_Page(url)'
					siteBase = 'utils.commonCacheKey(' + streamList + '.Episode_Listing_Pages, url)'
					cacheRemove = 'cache' + eval(siteBase)
		
					sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
					print base_txt + sql
					cur.execute(sql)

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
	
	# grab meida link from the streaming episode page
	ii=0
	for url in urls:
		print base_txt + url
		ii += 1
		epMedia_subdub = []	
		for streamList in streamSiteList:
			updateText = 'Streaming Media from: ' + streamList
			print base_txt + str(ii) + ' of ' + str(dirLength) +' - '+ updateText
			pb.update(int(ii/float(dirLength)*100), updateText)	
			siteBase = streamList + '.base_url_name'
			site_base_url_name = eval(siteBase)
			if (site_base_url_name in url):
				# siteBase = streamList + '.Episode_Page(url)'
				siteBase = 'cache.cacheFunction(' + streamList + '.Episode_Page, url)'
				try:
					epMedia = eval(siteBase)
					if 'dubbed' in url:
						for epMedia_subdub in epMedia:
							epMedia_subdub.append(' - DUB')
					else:
						for epMedia_subdub in epMedia:
							epMedia_subdub.append('')
				except:
					print base_txt + 'FAILED - ' + siteBase
		epMediaAll = epMediaAll + epMedia
	
	print epMediaAll
	
	pb.close()
		
	epMediaAll_2=[]
	siteNnameTest=''
	mirrorTest=0 
	partTest=0
	for siteNname, url, mirror, part, subdub in reversed(epMediaAll):
		if not(siteNnameTest==siteNname and mirrorTest==mirror):
			totParts = part
			siteNnameTest = siteNname 
			mirrorTest = mirror
		epMediaAll_2.append([siteNname, url, mirror, part, totParts, subdub])
		
	epMediaAll_2.sort(key=lambda a:(a[0],a[2],a[3]))
	return epMediaAll_2
		
def getEpisode_PageMerged(groupUrl,iconimage='', aid='0',episodeName=''):
	# Extracts the URL for the content media file
	# MODE 4 = getEpisode_Page
	
	iconimage = str(iconimage)
	# epMediaAll_2 = get_epMediaAll_2(groupUrl)
	epMediaAll_2 = cache.cacheFunction(get_epMediaAll_2,groupUrl)
	[searchText1, aidSer, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList, epList1, season, adult, epwatch, eptot, playcount] = get_detail_db('',aid)
	
	url = ''
	mode = 5
	mediaValid = []
	mediaInValid = []
	for siteNname, url, mirror, part, totParts, subdub in epMediaAll_2:
		name = ''
		# media_url = urlresolver.HostedMediaFile(url).resolve()
		
		if 'vidxden' in url:
			url = 'http://www.vidxden.com/CAPTCHA/nuisance'
		if 'vidbux' in url:
			url = 'http://www.vidbux.com/CAPTCHA/nuisance'
			
		try:
			media_url = urlresolver.HostedMediaFile(url).resolve()
			print base_txt + media_url
			if not('http' in media_url):
				media_url = False
		except:
			media_url = False
		
		if media_url != False:
			if '0067DB' in media_url and '9e2c88bbcf8d3e9c' in media_url:
				media_url = False
		
		if (media_url == False and url.endswith('.flv')):
			media_url = url
			
		if (media_url == False and url.endswith('.mp4')):
			media_url = url
		
		print 'Mirror: ' + str(mirror) + ' Part: ' + str(part)
		url = urllib.unquote(url)
		if media_url:
			media_url = urllib.unquote(media_url)
			print base_txt + media_url
			hostName = urlresolver.HostedMediaFile(url).get_host()
			if len(hostName)<1:
				hostName = media_url.split('/')[2]
			name = name + siteNname + ' -- Mirror ' + str(mirror) + ' - Part ' + str(part) + ' of ' + str(totParts) + ' (' + hostName + subdub + ')' 
			mediaValid.append([name,media_url,iconimage,siteNname,mirror])
		else:
			print base_txt + url + ' <-- VIDEO MAY NOT WORK'
			if len(url.split('/')) > 2:
				name = name + siteNname + ' -- Mirror ' + str(mirror) + ' - Part ' + str(part) + ' of ' + str(totParts) + ' (' + url.split('/')[2] + subdub+ ') -- X'	
			else:
				name = name + siteNname + ' -- Mirror ' + str(mirror) + ' - Part ' + str(part) + ' of ' + str(totParts) + ' (' + url.split('/')[0] + subdub+ ') -- X'
			mediaInValid.append([name,url,iconimage,siteNname,mirror])
	
	
	mediaValid.append(['','','','',''])
	
	mediaList = mediaValid + mediaInValid
	
	if len(mediaValid)>1:
		nameTest = mediaValid[0][0]
		siteNnameTest = mediaValid[0][3]
		mirrorTest = mediaValid[0][4]
		epPlaylist = '' 
		addPlaylistInfo = []
		for name, media_url, iconimage1, siteNname, mirror in mediaValid:
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
					
				epSplit = f2(epPlaylist.split(' <--> '))
				print epSplit
				nameTest = nameTest1 + ' -- Mirror ' + str(mirrorTest) + ' ' + nameTest + ' [' + str(len(epPlaylist.split(' <--> '))) +']'
				print base_txt + nameTest
				print base_txt + epPlaylist
				# addPlaylist(nameTest,epPlaylist,42,'')
				if 'auengine' in nameTest:
					mediaOrder = 10
				elif 'mp4upload' in nameTest:
					mediaOrder = 20
				elif 'video44' in nameTest:
					mediaOrder = 30
				elif 'videoweed' in nameTest:
					mediaOrder = 40
				else:
					mediaOrder = 100
				addPlaylistInfo.append([nameTest,epPlaylist,42,iconimage,mediaOrder])
				nameTest = name
				siteNnameTest = siteNname 
				mirrorTest = mirror
				epPlaylist = media_url
	
		
		addPlaylistInfo.sort(key=lambda name: name[4]) 
		# print addPlaylistInfo
		
		for name, url, mode, iconimage1 ,mediaOrder in addPlaylistInfo:
			addPlaylist(name,url,mode,iconimage,fanart=fanart)
			# if aid != '0':
				# streamSource = name.split(' -- ')[0]
				# epNameSplit = episodeName.replace('[B]','').replace('[/B]','').split()
				# seasonEpisode = epNameSplit.split('x')
				# setStreamMeadiaLink(url,streamSource,aid,seasonEpisode[0],seasonEpisode[1])
	
	if(len(mediaValid) > 0):
		name = 'View List of -- INDIVIDUAL VIDEOS'
		url = ''
		mode = 43
		iconimage = ''
		addDir(name,groupUrl,mode,iconimage,fanart=fanart)
		
	if(len(mediaInValid) > 0):
		name = 'View List of -- POSSIBLY BROKEN VIDEOS'
		url = ''
		mode = 41
		iconimage = ''
		addDir(name,groupUrl,mode,iconimage,fanart=fanart)
		
	if(len(mediaInValid) > 0):
		name = '-- REFRESH --'
		url = ''
		mode = 44
		iconimage = ''
		addDir(name,groupUrl,mode,iconimage)
		
def refresh_getEpisode_PageMerged(groupUrl):
	# remove entries related to getEpisode_PageMerged	

	con = sqlite.connect(cache_path)
	with con:
		cur = con.cursor()
		cacheRemove = 'cache' + utils.commonCacheKey(get_epMediaAll_2,groupUrl)
		
		sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
		print base_txt + sql
		cur.execute(sql)
		
		try:
			urls = groupUrl.split(' <--> ')
		except:
			urls = groupUrl
		
		urls = f2(urls)
		
		# grab meida link from the streaming episode page
		for url in urls:
			for streamList in streamSiteList:
				siteBase = streamList + '.base_url_name'
				site_base_url_name = eval(siteBase)
				if (site_base_url_name in url):
					# siteBase = streamList + '.Episode_Page(url)'
					siteBase = 'utils.commonCacheKey(' + streamList + '.Episode_Page, url)'
					cacheRemove = 'cache' + eval(siteBase)
		
					sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
					print base_txt + sql
					cur.execute(sql)

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
	for siteNname, url, mirror, part, totParts, subdub in epMediaAll_2:
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
	for siteNname, url, mirror, part, totParts, subdub in epMediaAll_2:
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

def getStreamingSiteList(searchText='',url=''):
	# formats the list of of steaming content by streaming site
	
	mostPop = []	
	searchRes = cache.cacheFunction(allAnimeList)
	# searchRes = allAnimeList()
	# print searchRes
	for possLink in searchRes:
		
		if not possLink[1]==None and not possLink[1].startswith('<') and possLink[0].startswith('http'):
			if not searchText == '' and not searchText == None:
				if searchText in possLink[0]:
					mostPop.append([0,possLink[1],possLink[0]])	
			else:					
				mostPop.append([0,possLink[1],possLink[0]])	
	
	name = ''
	nameTest = ''
	mostPop2 = []
	for iconimage, name, urls in mostPop:
		if name.startswith('The '):
			name = name[4:] + ', The'
		mostPop2.append([str(iconimage), name, urls])
		
	try:
		mostPop2.sort(key=lambda name: name[1])
	except:
		pass
		
	return mostPop2
	
def getStreamingSiteList2(searchText='',url=''):
	# formats the list of of steaming content by streaming site
	
	mostPop = []	
	searchRes = cache.cacheFunction(allAnimeList)
	# print searchRes
	for possLink in searchRes:
		
		if not possLink[1]==None and not possLink[1].startswith('<') and possLink[0].startswith('http'):
			if not searchText == '' and not searchText == None:
				if searchText in possLink[0]:
					mostPop.append([0,possLink[1],possLink[0]])	
			else:					
				mostPop.append([0,possLink[1],possLink[0]])	
	
	name = ''
	nameTest = ''
	mostPop2 = []
	for iconimage, name, urls in mostPop:
		if name.startswith('The '):
			name = name[4:] + ', The'
		mostPop2.append([urls, name])
		
	try:
		mostPop2.sort(key=lambda name: name[1])
	except:
		pass
		
	return mostPop2
		
def allAnimeList(url=''):
	# Searches the various websites for the searched content
	
	searchSiteList = []
	
	con = sqlite.connect(user_path)
	with con:
		cur = con.cursor()
		sql = 'CREATE TABLE IF NOT EXISTS SeriesContentLinks(link TEXT PRIMARY KEY, name TEXT, status TEXT)'
		cur.execute(sql)
	
		sql = 'INSERT INTO SeriesContentLinks VALUES(?,?,?)' 
		# print base_txt + sql
		con.text_factory = str
	
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
		aniUrl_list = []
		for streamList, url in searchSiteList:
			siteBase = streamList + '.base_url_name'
			site_base_url = eval(siteBase)
			if (site_base_url in url):
				siteBase = streamList + '.aniUrls'
				site_aniUrls = eval(siteBase)
				for aniUrl in site_aniUrls:
					aniUrl_list.append([streamList,aniUrl])
					
		dirLength = len(aniUrl_list)
		print base_txt + '# of items: ' + str(dirLength)
		pb = xbmcgui.DialogProgress()
		pb.create('Gathering Anime/Cartoon List', '# of items: ' + str(dirLength))
		ii=0
		for streamList,aniUrl in aniUrl_list:
			ii+=1
			updateText = str(ii) + ' of ' + str(dirLength) + ': ' + streamList + ': '
			pb.update(int(ii/float(dirLength)*100), updateText,aniUrl)	
			print base_txt + updateText + aniUrl
			link = ''
			link = grabUrlSource(aniUrl)	
			# try:					
			siteBase = streamList + '.Total_Video_List(link)'
			searchRes = searchRes + eval(siteBase)
			# except:
				# print base_txt + 'FAILED - ' + aniUrl + ' failed to load allAnimeList()'
			searchRes = utils.U2A_List(searchRes)
			row=[]
			for row in searchRes:
				name = convertName(row[1])
				link = row[0]
				if '"' in name:
					name = name.replace('"',"''")
				if '"' in link:
					link = link.replace('"',"%22")
					
				sql_para = (link, name, '')	
				cur.execute('SELECT * FROM SeriesContentLinks WHERE link="%s"' % sql_para[0])   
				rows = cur.fetchall()   
				if len(rows)==0 and not row[1]=='' and not 'Http:' in row[1] and not '<Span' in row[1] and not '<Imgsrc' in row[1]: 
					cur.execute(sql,sql_para)
				# else:
					# print base_txt + 'RECORD ALREADY EXISTS - INSERT INTO SeriesContentLinks ... link = ' + sql_para[0]
				if (pb.iscanceled()): return
		pb.close()
		
		
		
		sql = 'SELECT link, name FROM SeriesContentLinks ORDER BY name'
		print base_txt + sql
		cur.execute(sql)
		searchRes = cur.fetchall()
		# try:			
			# searchRes.sort(key=lambda name: name[1]) 
		# except:
			# print base_txt + 'FAILED - Sorting in allAnimeList()'
			
	# print searchRes	
	searchRes = f2(searchRes)
	return searchRes
		
def refresh_allAnimeList(streamList=''):
	# remove entries related to allAnimeList	

	con = sqlite.connect(cache_path)
	with con:
		cur = con.cursor()
		
		cacheRemove = 'cache' + utils.commonCacheKey(allAnimeList)		
		sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
		print base_txt + sql
		cur.execute(sql)
		
		if (len(streamList) > 0):
			streamSiteListTemp = [streamList]
		else:
			streamSiteListTemp = streamSiteList
		
		for streamList in streamSiteListTemp:
			siteOn = streamList + '_on'
			searchText = ''
			if (dc.getSetting(siteOn) == 'true'):
				siteBase = streamList + '.base_url_name'
				searchText = eval(siteBase)
				cacheRemove = 'cache' + utils.commonCacheKey(getStreamingSiteList,searchText)		
				sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
				print base_txt + sql
				cur.execute(sql)
		
		cacheRemove = 'cache' + utils.commonCacheKey(name2aid)		
		sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
		print base_txt + sql
		cur.execute(sql)
		
	
	con = sqlite.connect(user_path)
	with con:
		cur = con.cursor()		
		sql = 'DELETE FROM SeriesContentLinks;'
		print base_txt + sql
		cur.execute(sql)
		
def refresh_aniURL(searchText):
	# remove entries related to a single streaming site list	
	
	for streamList in streamSiteList:
		if streamList in searchText:
			break
	
	con = sqlite.connect(cache_path)
	with con:
		cur = con.cursor()
		
		siteBase = streamList + '.aniUrls'
		aniUrl_list = eval(siteBase)
		for aniUrl in aniUrl_list:
			cacheRemove = 'cache' + utils.commonCacheKey(grabUrlSource,aniUrl)		
			sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
			print base_txt + sql
			cur.execute(sql)
			cacheRemove = 'cache' + utils.commonCacheKey(utils.grabUrlSource,aniUrl)		
			sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
			print base_txt + sql
			cur.execute(sql)
	
	refresh_allAnimeList(streamList)
	
def allSearchList2(searchText):
	
	searchText_mod1 = searchText + ' '
	searchText_mod2 = ' ' + searchText
	url = ''
	# searchRes = allAnimeList()
	searchRes = cache.cacheFunction(allAnimeList)
	cache.cacheFunction(name2aid)
	# print searchRes
	searchResults = []
	for possLink in searchRes:
		
		if not possLink[1]==None and not possLink[1].startswith('<') and possLink[0].startswith('http'):
			if len(searchText)==1:
				print searchText
				if possLink[1].startswith(searchText) and possLink[1].endswith(searchText):
					searchResults.append(possLink)
					
				# if searchText_mod1 in possLink[1]:
					# searchResults.append(possLink)
					
				# if searchText_mod2 in possLink[1]:
					# searchResults.append(possLink)
			
			else:
				try:
					if searchText in possLink[1]:
						searchResults.append(possLink)
				except:
					pass
	
	return searchResults	
	
def allSearchList(searchText):
	
	# searchRes = allAnimeList()
	cache.cacheFunction(allAnimeList)
	cache.cacheFunction(name2aid)
	# print searchRes
	searchResults = []
	if not searchText == '':
		con = sqlite.connect(user_path)
		with con:
			cur = con.cursor()
			con.text_factory = str
			txt1 = searchText
			txt2 = cleanSearchText(searchText)
			if len(txt1)<3:
				sql = 'SELECT link, name FROM SeriesContentLinks WHERE name LIKE "'+txt1+'%" or name LIKE "'+txt2+'%" ORDER BY name'
			else:
				sql = 'SELECT link, name FROM SeriesContentLinks WHERE name LIKE "%'+txt1+'%" or name LIKE "%'+txt2+'%" ORDER BY name'
			print base_txt + sql
			cur.execute(sql)
			searchResults = cur.fetchall()
			
			# sql = 'SELECT link, name FROM SeriesContentLinks WHERE name LIKE "%'+cleanSearchText(searchText)+'%" ORDER BY name'
			# print base_txt + sql
			# cur.execute(sql)
			# searchResults = searchResults + cur.fetchall()
			
			print searchResults
	return searchResults

def name2aid():
	# create/update content name to aid map
	
	con = sqlite.connect(user_path)
	with con:
		cur = con.cursor()
		sql = 'CREATE TABLE IF NOT EXISTS SeriesNameAID(name TEXT PRIMARY KEY, aid TEXT)'
		cur.execute(sql)
		sql = 'CREATE VIEW IF NOT EXISTS linkAID AS SELECT SeriesContentLinks.link,SeriesContentLinks.name,SeriesNameAID.aid FROM SeriesContentLinks '
		sql = sql + 'LEFT JOIN SeriesNameAID ON SeriesContentLinks.name = SeriesNameAID.name ORDER BY SeriesContentLinks.name'
		cur.execute(sql)
		sql = 'CREATE VIEW IF NOT EXISTS AIDSeries AS SELECT linkAID.*, '
		sql = sql + 't1.tvdbSer, t1.description, t1.fanart, t1.iconimage, t1.genre, t1.year, t1.season, t1.adult, t1.epwatch, t1.eptot, t1.playcount '
		sql = sql + 'FROM linkAID '
		sql = sql + 'LEFT JOIN Series AS t1 ON linkAID.aid = t1.aid ORDER BY name'
		cur.execute(sql)
		
	
	
	# from anime-list.xml
	groupUrl = []
	groupUrl.append('https://raw.github.com/torenado/plugin.video.animestream/master/anime-list_modded.xml')
	groupUrl.append('https://sites.google.com/site/anidblist/anime-list.xml?attredirects=0')
	
	linkAID = ''
	for url in groupUrl:
		linkAID = linkAID + str(grabUrlSource(url))
	aidList = cache.cacheFunction(get_ani_aid_list,linkAID)
	aidList.sort(key=lambda name: name[1]) 
	dirLength = len(aidList)
	print base_txt + '# of items: ' + str(dirLength)
	pb = xbmcgui.DialogProgress()
	pb.create('Updating SeriesNameAID DB: anime-list', '# of items: ' + str(dirLength))
	ii=0
	name2=''
	sql = 'INSERT INTO SeriesNameAID VALUES(?,?)' 
	for aidFound, name, tvdbid, season in  aidList:
		ii+=1				
		with con:
			cur = con.cursor()
			con.text_factory = str
			cur.execute('SELECT * FROM SeriesNameAID WHERE name="%s"' % name)   
			rows = cur.fetchall() 
			
		if len(rows)==0: 
			name2 = name
			updateText = str(ii) + ' of ' + str(dirLength) + ': ' + name2
			print base_txt + updateText
			sql_para = (name, aidFound)
			print sql_para		
			with con:
				cur = con.cursor()
				con.text_factory = str
				cur.execute(sql,sql_para)		
		pb.update(int(ii/float(dirLength)*100),name2,str(ii) + ' of ' + str(dirLength))
		if (pb.iscanceled()): return
	pb.close()
	
	# from get_data_db sites
	with con:
		cur = con.cursor()
		con.text_factory = str
		sql = 'SELECT searchText,aid FROM Series ORDER BY searchText'
		cur.execute(sql)
		searchRes = cur.fetchall() 
	
	dirLength = len(searchRes)
	print base_txt + '# of items: ' + str(dirLength)
	pb = xbmcgui.DialogProgress()
	pb.create('Updating SeriesNameAID DB: Series', '# of items: ' + str(dirLength))
	ii=0
	name2=''
	sql = 'INSERT INTO SeriesNameAID VALUES(?,?)' 
	for searchText in searchRes:
		ii+=1			
		with con:
			cur = con.cursor()
			con.text_factory = str
			cur.execute('SELECT * FROM SeriesNameAID WHERE name="%s"' % searchText[0])   
			rows = cur.fetchall() 
			
		if len(rows)==0:
			name2 = searchText[0] 
			updateText = str(ii) + ' of ' + str(dirLength) + ': ' + name2
			print base_txt + updateText
			sql_para = (searchText[0], searchText[1])
			print sql_para		
			with con:
				cur = con.cursor()
				con.text_factory = str
				cur.execute(sql,sql_para)
		pb.update(int(ii/float(dirLength)*100),name2,str(ii) + ' of ' + str(dirLength))	
		if (pb.iscanceled()): return
	pb.close()
	
	# from aniDBFullList
	groupUrl = []
	groupUrl.append('http://anidb.net/api/animetitles.xml.gz')
	
	linkAID = ''
	for url in groupUrl:
		linkAID = linkAID + str(grabUrlSource(url))
	aidList = anidbQuick.aniDBFullList(linkAID)
	# aidList = cache.cacheFunction(anidbQuick.aniDBFullList,linkAID)
	aidList.sort(key=lambda name: name[1]) 
	dirLength = len(aidList)
	print base_txt + '# of items: ' + str(dirLength)
	pb = xbmcgui.DialogProgress()
	pb.create('Updating SeriesNameAID DB: aniDBFullList', '# of items: ' + str(dirLength))
	ii=0
	name2=''
	sql = 'INSERT INTO SeriesNameAID VALUES(?,?)' 
	for aidFound, name, eps in  aidList:
		ii+=1	
		with con:
			cur = con.cursor()
			con.text_factory = str
			cur.execute('SELECT * FROM SeriesNameAID WHERE name="%s"' % name)   
			rows = cur.fetchall() 
			
		if len(rows)==0: 
			name2 = name
			updateText = str(ii) + ' of ' + str(dirLength) + ': ' + name2
			print base_txt + updateText
			sql_para = (name, aidFound)
			print sql_para		
			with con:
				cur = con.cursor()
				con.text_factory = str
				cur.execute(sql,sql_para)
		pb.update(int(ii/float(dirLength)*100),name2,str(ii) + ' of ' + str(dirLength))	
		if (pb.iscanceled()): return
	pb.close()
	
	# from streaming sites
	with con:
		cur = con.cursor()
		con.text_factory = str
		sql = 'SELECT DISTINCT name FROM SeriesContentLinks ORDER BY name'
		print base_txt + sql
		cur.execute(sql)
		searchRes = cur.fetchall()
	dirLength = len(searchRes)
	print base_txt + '# of items: ' + str(dirLength)
	pb = xbmcgui.DialogProgress()
	pb.create('Updating SeriesNameAID DB: SeriesContentLinks', '# of items: ' + str(dirLength))
	ii=0
	name2=''
	sql = 'INSERT INTO SeriesNameAID VALUES(?,?)' 
	for searchText in searchRes:
		ii+=1				
		with con:
			cur = con.cursor()
			con.text_factory = str
			cur.execute('SELECT * FROM SeriesNameAID WHERE name="%s"' % searchText[0])   
			rows = cur.fetchall() 
			
		if len(rows)==0: 
			name2 = searchText[0] 
			updateText = str(ii) + ' of ' + str(dirLength) + ': ' + name2
			print base_txt + updateText
			sql_para = (searchText[0], get_detail_db(searchText[0])[1])
			print sql_para		
			with con:
				cur = con.cursor()
				con.text_factory = str
				cur.execute(sql,sql_para)
		pb.update(int(ii/float(dirLength)*100),name2,str(ii) + ' of ' + str(dirLength))	
		if (pb.iscanceled()): return
	pb.close()
		
	with con:
		cur = con.cursor()
		con.text_factory = str
		sql = 'SELECT * FROM SeriesNameAID ORDER BY name'
		print base_txt + sql
		cur.execute(sql)
		return cur.fetchall()
		
def searchCollection_2(searchText='',aid='0',outSearchName=False):
	# Searches the various websites for the searched content
	searchRes = []
	searchAlts = []
	searchText = cleanSearchText(searchText)
	
	
	ii=0
	dirLength = 1
	pb = xbmcgui.DialogProgress()
	pb.create('Generating Search Text for ... ', str(aid) + ' - ' + searchText)
	if len(searchText)>0:
		updateText = searchText
		pb.update(int(ii/float(dirLength)*100), updateText)
		print base_txt + 'Generating Search Text for ... ' + updateText
		searchAlts.append(searchText)
		if (pb.iscanceled()): return
	
	for name1 in get_ani_searchText(aid):
		updateText = name1
		pb.update(int(ii/float(dirLength)*100), updateText)
		print base_txt + 'Generating Search Text for ... ' + updateText
		searchAlts.append(name1)
		# searchRes = searchRes + cache.cacheFunction(allSearchList,name1)
		if (pb.iscanceled()): return
	
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
		# [searchText1, aid1, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList1, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,'',aidDB)
		# [searchText1, aid1, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList1, epList, season, adult, epwatch, eptot, playcount] = get_detail_db('',aidDB)
		[searchText1, aid1, tvdbSer, description, fanart, iconimage1, genre, year, simAniList, synAniList1, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_detail_db,'',aidDB)
		
		if (int(aidDB)>0 and len(synAniList1)>0):
			dirLength = len(synAniList1)
			print synAniList1
			print base_txt + '# of Synonym items: ' + str(dirLength)
			ii=0
			for aidAlt, name in synAniList1:
				subLoc = name.find('(')
				if subLoc > 0:
					name = name[:subLoc]
				name = urllib.unquote(name).title()
				ii+=1
				updateText = str(ii) + ' of ' + str(dirLength) + ': ' + name
				pb.update(int(ii/float(dirLength)*100), updateText)
				print base_txt + 'Generating Search Text for ... ' + updateText
				# print base_txt + 'Searching for ... ' + name
				# searchRes = searchRes + cache.cacheFunction(allSearchList,name)
				# print len(searchAlts)
				searchAlts.append(name)
				
				searchAlts = searchAlts + altName(name,' ')
				
				searchAlts = searchAlts + altName(name,']')
				searchAlts = searchAlts + altName(name,'[')
				searchAlts = searchAlts + altName(altName(name,'['),']')
				
				searchAlts = searchAlts + altName(name,')')
				searchAlts = searchAlts + altName(name,'(')
				searchAlts = searchAlts + altName(altName(name,'('),')')
				
				searchAlts = searchAlts + altName(name,':')
				searchAlts = searchAlts + altName(name,'\:')
				searchAlts = searchAlts + altName(name,'!')
				ssearchAlts = searchAlts + altName(altName(name,':'),'!')
				ssearchAlts = searchAlts + altName(altName(name,'\:'),'!')
				
				searchAlts = searchAlts + altName(name,';')
				searchAlts = searchAlts + altName(name,'\'')
				searchAlts = searchAlts + altName(name,'`')
				searchAlts = searchAlts + altName(name,'?')
				searchAlts = searchAlts + altName(name,'-')
				searchAlts = searchAlts + altName(name,'~')
				searchAlts = searchAlts + altName(name,'.')
				searchAlts = searchAlts + altName(name,',')
				searchAlts = searchAlts + altName(name,'/')
				searchAlts = searchAlts + altName(name,'\\')
				
				if name.startswith('The'):
					searchAlts.append(name.replace('The ',''))
				
				searchAlts = searchAlts + altName(searchAlts,' ')
				searchAlts = f2(searchAlts)
				if (pb.iscanceled()): return
	pb.close()
	
	print searchAlts
	pb = xbmcgui.DialogProgress()
	pb.create('Searching for ... ', 'Alternate names + variations')
	print base_txt + 'Searching ' + str(len(searchAlts)) + ' alternate names + variations'	
	dirLength = len(searchAlts)	
	ii=0
	for nameSearch in searchAlts:
		ii+=1
		updateText = str(ii) + ' of ' + str(dirLength) + ': ' + nameSearch
		pb.update(int(ii/float(dirLength)*100), updateText)
		print base_txt + 'Searching for ... ' + updateText
		searchRes = searchRes + cache.cacheFunction(allSearchList,nameSearch)
		if (pb.iscanceled()): return
	pb.close()
	
	searchRes.append(['','zzzzzzEND'])
	if outSearchName:
		return searchAlts
	else:
		return searchRes

def searchCollection(searchText,aid='0'):
	
	searchRes = searchCollection_2(searchText,aid)
	print searchRes
	tempsearchRes = searchRes
	searchRes = []
	for url, name in tempsearchRes:
		name = convertName(name, url)
		searchRes.append([url,name])
	
	
	searchRes = utils.U2A_List(searchRes)
	try:
		searchRes.sort(key=lambda name: name[1]) 
	except:
		print base_txt + 'Sorting failed in SEARCH()'
	
	searchRes = f2(searchRes)
	
	# print searchRes
	# searchRes = filter(None, searchRes)
	# print searchRes

	return combinedSearchCollect(searchRes)

def altName(name,removeText):
	
	searchAlts = []
	name1 = name
	if isinstance(name,list):
		for name in name1:
			name = name.replace(removeText,' ')
			name = name.replace('  ',' ')
			name = name.replace('  ',' ')
			name = name.replace('  ',' ')
			name = name.replace('  ',' ')
			name = name.replace('  ',' ')
			searchAlts.append(name)
			searchAlts.append(convertName(name))
			name = name.replace(removeText,'')
			name = name.replace('  ',' ')
			name = name.replace('  ',' ')
			name = name.replace('  ',' ')
			name = name.replace('  ',' ')
			name = name.replace('  ',' ')
			searchAlts.append(name)
			searchAlts.append(convertName(name))
	elif isinstance(name,str):
		name = name.replace(removeText,' ')
		name = name.replace('  ',' ')
		name = name.replace('  ',' ')
		name = name.replace('  ',' ')
		name = name.replace('  ',' ')
		name = name.replace('  ',' ')
		searchAlts.append(name)
		# searchAlts.append(convertName(name))
		name = name.replace(removeText,'')
		name = name.replace('  ',' ')
		name = name.replace('  ',' ')
		name = name.replace('  ',' ')
		name = name.replace('  ',' ')
		name = name.replace('  ',' ')
		searchAlts.append(name)
		# searchAlts.append(convertName(name))
	
	return 	searchAlts
	
def convertName(name, url=''):
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
	if 'Oad' in name:
		name = name.replace(' Oad',' ').strip() + ' (Movie/OVA)'
	if 'Featurettes' in name:
		name = name.replace(' Featurettes',' ').strip() + ' (Movie/OVA)'
	if 'ova' in url:
		name = name.strip() + ' (Movie/OVA)'
		
	if 'Tv Special' in name:
		name = name.replace(' Tv Special',' ').strip() + ' (Movie/OVA)'		
	if ' Specials' in name:
		name = name.replace(' Specials',' ').strip() + ' (Movie/OVA)'		
	if ' Special' in name:
		name = name.replace(' Special',' ').strip() + ' (Movie/OVA)'
	if 'special' in url:
		name = name.strip() + ' (Movie/OVA)'
	
	name = name.replace('(Movie) (Movie/Ova)','(Movie/OVA)')
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
	name = name.replace('(Movie/Ova) (Movie/Ova)','(Movie/OVA)').replace('(Movie/Ova) (Movie/OVA)','(Movie/OVA)')
	name = name.replace('(Movie/OVA) (Movie/OVA)','(Movie/OVA)')
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
	name = name.replace(' Raw','(Raw)')
	name = name.replace(' Uncensored','(Uncensored)')
	# name = name.replace('Shippuden','Shippuuden')
	# name = name.replace('Shipuden','Shippuuden')
	# name = name.replace('Shipuuden','Shippuuden')
	name = name.replace('Dragonball','Dragon Ball')
	name = name.replace('Diamonddust','Diamond Dust')
	name = name.replace('Highschool','High School')
	name = name.replace('Fatestaynightunlimitedbladeworks','Fate Stay Night Unlimited Blade Works')
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
	name = name.replace('((','(').replace('))',')')
	name = html_special(name)
	return name
	
def combinedSearchCollect(searchRes):
	
	nameTest = ''
	url = ''
	mode = 3
	iconimage = ''
	searchCollect = []
	dirLength = len(searchRes)
	print base_txt + '# of items: ' + str(dirLength)
	pb = xbmcgui.DialogProgress()
	pb.create('Searching for Series', '# of items: ' + str(dirLength))
	ii=0
	for url, name in searchRes:
		name = convertName(name, url)
		ii+=1
		name = name.title().strip()
		if not nameTest.replace(' ','').title() == name.replace(' ','').title():
			if not nameTest == '':
				# nameTest2 = cleanSearchText(nameTest)
				# [searchText2, aidSer, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_all_data(nameTest2)
				# [searchText2, aidSer, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache.cacheFunction(get_all_data,nameTest2)
				[searchText2, aidSer, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_detail_db,nameTest)
				# [searchText2, aidSer, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_detail_db(nameTest)
				cache7.cacheFunction(get_detail_db,'',str(aidSer))
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
				searchCollect.append([aidSerDB, nameTest, groupUrl, firstName[0],int(season)])
				
			groupUrl = ''
			nameTest = name
		
		if nameTest == name:
			groupUrl = groupUrl +' <--> '+ url
		
		updateText = str(ii) + ' of ' + str(dirLength) + ': ' + nameTest
		print base_txt + updateText
		pb.update(int(ii/float(dirLength)*100), updateText)	
		if (pb.iscanceled()): return
	pb.close()
		
	searchCollect_2 = [] + searchCollect
	try:
		searchCollect_2.sort(key=lambda name: name[3]) 
		searchCollect_2.sort(key=lambda name: name[4]) 
		searchCollect_2.sort(key=lambda name: name[0], reverse=True) 
	except:
		print base_txt + 'Sorting failed in SEARCH() regarding searchCollect_2'
	searchCollect_2.append(['', 'Zzzzzzend', '','',''])
	
	combinedSearchCollect=[]
	combinedSearchCollect2=[]
	aidSerTest=''
	nameTest=''
	groupUrls=''
	for aidSer, name, groupUrl, firstName, season in searchCollect_2:
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
	
	
	combinedSearchCollect.sort(key=lambda name: name[1]) 
	for aidSerTest, nameTest, groupUrl in combinedSearchCollect:
		if nameTest.endswith('The') or nameTest.endswith('The '):
			nameTest = nameTest[:-3] + ', The'
		combinedSearchCollect2.append([str(aidSerTest), nameTest, groupUrl])
	
	print combinedSearchCollect2
	# return searchCollect
	return combinedSearchCollect2
		
def refresh_searchCollection(groupAid,groupName=''):
	print base_txt + 'Remove entries related to searchCollection'

	try:
		aid_mult = groupAid.split(' <--> ')
	except:
		aid_mult = groupAid

	try:
		name_mult = groupName.split(' <--> ')
	except:
		name_mult = groupName

	con = sqlite.connect(cache_path)
	with con:
		cur = con.cursor()
		for aid in aid_mult:
			if aid != '' and aid != '0':
				print base_txt + 'Removing cache related to aid: ' + str(aid)
				searchAlts = searchCollection_2('',aid,outSearchName=True)		
				for nameSearch in searchAlts:
					cacheRemove = 'cache' + utils.commonCacheKey(allSearchList,nameSearch)					
					sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
					print base_txt + sql
					cur.execute(sql)
						
		for nameSearch in name_mult:
			print base_txt + 'Removing cache related to name: ' + nameSearch
			cacheRemove = 'cache' + utils.commonCacheKey(get_detail_db,nameSearch)
			sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
			print base_txt + sql
			cur.execute(sql)
			cacheRemove = 'cache7' + utils.commonCacheKey(get_detail_db,nameSearch)
			sql = 'DELETE FROM '+plugin_name+' WHERE name = "'+cacheRemove+'"'
			print base_txt + sql
			cur.execute(sql)
	
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
	
def addDir(name,url,mode,iconimage,numItems=1,aid='0',descr='',yr='1900',genre='',totep='0',watchep='0',epSeason=1, epNum=0, mo='01', day='01', fanart='', plycnt=0, mpaa='PG-13'):
	# XBMC: create directory
	
	aid = str(aid)	
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&aid="+urllib.quote_plus(aid)+"&iconimage="+urllib.quote_plus(iconimage)
	ok=True
	unwatchep = '0'
	airdate = str(yr)+'-'+str(mo).zfill(2)+'-'+str(day).zfill(2)
	totep = str(totep)
	watchep = str(watchep)
	if (len(totep)>0 and len(str(watchep))>0):
		unwatchep = str(int(totep)-int(watchep))
	
	if plycnt > 0:
		watched = True
	else:
		watched = False
		
	name = urllib.unquote(name)
	name = html_special(name)
	
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title":name, "Plot":descr, "Year":yr, "Genre":genre,"Season":epSeason,"Episode":epNum,"Aired":airdate,"PlayCount":plycnt,"Watched":watched,"Mpaa":mpaa} )
	liz.setProperty('Fanart_Image',fanart)
	liz.setProperty('TotalEpisodes',totep)
	liz.setProperty('WatchedEpisodes',watchep)
	liz.setProperty('UnWatchedEpisodes',unwatchep)
	contextMenuItems = []
	contextMenuItems.append(('Toggle General Content', 'XBMC.RunPlugin(%s?mode=162&name=%s)' % (sys.argv[0], 'general')))
	contextMenuItems.append(('Toggle Adult Content', 'XBMC.RunPlugin(%s?mode=162&name=%s)' % (sys.argv[0],  'adult')))		
	liz.addContextMenuItems(contextMenuItems, replaceItems=True)
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

def addPlaylist(name,url,mode,iconimage,descr='',fanart=''):
	# XBMC: create playlist link
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&aid="+str(aid)
	ok=True
	
	name = urllib.unquote(name)
	
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title":name, "Plot":descr} )
	liz.setProperty('Fanart_Image',fanart)
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
	try:
		link = cache.cacheFunction(utils.grabUrlSource,url)
		# link = cache.cacheFunction(grabUrlSource_Src,url)
	except:		
		print base_txt + 'grabUrlSource FAILED'
		link = 'No Dice'
		print base_txt + link + ' - ' + url
		
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
	
def html_special(text):

	text = text.replace('&lsquo;',"'")
	text = text.replace('&Lsquo;',"'")
	text = text.replace('&rsquo;',"'")
	text = text.replace('&Rsquo;',"'")
	text = text.replace('&quot;','"')
	text = text.replace('&Quot;','"')
	text = text.replace('&8217;',"'")
	
	return text

def unknown_list():
	# create/update content name to aid map
	
	con = sqlite.connect(user_path)
	with con:
		cur = con.cursor()
		con.text_factory = str
		sql = 'SELECT status,name,link FROM SeriesContentLinks WHERE name IN (SELECT name FROM SeriesNameAID WHERE aid LIKE "un%") ORDER BY name'
		print base_txt + sql
		cur.execute(sql)
		return cur.fetchall()

def unknown_list2():
	# create/update content name to aid map
	
	con = sqlite.connect(user_path)
	with con:
		cur = con.cursor()
		con.text_factory = str
		sql = 'SELECT status,name,link FROM SeriesContentLinks WHERE name IN (SELECT name FROM SeriesNameAID WHERE aid LIKE "un%") ORDER BY name'
		sql = 'SELECT substr(name,1,5),aid FROM SeriesNameAID WHERE aid LIKE "un%" ORDER BY name'
		sql = 'SELECT SUBSTR(searchText,1,5)||"%" FROM Series WHERE searchText LIKE "z%" ORDER BY searchText'
		sql = 'SELECT searchText,aid FROM Series WHERE searchText LIKE "z%" ORDER BY searchText'
		print base_txt + sql
		cur.execute(sql)
		rows = cur.fetchall()
		
	for row in rows:
		print row
		
def unknown_list3():
	# create/update content name to aid map
	
	con = sqlite.connect(user_path)
	with con:
		cur = con.cursor()
		con.text_factory = str
		sql = 'SELECT link,name FROM SeriesContentLinks WHERE name IN (SELECT name FROM SeriesNameAID WHERE aid LIKE "un%") ORDER BY name'
		print base_txt + sql
		cur.execute(sql)
		return cur.fetchall()
		
def alpha_list(alpha):
	# create/update content name to aid map
	
	con = sqlite.connect(user_path)
	with con:
		cur = con.cursor()
		con.text_factory = str
		# sql = 'SELECT status,name,link FROM SeriesContentLinks WHERE name LIKE "'+alpha+'%" ORDER BY name'
		sql = 'SELECT aid,searchText,adult FROM Series WHERE searchText LIKE "'+alpha+'%" ORDER BY searchText'
		print base_txt + sql
		cur.execute(sql)
		return cur.fetchall()
		
def alpha_list2(alpha):
	# create/update content name to aid map
	
	con = sqlite.connect(user_path)
	with con:
		cur = con.cursor()
		con.text_factory = str
		sql = 'SELECT link,name FROM SeriesContentLinks WHERE name LIKE "'+alpha+'%" ORDER BY name'
		# sql = 'SELECT aid,searchText,adult FROM Series WHERE searchText LIKE "'+alpha+'%" ORDER BY searchText'
		print base_txt + sql
		cur.execute(sql)
		return cur.fetchall()
	
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
iconimage=None
aid=None


watchListTotal = []

# pre-cache aniDB MyWishlist
# if (len(unid)>0 and len(pubpass)>0) :
	# watchWishlist = cache.cacheFunction(get_aniDB_list)
	# watchMylistSummary_List = cache.cacheFunction(get_aniDB_mysummarylist)
	# watchListTotal = f2(watchWishlist)

# pre-cache aniDB MyList
# if (len(uname)>0 and len(passwd)>0) :
	# watchMylistSummary = cache.cacheFunction(get_aniDB_mysummarylist_OLD)
	# watchListTotal = f2(watchListTotal + watchMylistSummary)

# if (datetime.today().hour > 2 and datetime.today().hour < 6):	
	# print base_txt + 'pre-cache all activated streaming website series lists'
	# cache.cacheFunction(allAnimeList)
	
	# print base_txt + 'pre-cache all the aniDB MyWishlist and MyList series data'
	# dirLength = len(watchListTotal)	
	# print base_txt + '# of items: ' + str(dirLength)
	# pb = xbmcgui.DialogProgress()
	# pb.create('Generating List', 'Total aniDB List')
	# ii=0
	# for aidDB, name1, ep1 in watchListTotal:
		# ii+=1
		# [searchText, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = cache7.cacheFunction(get_all_data,'',str(aidDB))
		# [searchText, aid, tvdbSer, description, fanart, iconimage2, genre, year, simAniList, synAniList, epList, season, adult, epwatch, eptot, playcount] = get_detail_db('',str(aidDB))
		
		# updateText = searchText
		# print base_txt + str(ii) + ' of ' + str(dirLength) +' - '+ updateText
		# pb.update(int(ii/float(dirLength)*100), updateText)	
	# pb.close()
	
	# mostPop = []
	# print base_txt + 'pre-cache cartoon list'
	# for url in cartoonUrls:
		# for streamList in streamSiteList:
			# if streamList in url:
				# siteBase = 'cache7.cacheFunction(' + streamList + '.Video_List_And_Pagination, url)'
				# mostPop = mostPop + eval(siteBase)
		
				
	# print base_txt + 'pre-cache most popular & most recent lists'
	# for url in mostUrls:
		# mostPop = mostPop + cache7.cacheFunction(animecrazy.Video_List_And_Pagination, url)
	
	
	# print base_txt + 'pre-cache allData based on series title'
	# mostPop2 = []
	# for iconimage, name, urls in mostPop:
		# if name.startswith('The '):
			# name = name[4:] + ', The'
		# mostPop2.append([str(iconimage), name, urls])
	
	# mostPop2.sort(key=lambda name: name[1])
	# mostPop2 = f2(mostPop2)
	# for iconimage, name, url in mostPop2:
		# searchText = cleanSearchText(name,True)
		# cache7.cacheFunction(get_all_data,searchText)
		
	# searchText = None
	# mostPop = None
	# mostPop2 = None
	# url = None

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
	iconimage=urllib.unquote_plus(params["iconimage"])
except:
	pass
try:
	# aid=str(params["aid"])
	aid=urllib.unquote_plus(params["aid"])
except:
	pass

				

if mode==None:
	HOME()

elif mode==10:
	ANIME() 

elif mode==11:
	CARTOON() 

elif mode==20:
	STREAMING_SITE() 

elif mode==21:
	STREAMING_SITE_LIST(url) 
	
elif mode==211:
	refresh_aniURL(url)
	STREAMING_SITE_LIST(url) 
	
elif mode==22:
	refresh_allAnimeList()
	STREAMING_SITE() 
	
elif mode==23:
	refresh_un_detail_db()
	STREAMING_SITE() 

elif mode==24:
	UNKNOWN_LIST() 

elif mode==25:
	STREAMING_SITE_A_Z_LIST() 

elif mode==251:
	STREAMING_SITE_A_Z_LIST_SERIES(url) 

elif mode==1:
	MOST_POPULAR(url) 
		
elif mode==2:
	SEARCH(name,aid) 
		
elif mode==211:
	refresh_searchCollection(aid) # <-- overloaded variables used: see SEARCH function
	refresh_detail_db(aid) # <-- overloaded variables used: see SEARCH function
	cache.cacheFunction(name2aid)
	SEARCH(url,iconimage) # <-- overloaded variables used: see SEARCH function
		
elif mode==212:
	refresh_searchCollection(aid,url) # <-- overloaded variables used: see SEARCH function
	refresh_detail_db(aid) # <-- overloaded variables used: see SEARCH function
	cache.cacheFunction(name2aid)
	if (url != None and len(url)>1) or (iconimage != None and len(iconimage)>1):
		SEARCH(url,iconimage) # <-- overloaded variables used: see SEARCH function
	else:
		addDir('-- REFRESH Complete --','',0,'')
	
elif mode==3:
	getEpisode_Listing_Pages(url,aid)
		
# elif mode==31:
	# refresh_detail_db(aid)
	# getEpisode_Listing_Pages(url,aid)
	
# elif mode==32:
	# refresh_getEpisode_Listing_Pages(url)
	# getEpisode_Listing_Pages(url,aid)
	
elif mode==33:
	refresh_detail_db(aid)
	refresh_getEpisode_Listing_Pages(url)
	getEpisode_Listing_Pages(url,aid)
		
elif mode==4:
	getEpisode_PageMerged(url,iconimage,aid,name)

elif mode==41:
	getEpisode_Page_Fail(url)

elif mode==42:
	PLAYLIST_VIDEOLINKS(url,name)

elif mode==43:
	getEpisode_Page(url)

elif mode==44:
	refresh_getEpisode_PageMerged(url)
	# getEpisode_PageMerged(url)
		
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

elif mode==122:
	refresh_detail_db(aid)
	ANIDB_WISHLIST(url)

elif mode==13:
	ANIDB_MYLIST(url)
		
elif mode==14:
	ANIDB_MYLIST_WATCHING(url)

elif mode==15:
	ANIDB_HOTANIME(url)

elif mode==16:
	SETTINGS()

elif mode==161:
	refresh_allAnimeList()

elif mode==163:
	refresh_un_detail_db()

elif mode==162:
	TOGGEL_CONTENT_VISIBILITY(name)

elif mode==164:
	print unknown_list()

elif mode==165:
	refresh_get_aniDB_list()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
