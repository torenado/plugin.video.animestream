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

sys.path.append("./sites")

import utils
import anidbQuick
import anime44
import animecrazy
import animeflavor
import animefushigi
import animetip
import myanimelinks

try:
	import StorageServer
except:
	import storageserverdummy as StorageServer
cache = StorageServer.StorageServer("animestream", 24) # (Your plugin name, Cache time in hours)

#testing in shell
#TEST 1
# python -c "execfile('default2.py'); getEpisode_Listing_Pages('http://www.animefushigi.com/anime/fairy-tail')"
# python -c "execfile('default2.py'); getEpisode_Listing_Pages('http://www.animetip.com/watch-anime/f/fairy-tail')"
# python -c "execfile('default2.py'); getEpisode_Listing_Pages('http://www.animecrazy.net/fairy-tail-anime/')"
# python -c "execfile('default2.py'); getEpisode_Listing_Pages('http://www.myanimelinks.com/category/fairy-tail/')"
# python -c "execfile('default2.py'); getEpisode_Listing_Pages('http://www.animeflavor.com/index.php?q=node/4871')"

#TEST 2
# python -c "execfile('default2.py'); getEpisode_Page('http://www.animefushigi.com/watch/fairy-tail-episode-90')"
# python -c "execfile('default2.py'); getEpisode_Page('http://www.animetip.com/watch-anime/f/fairy-tail/fairy-tail-episode-90.html')"
# python -c "execfile('default2.py'); getEpisode_Page('http://www.animecrazy.net/fairy-tail-episode-90/')"
# python -c "execfile('default2.py'); getEpisode_Page('http://www.myanimelinks.com/fairy-tail-episode-90/')"
# python -c "execfile('default2.py'); getEpisode_Page('http://www.animeflavor.com/index.php?q=node/19518')"

#TEST 3
# python -c "execfile('default.py'); MOST_POPULAR()"

#TEST 4
# python -c "execfile('default.py'); SEARCH('Fairy Tail')"
	
#animestream
# modded from --> <addon id="plugin.video.animecrazy" name="Anime Crazy" version="1.0.9" provider-name="AJ">
dc=xbmcaddon.Addon(id='plugin.video.animestream')
addonPath=os.getcwd()
#artPath=addonPath+'/resources/art'
mozilla_user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
base_txt = 'animestream: '

# aniDB Login
uname = dc.getSetting('username')
passwd = dc.getSetting('pass')

# aniDB Public Wishlist
unid = dc.getSetting('uid')
pubpass = dc.getSetting('pubpass')

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
	addDir('Anime','',10,'')
	addDir('Cartoons','',11,'')
	addDir('Search','',7,'')

def ANIME():
	# XBMC: Anime screen
	print base_txt + 'Create Anime Screen'
	
	if (len(unid)>0 and len(pubpass)>0) :
		addDir('aniDB Wishlist','',12,'')
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
	
	# watchWishlist = get_aniDB_list()
	# watchWishlist = cache.cacheFunction(get_aniDB_list)
	dirLength = len(watchWishlist)
	print base_txt + '# of items: ' + str(dirLength)
	
	name = ''
	url = ''
	mode = 2
	iconimage = ''
	for aid, name, eps in watchWishlist:
		if len(name)>0:
			# linkAID = get_ani_detail(aid)
			linkAID = cache.cacheFunction(get_ani_detail,aid)
			
			# ani_detail = anidbQuick.AID_Resolution(linkAID)
			ani_detail = cache.cacheFunction(anidbQuick.AID_Resolution,linkAID)
			
			tvdbSer = get_tvdb_id(aid)[0]
			fanart = ''
			tvdbid = 0
			if int(tvdbSer)>0:
				# linkTVDB = get_tvdb_detail(tvdbSer)
				linkTVDB = cache.cacheFunction(get_tvdb_detail,tvdbSer)
				
				# tvdb_detail = anidbQuick.TVDBID_Resolution(aid,linkTVDB)
				tvdb_detail = cache.cacheFunction(anidbQuick.TVDBID_Resolution,aid,linkTVDB)
				
				tvdbid = tvdb_detail[1]
				fanart = tvdb_detail[3]
			
			iconimage = ani_detail[1]
			description = ani_detail[2]
			
			if len(ani_detail[3])>1:
				year = int(ani_detail[3][0])
			else:
				year = 1901
				
			if len(ani_detail[9])>0:
				genre = " / ".join(ani_detail[9])
			else: 
				genre ='Animation'
			
			epwatch = eps[0]
			eptot = eps[1]
			
			print base_txt + name + ' [' + epwatch + ' of ' + eptot + '] (aid=' + aid + ', tvdbid='+ str(tvdbid) +') -- ' + iconimage
			
			# if (len(ani_detail)>6):
				# print ani_detail[6]
				
			searchText = name + ' [' + epwatch + ' of ' + eptot + ']' 
			if searchText == '-- NEXT PAGE --':
				mode = 1
				url = iconimage
				iconimage = ''
			
			if eptot == 'TBC':
				eptot = str(ani_detail[4])
			
			if epwatch==eptot:
				playcount = 1
			else:
				playcount = 0
			
			if fanart=='':
				fanart=iconimage
			
			addDir(searchText,url,mode,iconimage,numItems=dirLength,aid=str(aid),descr=description,yr=year,genre=genre,totep=eptot, watchep=epwatch, fanart=fanart, plycnt=playcount)
		aid = None
		
