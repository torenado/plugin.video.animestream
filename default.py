import urllib,urllib2,re,sys,httplib
import xbmcplugin,xbmcgui,xbmcaddon,urlresolver
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json

sys.path.append("./sites")

import anidbQuick
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

def HOME():
	# XBMC: Default screen
	print base_txt + 'Create Home Screen'
	#addDir('aniDB Wishlist','',12,'')
	addDir('Most Popular','',1,'')
	addDir('Most Recent','',8,'')
	addDir('A-Z List','',6,'')
	addDir('Anime','',10,'')
	addDir('Cartoons','',11,'')
	addDir('Search','',7,'')

def ANIME():
	# XBMC: Anime screen
	print base_txt + 'Create Anime Screen'
	addDir('Most Popular','',1,'')
	addDir('Most Recent','',8,'')
	addDir('A-Z List','',6,'')
	addDir('Search','',7,'')

def CARTOON():
	# XBMC: Cartoon screen
	print base_txt + 'Create Cartoon Screen'
	addDir('Cartoons','',9,'')
	addDir('Search','',7,'')

def ANIDB_WISHLIST():
	# MODE 12 = ANIDB_WISHLIST

	url = 'http://anidb.net/perl-bin/animedb.pl?show=mywishlist&uid=%(uid)s&pass=%(pubpass)s' % {"uid": dc.getSetting('uid'), "pubpass": dc.getSetting('publicpass')}
	
	print base_txt + url
	link = cache.cacheFunction(grabUrlSource,url)
	# link = grabUrlSource(url)
	# watchWishlist = cache.cacheFunction(anidbQuick.Wishlist,link)
	watchWishlist = anidbQuick.Wishlist(link)
	
	name = ''
	url = ''
	mode = 2
	iconimage = ''
	for name,stat_seen,stat_eps,aid in watchWishlist:
		print base_txt + name + ' - Seen ' + stat_seen + ' of ' + stat_eps + ' ~ aid = ' + aid
		searchText = name
		if searchText == '-- NEXT PAGE --':
			mode = 1
			url = iconimage
			iconimage = ''
		addDir(searchText,url,mode,iconimage)
		
		
def getEpisode_Listing_Pages(groupUrl):
	# Extracts the URL and Page name of the various content pages
	# MODE 3 = getEpisode_Listing_Pages
	
	try:
		urls = groupUrl.split()
	except:
		urls = groupUrl
		
	epListAll = []
	for url in urls:
		if ('animecrazy.net' in url):
			# epList = animecrazy.Episode_Listing_Pages(url)
			epList = cache.cacheFunction(animecrazy.Episode_Listing_Pages, url)
		elif ('animeflavor.com' in url):
			epList = cache.cacheFunction(animeflavor.Episode_Listing_Pages, url)
		elif ('animefushigi.com' in url):
			# epList = animefushigi.Episode_Listing_Pages(url)
			epList = cache.cacheFunction(animefushigi.Episode_Listing_Pages, url)
		elif ('animetip.com' in url):
			epList = cache.cacheFunction(animetip.Episode_Listing_Pages, url)
		elif ('myanimelinks.com' in url):
			epList = cache.cacheFunction(myanimelinks.Episode_Listing_Pages, url)
		
		epListAll = epListAll + epList
	
	epListAll.sort(key=lambda name: name[3], reverse=True) 
	epListAll = f2(epListAll)
	epListAll.append(['','END','',''])
	
	epNumTest = ''
	name = ''
	url = ''
	mode = 4
	iconimage = ''
	for url, name, iconimage, epNum in epListAll:
		name = name.title().replace('Episode','').replace('#','').replace(':','').replace('  ',' ').strip()
		
		try:
			if not epNumTest == epNum:
				if not epNumTest == '':
					print base_txt + nameTest + ' ' + groupUrl
					addDir(nameTest,groupUrl,mode,iconimageTest)
				groupUrl = ''
				iconimageTest = ''
				nameTest = name
				epNumTest = epNum
			
			if epNumTest == epNum:
				groupUrl = groupUrl +' '+ url
				if 'myanimelinks.com' in iconimage:
					iconimageTest = iconimage
				
		except:
			print base_txt + 'Directory not created in SEARCH() for ' + url + ' ' + epNum		
		
		
