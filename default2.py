import urllib,urllib2,re,sys,httplib
#import xbmcplugin,xbmcgui,xbmcaddon,urlresolver
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json

sys.path.append("./sites")

import animecrazy
import animeflavor
import animefushigi
import animetip
import myanimelinks

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
# python -c "execfile('default2.py'); SEARCH('Fairy Tail')"
	
#animestream
# modded from --> <addon id="plugin.video.animecrazy" name="Anime Crazy" version="1.0.9" provider-name="AJ">
#dc=xbmcaddon.Addon(id='plugin.video.animestream')
addonPath=os.getcwd()
#artPath=addonPath+'/resources/art'
mozilla_user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
base_txt = 'animestream: '

def HOME():
	# XBMC: Default screen
	print base_txt + 'Create Home Screen'
	addDir('Most Popular','',1,'')
		
		
def getEpisode_Listing_Pages(url):
	# Extracts the URL and Page name of the various content pages
	if ('animecrazy.net' in url):
		print base_txt + ' 1'
		epList = animecrazy.Episode_Listing_Pages(url)
	elif ('animeflavor.com' in url):
		print base_txt + ' 2'
		epList = animeflavor.Episode_Listing_Pages(url)
	elif ('animefushigi.com' in url):
		print base_txt + ' 3'
		epList = animefushigi.Episode_Listing_Pages(url)
	elif ('animetip.com' in url):
		print base_txt + ' 4'
		epList = animetip.Episode_Listing_Pages(url)
	elif ('myanimelinks.com' in url):
		print base_txt + ' 5'
		epList = myanimelinks.Episode_Listing_Pages(url)
		
	name = ''
	url = ''
	mode = 4
	iconimage = ''
	for url, name, iconimage in epList:
		print base_txt + url + ' ' + name
		# addDir(name,url,mode,iconimage)
		
		
def getEpisode_Page(url):
	# Extracts the URL for the content media file
	if ('animecrazy.net' in url):
		print base_txt + ' 1'
		epMedia = animecrazy.Episode_Page(url)
	elif ('animeflavor.com' in url):
		print base_txt + ' 2'
		epMedia = animeflavor.Episode_Page(url)
	elif ('animefushigi.com' in url):
		print base_txt + ' 3'
		epMedia = animefushigi.Episode_Page(url)
	elif ('animetip.com' in url):
		print base_txt + ' 4'
		epMedia = animetip.Episode_Page(url)
	elif ('myanimelinks.com' in url):
		print base_txt + ' 5'
		epMedia = myanimelinks.Episode_Page(url)
		
	name = 'PLAY'
	url = ''
	mode = 5
	iconimage = ''
	mediaValid = []
	mediaInValid = []
	mediaList = mediaValid + mediaInValid
	print epMedia
	# for url in epMedia:
		# name = 'PLAY'
		
		# media_url = urlresolver.HostedMediaFile(url).resolve()
		# if media_url:
			# print base_txt + media_url
			# hostName = urlresolver.HostedMediaFile(url).get_host()
			# name = name + ' (' + hostName + ')'
			# mediaValid.append([name,media_url,iconimage])
		# else:
			# print base_txt + url + ' <-- DID NOT SUCCEED'
			# name = name + ' (' + url.split('/')[2] + ') -- X'			
			# mediaInValid.append([name,url,iconimage])
			
	# mediaList = mediaValid + mediaInValid
	# for name, media_url, iconimage in mediaList:
		# addLink(name,media_url,iconimage)


def MOST_POPULAR():
	# Hardcoded to use animecrazy.net
	url = 'http://www.animecrazy.net/most-popular/'
	mostPop = animecrazy.Video_List_And_Pagination(url)
	name = ''
	url = ''
	mode = 2
	iconimage = ''
	for iconimage, name in mostPop:
		print base_txt + iconimage + ' ' + name
		searchText = name.replace('(TV)','').strip()
		# addDir(searchText,url,mode,iconimage)
	
	
def SEARCH(searchText):
	# Searches the various websites for the searched content
	searchSiteList = ["animecrazy.net","animeflavor.com","animefushigi.com","animetip.com","myanimelinks.com"]
	print base_txt + searchText
	
	searchRes = []
	for url in searchSiteList:
		if ('animecrazy.net' in url):
			searchRes = searchRes + animecrazy.Video_List_Searched(searchText)
		elif ('animeflavor.com' in url):
			searchRes = searchRes + animeflavor.Video_List_Searched(searchText)
		elif ('animefushigi.com' in url):
			searchRes = searchRes + animefushigi.Video_List_Searched(searchText)
		elif ('animetip.com' in url):
			searchRes = searchRes + animetip.Video_List_Searched(searchText)
		elif ('myanimelinks.com' in url):
			searchRes = searchRes + myanimelinks.Video_List_Searched(searchText)
		
	name = ''
	url = ''
	mode = 3
	iconimage = ''
	searchRes.sort(key=lambda name: name[1]) 
	searchRes = f2(searchRes)
	for url, name in searchRes:
		name = name + ' (' + url.split('/')[2] + ')'
		print base_txt + url + ' ' + name
		# addDir(name,url,mode,iconimage)

def addDir(name,url,mode,iconimage):
	# XBMC: create directory
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
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
		
		
# def get_params():
        # param=[]
        # paramstring=sys.argv[2]
        # if len(paramstring)>=2:
                # params=sys.argv[2]
                # cleanedparams=params.replace('?','')
                # if (params[len(params)-1]=='/'):
                        # params=params[0:len(params)-2]
                # pairsofparams=cleanedparams.split('&')
                # param={}
                # for i in range(len(pairsofparams)):
                        # splitparams={}
                        # splitparams=pairsofparams[i].split('=')
                        # if (len(splitparams))==2:
                                # param[splitparams[0]]=splitparams[1]
                                
        # return param    

# params=get_params()
# url=None
# name=None
# mode=None

# try:
        # url=urllib.unquote_plus(params["url"])
# except:
        # pass
# try:
        # name=urllib.unquote_plus(params["name"])
# except:
        # pass
# try:
        # mode=int(params["mode"])
# except:
        # pass

                

# if mode==None:
        # HOME()

# elif mode==1:
        # MOST_POPULAR() 
        
# elif mode==2:
        # SEARCH(name) 
        
# elif mode==3:
        # getEpisode_Listing_Pages(url)
        
# elif mode==4:
        # getEpisode_Page(url)
        
# elif mode==5:
        # LOAD_AND_PLAY_VIDEO(url,name)

# xbmcplugin.endOfDirectory(int(sys.argv[1]))