def ANIDB_SIMILAR(aid_org):
	# MODE 121 = ANIDB_SIMILAR

	print base_txt + 'Create Similar Title(s) Screen'
	
	# content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
	# xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	
	# linkAID = get_ani_detail(aid_org)
	linkAID = cache.cacheFunction(get_ani_detail,aid_org)
	
	# ani_detail_org = anidbQuick.AID_Resolution(linkAID)
	ani_detail_org = cache.cacheFunction(anidbQuick.AID_Resolution,linkAID)
	
	dirLength = len(ani_detail_org[6])
	print base_txt + '# of items: ' + str(dirLength)
	
	name = ''
	url = ''
	mode = 2
	iconimage = ''
	for aid, name in ani_detail_org[6]:
	
		epwatch = '0'
		for aidWish, nameWish, epsWish in watchListTotal:
			if int(aid) == int(aidWish):
				epwatch = str(epsWish[0])
				break
				
		# linkAID = get_ani_detail(aid)
		linkAID = cache.cacheFunction(get_ani_detail,aid)
		
		# ani_detail = anidbQuick.AID_Resolution(linkAID)
		ani_detail = cache.cacheFunction(anidbQuick.AID_Resolution,linkAID)
		
		tvdbSer = get_tvdb_id(aid)[0]
		fanart = ''
		tvdbid = 0
		if int(tvdbSer)>0:
			# linkTVDB = get_tvdb_detail(tvdbSer)
			linkTVDB = cache.cacheFunction(get_tvdb_detail,tvdbSer)
			
			# tvdb_detail = anidbQuick.TVDBID_Resolution(aid,linkTVDB)
			tvdb_detail = cache.cacheFunction(anidbQuick.TVDBID_Resolution,aid,linkTVDB)
			
			tvdbid = tvdb_detail[1]
			fanart = tvdb_detail[3]
		
		iconimage = ani_detail[1]
		description = ani_detail[2]
		if len(ani_detail[3])>1:
			year = int(ani_detail[3][0])
		else:
			year = 1901
		
		if len(ani_detail[9])>0:
			genre = " / ".join(ani_detail[9])
		else: 
			genre ='Animation'
		
		# if (len(ani_detail)>6):
			# print ani_detail[6]
			
		searchText = name
		if searchText == '-- NEXT PAGE --':
			mode = 1
			url = iconimage
			iconimage = ''
			
		eptot = str(ani_detail[4])
			
		if epwatch==eptot:
			playcount = 1
		else:
			playcount = 0
		
		if fanart=='':
			fanart=iconimage
			
		if int(epwatch)>0:
			print base_txt + name + ' [' + epwatch + ' of ' + eptot + '] (aid=' + aid + ', tvdbid='+ str(tvdbid) +') -- ' + iconimage
			searchText = name + ' [' + epwatch + ' of ' + eptot + ']' 
		else:
			print base_txt + name + ' (aid=' + aid + ', tvdbid='+ str(tvdbid) +') -- ' + iconimage
		
		addDir(searchText,url,mode,iconimage,numItems=dirLength,aid=aid,descr=description,yr=year,genre=genre,totep=eptot, watchep=epwatch, fanart=fanart, plycnt=playcount)
		aid = None
		
	skin = xbmc.getSkinDir()
	thumbnail_view = THUMBNAIL_VIEW_IDS.get(skin)
	if thumbnail_view:
		cmd = 'Container.SetViewMode(%s)' % thumbnail_view
		xbmc.executebuiltin(cmd)

def MOST_POPULAR(url=''):
	# Hardcoded to use animecrazy.net
	# MODE 1 = MOST_POPULAR
	
	# content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	
	if url == '':
		url = 'http://www.animecrazy.net/most-popular/'
	# mostPop = animecrazy.Video_List_And_Pagination(url)
	mostPop = cache.cacheFunction(animecrazy.Video_List_And_Pagination, url)
	
	returnMode = 1
	getSeriesList(mostPop,url,returnMode)

def CARTOON_LIST(url=''):
	# Hardcoded to use animeflavor.com
	# MODE 9 = CARTOON_LIST
	
	# content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	
	if url == '':
		url = 'http://www.animeflavor.com/index.php?q=cartoons'
	# mostPop = cache.cacheFunction(animeflavor.Video_List_And_Pagination, url)
	mostPop = animeflavor.Video_List_And_Pagination(url)
	returnMode = 1
	
	# name = ''
	# url = ''
	# mode = 2
	# iconimage = ''
	
	# mostPop.sort(key=lambda name: name[1]) 
	# mostPop = f2(mostPop)
	
	# dirLength = len(mostPop)
	# print base_txt + '# of items: ' + str(dirLength)
	
	# for iconimage, name in mostPop:
		# print base_txt + iconimage + ' ' + name
		# searchText = name
		# if searchText == '-- NEXT PAGE --':
			# mode = 1
			# url = iconimage
			# iconimage = ''
		# addDir(searchText,url,mode,iconimage,numItems=dirLength)
	getSeriesList(mostPop,url,returnMode)