def getEpisode_Page(groupUrl):
	# Extracts the URL for the content media file
	# MODE 4 = getEpisode_Page
	
	try:
		urls = groupUrl.split()
	except:
		urls = groupUrl
	
	urls = f2(urls)
	epMediaAll = []
	for url in urls:
		print base_txt + url
		if ('animecrazy.net' in url):
			epMedia = cache.cacheFunction(animecrazy.Episode_Page, url)
		elif ('animeflavor.com' in url):
			epMedia = cache.cacheFunction(animeflavor.Episode_Page, url)
		elif ('animefushigi.com' in url):
			# epMedia = animefushigi.Episode_Page(url)
			epMedia = cache.cacheFunction(animefushigi.Episode_Page, url)
		elif ('animetip.com' in url):
			epMedia = cache.cacheFunction(animetip.Episode_Page, url)
		elif ('myanimelinks.com' in url):
			epMedia = cache.cacheFunction(myanimelinks.Episode_Page, url)
		
		epMediaAll = epMediaAll + epMedia
		
	url = ''
	mode = 5
	iconimage = ''
	mediaValid = []
	mediaInValid = []
	mediaList = mediaValid + mediaInValid
	for siteNname, url, mirror, part in epMediaAll:
		name = ''
		# media_url = urlresolver.HostedMediaFile(url).resolve()
		try:
			media_url = urlresolver.HostedMediaFile(url).resolve()
		except:
			media_url = False
			
		if (media_url == False and url.endswith('.flv')):
			media_url = url
		
		print 'Mirror: ' + str(mirror) + ' Part: ' + str(part)
		if media_url:
			print base_txt + media_url
			hostName = urlresolver.HostedMediaFile(url).get_host()
			name = name + 'Mirror ' + str(mirror) + ' - Part ' + str(part) + ' (' + hostName + ') -- ' + siteNname
			mediaValid.append([name,media_url,iconimage])
		else:
			print base_txt + url + ' <-- VIDEO MAY NOT WORK'
			name = name + 'Mirror ' + str(mirror) + ' - Part ' + str(part) + ' (' + url.split('/')[2] + ') -- ' + siteNname +' -- X'		
			mediaInValid.append([name,url,iconimage])
			
	mediaList = mediaValid + mediaInValid
	for name, media_url, iconimage in mediaValid:
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
	
	try:
		urls = groupUrl.split()
	except:
		urls = groupUrl
	
	urls = f2(urls)
	epMediaAll = []
	for url in urls:
		print base_txt + url
		if ('animecrazy.net' in url):
			epMedia = cache.cacheFunction(animecrazy.Episode_Page, url)
		elif ('animeflavor.com' in url):
			epMedia = cache.cacheFunction(animeflavor.Episode_Page, url)
		elif ('animefushigi.com' in url):
			# epMedia = animefushigi.Episode_Page(url)
			epMedia = cache.cacheFunction(animefushigi.Episode_Page, url)
		elif ('animetip.com' in url):
			epMedia = cache.cacheFunction(animetip.Episode_Page, url)
		elif ('myanimelinks.com' in url):
			epMedia = cache.cacheFunction(myanimelinks.Episode_Page, url)
		
		epMediaAll = epMediaAll + epMedia
		
	url = ''
	mode = 5
	iconimage = ''
	mediaValid = []
	mediaInValid = []
	mediaList = mediaValid + mediaInValid
	for siteNname, url, mirror, part in epMediaAll:
		name = ''
		# media_url = urlresolver.HostedMediaFile(url).resolve()
		try:
			media_url = urlresolver.HostedMediaFile(url).resolve()
		except:
			media_url = False
			
		if (media_url == False and url.endswith('.flv')):
			media_url = url
		
		print 'Mirror: ' + str(mirror) + ' Part: ' + str(part)
		if media_url:
			print base_txt + media_url
			hostName = urlresolver.HostedMediaFile(url).get_host()
			name = name + 'Mirror ' + str(mirror) + ' - Part ' + str(part) + ' (' + hostName + ') -- ' + siteNname
			mediaValid.append([name,media_url,iconimage])
		else:
			print base_txt + url + ' <-- VIDEO MAY NOT WORK'
			name = name + 'Mirror ' + str(mirror) + ' - Part ' + str(part) + ' (' + url.split('/')[2] + ') -- ' + siteNname +' -- X'		
			mediaInValid.append([name,url,iconimage])
			
	for name, media_url, iconimage in mediaInValid:
		addLink(name,media_url,iconimage)

def MOST_POPULAR(url=''):
	# Hardcoded to use animecrazy.net
	# MODE 1 = MOST_POPULAR
	
	if url == '':
		url = 'http://www.animecrazy.net/most-popular/'
	# mostPop = animecrazy.Video_List_And_Pagination(url)
	mostPop = cache.cacheFunction(animecrazy.Video_List_And_Pagination, url)
	name = ''
	url = ''
	mode = 2
	iconimage = ''
	for iconimage, name in mostPop:
		print base_txt + iconimage + ' ' + name
		searchText = name
		if searchText == '-- NEXT PAGE --':
			mode = 1
			url = iconimage
			iconimage = ''
		addDir(searchText,url,mode,iconimage)


def CARTOON_LIST(url=''):
	# Hardcoded to use animeflavor.com
	# MODE 9 = CARTOON_LIST
	
	if url == '':
		url = 'http://www.animeflavor.com/index.php?q=cartoons'
	# mostPop = cache.cacheFunction(animeflavor.Video_List_And_Pagination, url)
	mostPop = animeflavor.Video_List_And_Pagination(url)
	name = ''
	url = ''
	mode = 2
	iconimage = ''
	
	mostPop.sort(key=lambda name: name[1]) 
	mostPop = f2(mostPop)
	for iconimage, name in mostPop:
		print base_txt + iconimage + ' ' + name
		searchText = name
		if searchText == '-- NEXT PAGE --':
			mode = 1
			url = iconimage
			iconimage = ''
		addDir(searchText,url,mode,iconimage)

def MOST_RECENT(url=''):
	# Hardcoded to use animecrazy.net
	# MODE 8 = MOST_RECENT
	
	if url == '':
		url = 'http://www.animecrazy.net/most-recent/'
	
	# mostRecent = animecrazy.Video_List_And_Pagination(url)
	mostRecent = cache.cacheFunction(animecrazy.Video_List_And_Pagination, url)
	name = ''
	url = ''
	mode = 2
	iconimage = ''
	for iconimage, name in mostRecent:
		print base_txt + iconimage + ' ' + name
		searchText = name
		if searchText == '-- NEXT PAGE --':
			mode = 8
			url = iconimage
			iconimage = ''
		addDir(searchText,url,mode,iconimage)
	
	
def A_Z_LIST():
	# Hardcoded to use animecrazy.net
	# MODE 6 = A_Z_LIST
	
	url = 'http://www.animecrazy.net/alpha-'
	abc = [chr(i) for i in xrange(ord('A'), ord('Z')+1)]
	
	for alphaB in abc:
		addDir(alphaB,url+alphaB.lower()+'/',61,'')
        

def A_Z_LIST_VIDEOS(url):
	# Hardcoded to use animecrazy.net
	# MODE 61 = A_Z_LIST_VIDEOS
	
	azList = cache.cacheFunction(animecrazy.Video_List_And_Pagination, url)
	name = ''
	url = ''
	mode = 2
	iconimage = ''
	for iconimage, name in azList:
		print base_txt + iconimage + ' ' + name
		searchText = name
		if searchText == '-- NEXT PAGE --':
			mode = 61
			url = iconimage
			iconimage = ''
		addDir(searchText,url,mode,iconimage)
		
def TYPED_SEARCH():
        keyb = xbmc.Keyboard('', 'Enter search text')
        keyb.doModal()
        searchText = ''
        if (keyb.isConfirmed()):
                searchText = urllib.quote_plus(keyb.getText())
		
		searchText = searchText.title()
        SEARCH(searchText)
		
		
def SEARCH(searchTextOrg):
	# Searches the various websites for the searched content
	
	searchText = searchTextOrg.replace('(TV)','').replace('(OVA)','').replace('(Movie)','').strip()
	print base_txt + 'Searching for ... ' + searchText
	
	searchRes = cache.cacheFunction(allSearch,searchText)
	searchRes.append(['','END'])
	
	nameTest = ''
	url = ''
	mode = 3
	iconimage = ''
	for url, name in searchRes:
		name = name.title().replace(' - ',' ').replace(':','')
		try:
			if not nameTest == name:
				if not nameTest == '':
					print base_txt + nameTest + ' ' + groupUrl
					addDir(nameTest,groupUrl,mode,iconimage)
				groupUrl = ''
				nameTest = name
			
			if nameTest == name:
				groupUrl = groupUrl +' '+ url
				
		except:
			print base_txt + 'Directory not created in SEARCH() for ' + url + ' ' + name		
		
		