def MOST_RECENT(url=''):
	# Hardcoded to use animecrazy.net
	# MODE 8 = MOST_RECENT
	
	# content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	
	if url == '':
		url = 'http://www.animecrazy.net/most-recent/'
	# mostRecent = animecrazy.Video_List_And_Pagination(url)
	mostRecent = cache.cacheFunction(animecrazy.Video_List_And_Pagination, url)
	returnMode = 8
	
	# dirLength = len(mostRecent)
	# print base_txt + url
	# print base_txt + '# of items: ' + str(dirLength)
	
	# name = ''
	# url = ''
	# mode = 2
	# iconimage = ''	
	# for iconimage, name in mostRecent:
		# searchText = cleanSearchText(name)
		# print base_txt + iconimage + ' ' + searchText
		
		# fanart = ''
		# tvdbid = 0
		# description = ''
		# year = 1902
		# genre ='Animation'
		
		# aid = get_ani_aid(searchText)
		# if not aid.isdigit:
			# aid = '0'
		# if (int(aid)>0 and len(uname)>0 and len(passwd)>0) :
			# linkAID = get_ani_detail(aid)
			# linkAID = cache.cacheFunction(get_ani_detail,aid)
			
			# ani_detail = anidbQuick.AID_Resolution(linkAID)
			# ani_detail = cache.cacheFunction(anidbQuick.AID_Resolution,linkAID)
		
			# iconimage = ani_detail[1]
			# description = ani_detail[2]
			# if len(ani_detail[3])>1:
				# year = int(ani_detail[3][0])
			# else:
				# year = 1901
			
			# if len(ani_detail[9])>0:
				# genre = " / ".join(ani_detail[9])
		
		# tvdbSer = get_tvdb_id(aid)[0]
		# if int(tvdbSer)>0:
			# linkTVDB = get_tvdb_detail(tvdbSer)
			# linkTVDB = cache.cacheFunction(get_tvdb_detail,tvdbSer)
			
			# tvdb_detail = anidbQuick.TVDBID_Resolution(aid,linkTVDB)
			# tvdb_detail = cache.cacheFunction(anidbQuick.TVDBID_Resolution,aid,linkTVDB)
			
			# tvdbid = tvdb_detail[1]
			# fanart = tvdb_detail[3]
			# iconimage = tvdb_detail[4]
		
		# if searchText == '-- NEXT PAGE --':
			# mode = 8
			# url = iconimage
			# iconimage = ''
		# print base_txt + searchText + ' (aid=' + aid + ', tvdbid='+ str(tvdbSer) +')'
		# addDir(searchText,url,mode,iconimage,numItems=dirLength,aid=aid,descr=description,yr=year,genre=genre,fanart=fanart)
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
	
	azList = cache.cacheFunction(animecrazy.Video_List_And_Pagination, url)	
	returnMode = 61
	
	# dirLength = len(azList)
	# print base_txt + url
	# print base_txt + '# of items: ' + str(dirLength)
	
	# name = ''
	# url = ''
	# mode = 2
	# iconimage = ''
	
	# for iconimage, name in azList:
		# searchText = cleanSearchText(name)
		# print base_txt + iconimage + ' ' + searchText
		
		# fanart = ''
		# tvdbid = 0
		# description = ''
		# year = 1902
		# genre ='Animation'
		
		# aid = get_ani_aid(searchText)
		# if not aid.isdigit:
			# aid = '0'
		# if int(aid)>0:
			
			# if (len(uname)>0 and len(passwd)>0) :
				# linkAID = get_ani_detail(aid)
				# linkAID = cache.cacheFunction(get_ani_detail,aid)
				
				# ani_detail = anidbQuick.AID_Resolution(linkAID)
				# ani_detail = cache.cacheFunction(anidbQuick.AID_Resolution,linkAID)
			
				# iconimage = ani_detail[1]
				# description = ani_detail[2]
				# year = int(ani_detail[3][0])
					
				# if len(ani_detail[9])>0:
					# genre = " / ".join(ani_detail[9])
			
			# tvdbSer = get_tvdb_id(aid)[0]
			# if int(tvdbSer)>0:
				# linkTVDB = get_tvdb_detail(tvdbSer)
				# linkTVDB = cache.cacheFunction(get_tvdb_detail,tvdbSer)
				
				# tvdb_detail = anidbQuick.TVDBID_Resolution(aid,linkTVDB)
				# tvdb_detail = cache.cacheFunction(anidbQuick.TVDBID_Resolution,aid,linkTVDB)
				
				# tvdbid = tvdb_detail[1]
				# fanart = tvdb_detail[3]
				# iconimage = tvdb_detail[4]
		
		# if searchText == '-- NEXT PAGE --':
			# mode = 61
			# url = iconimage
			# iconimage = ''
		# addDir(searchText,url,mode,iconimage,numItems=dirLength,aid=aid,descr=description,yr=year,genre=genre,fanart=fanart)
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
	searchText = cleanSearchText(searchText)
	print base_txt + 'Searching for ... ' + searchText
	
	# searchRes = allSearchList(searchText)
	searchRes = cache.cacheFunction(allSearchList,searchText)
	
	if (len(uname)>0 and len(passwd)>0) :
		# linkAID = get_ani_detail(aid_org)
		linkAID = cache.cacheFunction(get_ani_detail,aid)
		
		# ani_detail_org = anidbQuick.AID_Resolution(linkAID)
		ani_detail_org = cache.cacheFunction(anidbQuick.AID_Resolution,linkAID)
		if not aid.isdigit:
			aidDB = '0'
		else:
			aidDB = aid
		if (int(aidDB)>0 and len(ani_detail_org[7])>0):
			print base_txt + 'Searching ' + str(len(ani_detail_org[7])) + ' alternate names'
			for aidAlt, name in ani_detail_org[7]:
				subLoc = name.find('(')
				if subLoc > 0:
					name = name[:subLoc]
				name = urllib.unquote(name).title()
				print base_txt + 'Searching for ... ' + name
				searchRes = searchRes + cache.cacheFunction(allSearchList,name)
				if name.find(':') > 0:
					print base_txt + 'Searching for ... ' + name.replace(':',' ')
					searchRes = searchRes + cache.cacheFunction(allSearchList,name.replace(':',' '))
					print base_txt + 'Searching for ... ' + name.replace(':','')
					searchRes = searchRes + cache.cacheFunction(allSearchList,name.replace(':',''))
				if name.find('\'') > 0 or name.find('`') > 0:
					print base_txt + 'Searching for ... ' + name.replace('\'','').replace('`','').replace(':',' ').title()
					searchRes = searchRes + cache.cacheFunction(allSearchList,name.replace('\'','').replace('`','').replace(':',' ').title())
				if name.find('?') > 0 or name.find('!') > 0:
					print base_txt + 'Searching for ... ' + name.replace('?','').replace('!','')
					searchRes = searchRes + cache.cacheFunction(allSearchList,name.replace('?','').replace('!',''))
				if name.find('-') > 0:
					print base_txt + 'Searching for ... ' + name.replace('-',' ')
					searchRes = searchRes + cache.cacheFunction(allSearchList,name.replace('-',' '))
				if name.find('~') > 0:
					print base_txt + 'Searching for ... ' + name.replace('~','')
					searchRes = searchRes + cache.cacheFunction(allSearchList,name.replace('~',''))
				if name.startswith('The'):
					print base_txt + 'Searching for ... ' + name.replace('The ','')
					searchRes = searchRes + cache.cacheFunction(allSearchList,name.replace('The ',''))
				if name.find('.') > 0 or name.find(',') > 0:
					print base_txt + 'Searching for ... ' + name.replace('.','').replace(',','')
					searchRes = searchRes + cache.cacheFunction(allSearchList,name.replace('.','').replace(',',''))
					print base_txt + 'Searching for ... ' + name.replace(',','')
					searchRes = searchRes + cache.cacheFunction(allSearchList,name.replace(',',''))
					print base_txt + 'Searching for ... ' + name.replace('.','')
					searchRes = searchRes + cache.cacheFunction(allSearchList,name.replace('.',''))
		
	searchRes.append(['','zzzzzzEND'])
	
	tempsearchRes = searchRes
	searchRes = []
	for url, name in tempsearchRes:
		name = name.title().replace(' - ',' ').replace(':',' ').replace('2Nd','2').strip()
		if 'Movies' in name:
			name = name.replace(' Movies','').strip() + ' (Movies)'
		elif 'The Movie' in name:
			name = name.replace(' The Movie','').replace(' Movie','').strip() + ' (Movie)'
		elif 'Movie' in name:
			name = name.replace(' Movie','').replace(' Movie','').strip() + ' (Movie)'
		
		if 'movie' in url:
			name = name.strip() + ' (Movie)'
			
		if 'Ova' in name:
			name = name.replace(' Ova','').strip() + ' (OVA)'
		if 'Oav' in name:
			name = name.replace(' Oav','').strip() + ' (OVA)'
		if 'Featurettes' in name:
			name = name.replace(' Featurettes','').strip() + ' (OVA)'
		if 'ova' in url:
			name = name.strip() + ' (OVA)'
			
		if 'Tv Special' in name:
			name = name.replace(' Tv Special','').strip() + ' (OVA)'
			
		if ' Special ' in name:
			name = name.replace(' Special ','').strip() + ' (OVA)'
		
		name = name.replace('(Movie) (Movie)','(Movie)')
		name = name.replace('(Movies) (Movie)','(Movie)')
		name = name.replace('2 (Movie)','(Movie)')
		name = name.replace('(Oav)','(OVA)')
		name = name.replace('(Ova)','(OVA)')
		name = name.replace('(Movie) (OVA)','(OVA)')
		name = name.replace('(OVA) (Movie)','(OVA)')
		name = name.replace('(Ova) (Ova)','(OVA)')
		name = name.replace('(OVA) (OVA)','(OVA)').replace('(OVA) (OVA)','(OVA)')
		name = name.replace('2Nd Season','2')
		name = name.replace('Second Season','2')
		name = name.replace('Iii','3')
		name = name.replace(' Season','')
		name = name.replace(' Vs.',' Vs')
		# name = name.replace('Shippuden','Shippuuden')
		# name = name.replace('Shipuden','Shippuuden')
		# name = name.replace('Shipuuden','Shippuuden')
		name = name.replace('Dragonball','Dragon Ball')
		name = name.replace('Diamonddust','Diamond Dust')
		name = name.replace('Highschool','High School')
		# name = name.replace('Find',' Find')
		# name = name.replace('Finally',' Finally')
		name = name.replace('&#039;',"'")
		name = name.replace('&#8217;',"'")
		name = name.replace('&#8211;',' ')
		name = name.replace("'",'')
		name = name.replace('`','')
		name = name.replace('~','')
		name = name.replace('^','')
		name = name.replace('!','')
		name = name.replace(',','')
		name = name.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ')
		searchRes.append([url,name])
		
	searchRes.sort(key=lambda name: name[1]) 
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
	
	dirLength = len(searchRes)
	print base_txt + '# of items: ' + str(dirLength)
	for url, name in searchRes:
		# name = name.title().replace(' - ',' ').replace(':',' ').strip()
		# if 'Movies' in name:
			# name = name.replace(' Movies','').strip() + ' (Movies)'
		# elif 'The Movie' in name:
			# name = name.replace(' The Movie','').replace(' Movie','').strip() + ' (Movie)'
		# elif 'Movie' in name:
			# name = name.replace(' Movie','').replace(' Movie','').strip() + ' (Movie)'
		
		# try:
		if not nameTest == name:
			if not nameTest == '':
				aidSer = get_ani_aid(nameTest)
				iconimage = ''
				fanart = ''
				genre ='Animation'
				# print base_txt + str(aidSer)
					
				tvdbSer = get_tvdb_id(aidSer)[0]
				if int(tvdbSer)>0:
					# linkTVDB = get_tvdb_detail(tvdbSer)
					linkTVDB = cache.cacheFunction(get_tvdb_detail,tvdbSer)
					
					tvdb_detail = anidbQuick.TVDBID_Resolution(aidSer,linkTVDB)
					# tvdb_detail = cache.cacheFunction(anidbQuick.TVDBID_Resolution,aidSer,linkTVDB)
					
					fanart = tvdb_detail[3]
					if not int(aidDB)>0:
						iconimage = tvdb_detail[4]
						description = tvdb_detail[6]
						if len(tvdb_detail[7])>1:
							year = int(tvdb_detail[7][0])
						else:
							year = 1903
						if len(tvdb_detail[8])>0:
							genre = " / ".join(tvdb_detail[8])
				
				
				if not aidSer.isdigit:
					aidDB = '0'
				else:
					aidDB = aidSer
				if  int(aidDB)>0 and len(uname)>0 and len(passwd)>0:
					epwatch = '0'
					for aidWish, nameWish, epsWish in watchListTotal:
						if int(aidDB) == int(aidWish):
							epwatch = str(epsWish[0])
							break
				
					# linkAID = get_ani_detail(aidDB)
					linkAID = cache.cacheFunction(get_ani_detail,aidDB)
					
					# ani_detail = anidbQuick.AID_Resolution(linkAID)
					ani_detail = cache.cacheFunction(anidbQuick.AID_Resolution,linkAID)
					
					iconimage = ani_detail[1]
					description = ani_detail[2]
					if len(ani_detail[3])>1:
						year = int(ani_detail[3][0])
					else:
						year = 1900
					
					eptot = str(ani_detail[4])
					
					if len(ani_detail[9])>0:
						genre = " / ".join(ani_detail[9])
		
					if epwatch==eptot:
						playcount = 1
					else:
						playcount = 0
						
					if fanart=='':
						fanart=iconimage
					
					if int(epwatch)>0:
						print base_txt + nameTest + ' [' + epwatch + ' of ' + eptot + '] (aid=' + aidSer + ', tvdbid='+ str(tvdbSer) +') <--> ' + groupUrl
						nameTest = nameTest + ' [' + epwatch + ' of ' + eptot + ']'
					else:
						print base_txt + nameTest + ' (aid=' + aidSer + ', tvdbid='+ str(tvdbSer) +') <--> ' + groupUrl
						
					addDir(nameTest,groupUrl,mode,iconimage,numItems=dirLength,aid=aidSer,descr=description,yr=year,genre=genre,totep=eptot, watchep=epwatch, fanart=fanart, plycnt=playcount)
				else:
					print base_txt + nameTest + ' (aid=' + aidSer + ', tvdbid='+ str(tvdbSer) +') <--> ' + groupUrl
					addDir(nameTest,groupUrl,mode,iconimage,numItems=dirLength,aid=aidSer,genre=genre,fanart=fanart)
			groupUrl = ''
			nameTest = name
		
		if nameTest == name:
			groupUrl = groupUrl +' <--> '+ url
				
		# except:
			# print base_txt + 'Directory not created in SEARCH() for ' + url + ' ' + name	

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
		if not aid.isdigit:
			aid = '0'
		if (int(aid)>0):
			addDir('-- SIMILAR TITLES --','',121,'',aid=aid)