def allSearch(searchText):
	# Searches the various websites for the searched content
	
	searchSiteList = []
	if (dc.getSetting('animecrazy_on') == 'true'):
		searchSiteList.append('animecrazy.net')
	
	if (dc.getSetting('animeflavor_on') == 'true'):
		searchSiteList.append('animeflavor.com')
	
	if (dc.getSetting('animefushigi_on') == 'true'):
		searchSiteList.append('animefushigi.com')
	
	if (dc.getSetting('animetip_on') == 'true'):
		searchSiteList.append('animetip.com')
	
	if (dc.getSetting('myanimelinks_on') == 'true'):
		searchSiteList.append('myanimelinks.com')
		
	if(len(searchSiteList) < 1):
		searchSiteList = ['animecrazy.net']
		print base_txt +  'No sites choosen in the settings.  Using animecrazy.net'
		
	
	searchRes = []
	for url in searchSiteList:
		link = ''
		if ('animecrazy.net' in url):
			try:
				aniUrls = ['http://www.animecrazy.net/anime-index/']
				for aniUrl in aniUrls:
					print base_txt + aniUrl
					link = cache.cacheFunction(grabUrlSource,aniUrl)
					searchRes = searchRes + animecrazy.Video_List_Searched(searchText, link)
			except:
				print base_txt + url + ' failed to load allSearch()'
		elif ('animeflavor.com' in url):
			try:
				aniUrls = ['http://www.animeflavor.com/index.php?q=node/anime_list','http://www.animeflavor.com/index.php?q=anime_movies','http://www.animeflavor.com/index.php?q=cartoons']
				for aniUrl in aniUrls:
					print base_txt + aniUrl
					link = cache.cacheFunction(grabUrlSource,aniUrl)
					searchRes = searchRes + animeflavor.Video_List_Searched(searchText, link)
			except:
				print base_txt + 'animeflavor.com failed to load allSearch()'
		elif ('animefushigi.com' in url):
			try:
				aniUrls = ['http://www.animefushigi.com/full-anime-list/','http://www.animefushigi.com/anime/movies/']
				for aniUrl in aniUrls:
					print base_txt + aniUrl
					link = cache.cacheFunction(grabUrlSource,aniUrl)
					searchRes = searchRes + animefushigi.Video_List_Searched(searchText, link)
			except:
				print base_txt + 'animefushigi.com failed to load allSearch()'
		elif ('animetip.com' in url):
			try:
				aniUrls = ['http://www.animetip.com/watch-anime','http://www.animetip.com/anime-movies']
				for aniUrl in aniUrls:
					print base_txt + aniUrl
					link = cache.cacheFunction(grabUrlSource,aniUrl)
					searchRes = searchRes + animetip.Video_List_Searched(searchText, link)
			except:
				print base_txt + 'animetip.com failed to load allSearch()'
		elif ('myanimelinks.com' in url):
			try:
				aniUrls = ['http://www.myanimelinks.com/full-anime-list/']
				for aniUrl in aniUrls:
					print base_txt + aniUrl
					link = cache.cacheFunction(grabUrlSource,aniUrl)
					searchRes = searchRes + myanimelinks.Video_List_Searched(searchText, link)
			except:
				print base_txt + 'myanimelinks.com failed to load allSearch()'
		
	searchRes.sort(key=lambda name: name[1]) 
	searchRes = f2(searchRes)
	
	return searchRes

	
def addDir(name,url,mode,iconimage,numItems=1):
	# XBMC: create directory
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
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
		
def f2(seq): 
   # order preserving uniqify --> http://www.peterbe.com/plog/uniqifiers-benchmark
   checked = []
   for e in seq:
       if e not in checked:
           checked.append(e)
   return checked	
   
   
def grabUrlSource(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', mozilla_user_agent)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	link = ''.join(link.splitlines()).replace('\t','')
	
	return link
		
		
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

                

if mode==None:
        HOME()

elif mode==10:
        ANIME() 

elif mode==11:
        CARTOON() 

elif mode==1:
        MOST_POPULAR(url) 
        
elif mode==2:
        SEARCH(name) 
        
elif mode==3:
        getEpisode_Listing_Pages(url)
        
elif mode==4:
        getEpisode_Page(url)
elif mode==41:
        getEpisode_Page_Fail(url)
        
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
        ANIDB_WISHLIST()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