def cleanSearchText(searchText):
	# cleans up the text for easier searching
	subLoc = searchText.find('[')
	if subLoc > 0:
		searchText = searchText[:subLoc]
	subLoc = searchText.find('(')
	if subLoc > 0:
		searchText = searchText[:subLoc]
		
	searchText = searchText.replace('(TV)','').replace('(OVA)','').replace('(Movie)','').title().strip()
	# searchText = searchText.replace(':',' ').replace('-',' ').replace('_',' ').strip()
	
	return searchText

def get_ani_detail(aid):
	linkAID = ' '
	if not aid.isdigit:
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
		linkAID = linkAID + grabUrlSource(url)
	
	aid = '0'
	
	aidList = get_ani_aid_list(linkAID)
	# aidList = cache.cacheFunction(get_ani_aid_list,linkAID)

	searchText = cleanSearchText(searchText.replace(':',' ').replace('!',' ').replace('-',' ').replace('_',' ').replace('  ',' ').title().strip())
	print base_txt + 'Searching for aid: ' + searchText
	
	for aidFound, name, tvdbid, season in  aidList:
		name = cleanSearchText(name.replace(':',' ').replace('!',' ').replace('-',' ').replace('_',' ').replace('  ',' ').title().strip())
		if name == searchText:
			return str(aidFound)
	
	return aid
		
def get_tvdb_id(aid):

	groupUrl = []
	groupUrl.append('https://sites.google.com/site/anidblist/anime-list.xml?attredirects=0')
	groupUrl.append('https://raw.github.com/torenado/plugin.video.animestream/master/anime-list_modded.xml')
	
	linkAID = ''
	for url in groupUrl:
		linkAID = linkAID + grabUrlSource(url)
	
	tvdbid = ['0','']
	
	aidList = get_ani_aid_list(linkAID)
	# aidList = cache.cacheFunction(get_ani_aid_list,linkAID)
	
	for aidFound, name, tvdbidFound, season in  aidList:
		if tvdbidFound.isdigit() and int(aidFound) == int(aid):
			return [tvdbidFound,season]
	
	return tvdbid

def get_ani_aid_list(linkAID):

	# linkAID = linkAID.replace('> <','><').replace('>  <','><').replace('>   <','><').replace('>    <','><').replace('>     <','><')
	linkAID = linkAID.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('> <','><')
	match=re.compile('<anime (.+?)</anime>').findall(linkAID)
	aniInfo = []
	aid = ''
	name = ''
	tvdbid = ''
	season=''
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
		season=''
		
	aniInfo.sort(key=lambda aid: aid[0]) 
	return aniInfo

def get_aniDB_list(url=''):	
	
	if url == '':
		url = 'http://anidb.net/perl-bin/animedb.pl?show=mywishlist&uid=%(un)s&pass=%(pass)s' % {"un": unid, "pass": pubpass}
	
	multiPg = []	
	for pg in xrange(0,10):
		time.sleep(5)
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
	watchWishlist.sort(key=lambda name: name[1]) 
	
	return watchWishlist
	
def get_aniDB_mysummarylist(url=''):	
	
	if url == '':
		url = 'http://api.anidb.net:9001/httpapi?client=xbmcscrap&clientver=1&protover=1&request=mylistsummary&user=%(un)s&pass=%(pass)s' % {"un": uname, "pass": passwd}
	
	link = grabUrlSource(url)
		
	watchMylistSummary = anidbQuick.MyListSummaryAPI(link)	
	watchMylistSummary.sort(key=lambda name: name[1]) 
	
	return watchMylistSummary

def getSeriesList(mostPop,url,returnMode):

	dirLength = len(mostPop)
	print base_txt + url
	print base_txt + '# of items: ' + str(dirLength)
	
	name = ''
	url = ''
	iconimage = ''
	mode = 2
	for iconimage, name in mostPop:
		searchText = cleanSearchText(name)
		# print base_txt + iconimage + ' ' + searchText
		
		fanart = ''
		tvdbid = 0
		description = ''
		year = 1902
		genre ='Animation'
		epwatch = '0'
		
		aid = get_ani_aid(searchText)
		if not aid.isdigit:
			aidDB = '0'
		else:
			aidDB = aid
		
		tvdbSer = get_tvdb_id(aid)[0]
		if int(tvdbSer)>0:
			# linkTVDB = get_tvdb_detail(tvdbSer)
			linkTVDB = cache.cacheFunction(get_tvdb_detail,tvdbSer)
			
			tvdb_detail = anidbQuick.TVDBID_Resolution(aid,linkTVDB)
			# tvdb_detail = cache.cacheFunction(anidbQuick.TVDBID_Resolution,aid,linkTVDB)
			
			tvdbid = tvdb_detail[1]
			fanart = tvdb_detail[3]
			if not int(aidDB)>0:
				iconimage = tvdb_detail[4]
				description = tvdb_detail[6]
				if len(tvdb_detail[7])>1:
					year = int(tvdb_detail[7][0])
				else:
					year = 1903			
				if len(tvdb_detail[8])>0:
					genre = " / ".join(tvdb_detail[8])
		
		
		if (int(aidDB)>0 and len(uname)>0 and len(passwd)>0) :
			for aidWish, nameWish, epsWish in watchListTotal:
				if int(aidDB) == int(aidWish):
					epwatch = str(epsWish[0])
					break
					
			# linkAID = get_ani_detail(aidDB)
			linkAID = cache.cacheFunction(get_ani_detail,aidDB)
			
			# ani_detail = anidbQuick.AID_Resolution(linkAID)
			ani_detail = cache.cacheFunction(anidbQuick.AID_Resolution,linkAID)
		
			iconimage = ani_detail[1]
			description = ani_detail[2]
			if len(ani_detail[3])>1:
				year = int(ani_detail[3][0])
			else:
				year = 1904
					
			eptot = str(ani_detail[4])
				
			if len(ani_detail[9])>0:
				genre = " / ".join(ani_detail[9])
		
			if epwatch==eptot:
				playcount = 1
			else:
				playcount = 0
				
			if fanart=='':
				fanart=iconimage
		
		if searchText == '-- NEXT PAGE --':
			mode = returnMode
			url = iconimage
			iconimage = ''
		
		if int(epwatch)>0:
			print base_txt + searchText + ' [' + epwatch + ' of ' + eptot + '] (aid=' + aid + ', tvdbid='+ str(tvdbSer) +')'
			searchText = searchText + ' [' + epwatch + ' of ' + eptot + ']'
			addDir(searchText,url,mode,iconimage,numItems=dirLength,aid=aid,descr=description,yr=year,genre=genre,totep=eptot, watchep=epwatch, fanart=fanart, plycnt=playcount)
		else:
			print base_txt + searchText + ' (aid=' + aid + ', tvdbid='+ str(tvdbSer) +')'
			addDir(searchText,url,mode,iconimage,numItems=dirLength,aid=aid,descr=description,yr=year,genre=genre,fanart=fanart)
	
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
	if not aid.isdigit:
		aidDB = '0'
	else:
		aidDB = aid
	
	if (int(aidDB)>0 and len(uname)>0 and len(passwd)>0) :
		for aidWish, nameWish, epsWish in watchListTotal:
			if int(aidDB) == int(aidWish):
				epWishWatch = int(epsWish[0])
				break
		
		# linkAID = get_ani_detail(aid_org)
		linkAID = cache.cacheFunction(get_ani_detail,aidDB)
		
		# ani_detail = anidbQuick.AID_Resolution(linkAID)
		ani_detail = cache.cacheFunction(anidbQuick.AID_Resolution,linkAID)
		
		iconimageSeries = ani_detail[1]
		description = ani_detail[2]
		if len(ani_detail[3])>1:
			year = int(ani_detail[3][0])
		else:
			year = 1900
		eptot = ani_detail[4]
		epDetail = ani_detail[8]
	
	
	(tvdbSer,tvdbSeason) = get_tvdb_id(aid)
	if int(tvdbSer)>0:
		print base_txt + 'TheTVDB Season ' + tvdbSeason
		# linkTVDB = get_tvdb_detail(tvdbSer)
		linkTVDB = cache.cacheFunction(get_tvdb_detail,tvdbSer)
		
		tvdb_detail = anidbQuick.TVDBID_Resolution(aid,linkTVDB)
		# tvdb_detail = cache.cacheFunction(anidbQuick.TVDBID_Resolution,aid,linkTVDB)
		
		if len(tvdb_detail[3])>0:
			iconimageSeries = tvdb_detail[3]
		
		epTvDetail = []
		for epNum,epName,iconimage,description,seasonNum in tvdb_detail[5]:
			if tvdbSeason==seasonNum:
				epTvDetail.append([epNum,epName,iconimage,description, seasonNum])
	

	try:
		urls = groupUrl.split(' <--> ')
	except:
		urls = groupUrl
		
	epListAll = []
	epList = []
	
	for url in urls:
		if (anime44.base_url_name in url):
			# epList = anime44.Episode_Listing_Pages(url)
			epList = cache.cacheFunction(anime44.Episode_Listing_Pages, url)
		elif (animecrazy.base_url_name in url):
			# epList = animecrazy.Episode_Listing_Pages(url)
			epList = cache.cacheFunction(animecrazy.Episode_Listing_Pages, url)
		elif (animeflavor.base_url_name in url):
			epList = cache.cacheFunction(animeflavor.Episode_Listing_Pages, url)
		elif (animefushigi.base_url_name in url):
			# epList = animefushigi.Episode_Listing_Pages(url)
			epList = cache.cacheFunction(animefushigi.Episode_Listing_Pages, url)
		elif (animetip.base_url_name in url):
			epList = cache.cacheFunction(animetip.Episode_Listing_Pages, url)
		elif (myanimelinks.base_url_name in url):
			epList = cache.cacheFunction(myanimelinks.Episode_Listing_Pages, url)
		
		epListAll = epListAll + epList
		
	epListAllClean = []
	for episodePageLink, episodePageName, episodeMediaThumb, epNum in epListAll:		
		episodePageName = episodePageName.title().replace(' Episode','').replace('#','').replace(' - ',' ').replace(':',' ').replace('-',' ').strip()
		epListAllClean.append([episodePageLink, episodePageName, '', epNum])
	
	epListAll = epListAllClean
	epListAll.sort(key=lambda name: name[3], reverse=True) 
	epListAll = f2(epListAll)
	epListAll.append(['','END','',''])

	# print epListAll
	
	dirLength = len(epListAll)
	print base_txt + '# of items: ' + str(dirLength)
	if not aid.isdigit:
		aidDB = '0'
	else:
		aidDB = aid
	if int(aidDB)>0 and len(uname)>0 and len(passwd)>0:
		print base_txt + 'WATCHED ' + epsWish[0] + ' of ' + epsWish[1]
	else:		
		print base_txt 
	
	epNumTest = ''
	name = ''
	url = ''
	mode = 4
	iconimage = ''
	for url, name, iconimage, epNum in epListAll:
		name = name.title().replace('Episode','').replace('#','').replace(':',' ').replace('  ',' ').strip()
		# try:
		if not epNumTest == epNum:
			if not epNumTest == '':
				if int(epWishWatch) >= int(epNumTest):
					playcount = 1
					print base_txt + nameTest + ' - Season:' + seasonNum + ' [WATCHED] ' + groupUrl
				else:
					print base_txt + nameTest + ' - Season:' + seasonNum + groupUrl
					nameTest = '[B]' + nameTest + '[/B]'
					
				addDir(nameTest,groupUrl,mode,iconimageTest,numItems=dirLength,descr=description,yr=yr,mo=mo,day=day,epNum=epNumTest,fanart=fanart,plycnt=playcount)
			groupUrl = ''
			iconimageTest = ''
			description = ''
			seasonNum = ''
			fanart = iconimageSeries
			epNumTest = epNum
			nameTest = name
			playcount = 0
			yr = 1900
			mo = 01
			day = 02
			if not aid.isdigit:
				aidDB = '0'
			else:
				aidDB = aid
			if int(aidDB)>0 and len(uname)>0 and len(passwd)>0:
				for epNum1,epName,epAirdate in epDetail:
					if epNum==epNum1:
						nameTest = str(epNum1) + ' - ' + epName
						yr = epAirdate[0]
						mo = epAirdate[1]
						day = epAirdate[2]
						break
						
			if int(tvdbSer)>0:
				for epNum2,epName2,epIconimage,description,seasonNum in epTvDetail:
					if epNum==epNum2:
						if len(epIconimage)>0:
							iconimageTest = epIconimage
						break
		
		if epNumTest == epNum:
			try:
				groupUrl = groupUrl +' <--> '+ url
			except:
				groupUrl = groupUrl
				print base_txt + 'URL not added in SEARCH() for ' + url + ' ' + str(epNum)
				
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
	for url in urls:
		print base_txt + url
		if (anime44.base_url_name in url):
			epMedia = cache.cacheFunction(anime44.Episode_Page, url)
		elif (animecrazy.base_url_name in url):
			epMedia = cache.cacheFunction(animecrazy.Episode_Page, url)
		elif (animeflavor.base_url_name in url):
			# epMedia = animeflavor.Episode_Page(url)
			epMedia = cache.cacheFunction(animeflavor.Episode_Page, url)
		elif (animefushigi.base_url_name in url):
			# epMedia = animefushigi.Episode_Page(url)
			epMedia = cache.cacheFunction(animefushigi.Episode_Page, url)
		elif (animetip.base_url_name in url):
			epMedia = cache.cacheFunction(animetip.Episode_Page, url)
		elif (myanimelinks.base_url_name in url):
			epMedia = cache.cacheFunction(myanimelinks.Episode_Page, url)
		
		epMediaAll = epMediaAll + epMedia
		
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
			name = name + siteNname + ' -- Mirror ' + str(mirror) + ' - Part ' + str(part) + ' of ' + str(totParts) + ' (' + url.split('/')[2] + ') -- X'	
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

def allAnimeList():
	# Searches the various websites for the searched content
	
	searchSiteList = []
	if (dc.getSetting('anime44_on') == 'true'):
		searchSiteList.append(anime44.base_url_name)
		
	if (dc.getSetting('animecrazy_on') == 'true'):
		searchSiteList.append(animecrazy.base_url_name)
	
	if (dc.getSetting('animeflavor_on') == 'true'):
		searchSiteList.append(animeflavor.base_url_name)
	
	if (dc.getSetting('animefushigi_on') == 'true'):
		searchSiteList.append(animefushigi.base_url_name)
	
	if (dc.getSetting('animetip_on') == 'true'):
		searchSiteList.append(animetip.base_url_name)
	
	if (dc.getSetting('myanimelinks_on') == 'true'):
		searchSiteList.append(myanimelinks.base_url_name)
		
	if(len(searchSiteList) < 1):
		searchSiteList = ['animecrazy.net']
		print base_txt +  'No sites choosen in the settings.  Using animecrazy.net'
		
	
	searchRes = []
	for url in searchSiteList:
		xbmc.executebuiltin('XBMC.Notification(Retrieving Info!,'+ url +',5000)')
		link = ''
		if (anime44.base_url_name in url):
			try:
				# aniUrls = ['http://www.anime44.com/anime-list','http://www.anime44.com/category/anime-movies']
				for aniUrl in anime44.aniUrls:
					print base_txt + aniUrl
					link = grabUrlSource(aniUrl)
					searchRes = searchRes + anime44.Total_Video_List(link)
			except:
				print base_txt + url + ' failed to load allAnimeList()'
		elif (animecrazy.base_url_name in url):
			try:
				# aniUrls = ['http://www.animecrazy.net/anime-index/']
				for aniUrl in animecrazy.aniUrls:
					print base_txt + aniUrl
					link = grabUrlSource(aniUrl)
					searchRes = searchRes + animecrazy.Total_Video_List(link)
			except:
				print base_txt + url + ' failed to load allAnimeList()'
		elif (animeflavor.base_url_name in url):
			try:
				# aniUrls = ['http://www.animeflavor.com/index.php?q=node/anime_list','http://www.animeflavor.com/index.php?q=anime_movies','http://www.animeflavor.com/index.php?q=cartoons']
				for aniUrl in animeflavor.aniUrls:
					print base_txt + aniUrl
					link = grabUrlSource(aniUrl)
					searchRes = searchRes + animeflavor.Total_Video_List(link)
			except:
				print base_txt + url + ' failed to load allAnimeList()'
		elif (animefushigi.base_url_name in url):
			try:
				# aniUrls = ['http://www.animefushigi.com/full-anime-list/','http://www.animefushigi.com/anime/movies/']
				for aniUrl in animefushigi.aniUrls:
					print base_txt + aniUrl
					link = grabUrlSource(aniUrl)
					searchRes = searchRes + animefushigi.Total_Video_List(link)
			except:
				print base_txt + url + ' failed to load allAnimeList()'
		elif (animetip.base_url_name in url):
			try:
				# aniUrls = ['http://www.animetip.com/watch-anime','http://www.animetip.com/anime-movies']
				for aniUrl in animetip.aniUrls:
					print base_txt + aniUrl
					link = grabUrlSource(aniUrl)
					searchRes = searchRes + animetip.Total_Video_List(link)
			except:
				print base_txt + url + ' failed to load allAnimeList()'
		elif (myanimelinks.base_url_name in url):
			try:
				# aniUrls = ['http://www.myanimelinks.com/full-anime-list/']
				for aniUrl in myanimelinks.aniUrls:
					print base_txt + aniUrl
					link = grabUrlSource(aniUrl)
					searchRes = searchRes + myanimelinks.Total_Video_List(link)
			except:
				print base_txt + url + ' failed to load allAnimeList()'
	
	searchRes = utils.U2A_List(searchRes)
	searchRes.sort(key=lambda name: name[1]) 
	searchRes = f2(searchRes)
			
	return searchRes
	
def allSearchList(searchText):
	
	searchText_mod1 = searchText + ' '
	searchText_mod2 = ' ' + searchText
	# searchRes = allAnimeList()
	searchRes = cache.cacheFunction(allAnimeList)
	# print searchRes
	searchResults = []
	for possLink in searchRes:
		
		if not possLink[1]==None and not possLink[1].startswith('<'):
			if len(searchText)==1:
				if searchText_mod1 in possLink[1]:
					searchResults.append(possLink)
					
				if searchText_mod2 in possLink[1]:
					searchResults.append(possLink)
			
			else:
				if searchText in possLink[1]:
					searchResults.append(possLink)
	
	return searchResults
	
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
	
def addDir(name,url,mode,iconimage,numItems=1,aid='0',descr='',yr='1900',genre='',totep='0',watchep='0',epNum=0, mo='01', day='01', fanart='', plycnt=0):
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
	liz.setInfo( type="Video", infoLabels={ "Title":name, "Plot":descr, "Year":yr, "Genre":genre,"Episode":epNum,"Aired":airdate,"PlayCount":plycnt,"Watched":watched} )
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
if (len(unid)>0 and len(pubpass)>0) :
	# watchWishlist = get_aniDB_list()
	watchWishlist = cache.cacheFunction(get_aniDB_list)
	watchListTotal = f2(watchWishlist)

if (len(uname)>0 and len(passwd)>0) :
	# watchMylistSummary = get_aniDB_mysummarylist()
	watchMylistSummary = cache.cacheFunction(get_aniDB_mysummarylist)
	watchListTotal = f2(watchListTotal + watchMylistSummary)



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

xbmcplugin.endOfDirectory(int(sys.argv[1]))
