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
# python -c "execfile('animetip.py'); Episode_Listing_Pages('http://www.animetip.com/watch-anime/f/fairy-tail')"
#TEST2
# python -c "execfile('animetip.py'); Episode_Media_Link('http://www.animetip.com/watch-anime/f/fairy-tail/fairy-tail-episode-90.html')"
	
#animestream
# modded from --> <addon id="plugin.video.animecrazy" name="Anime Crazy" version="1.0.9" provider-name="AJ">
#dc=xbmcaddon.Addon(id='plugin.video.animestream')
addonPath=os.getcwd()
#artPath=addonPath+'/resources/art'

BASE_URL = 'http://anidb.net'

base_url_name = BASE_URL.split('//')[1]
base_txt = base_url_name + ': '
	
	
def Wishlist(link):
	# Grabs and parses the public wishlist from anidb.  User must set uid and password of the public wishlist in settings
	# ***WARNING: both this addon and anidb sends this password in the clear (plain text)
	print base_txt +  'Grabbing anidb public wishlist info'
	watchWishlist = []
		
	match=re.compile('<tr(.+?)</tr>').findall(link)[1:]
	if(len(match) >= 1):
		for aniLine in match:
			aid=re.compile('id="a(.+?)"').findall(link)
			name=re.compile('<label>(.+?)>(.+?)</a>').findall(link)[1]
			stat_eps=re.compile('"stats eps">(.+?)/(.+?)</').findall(link)[1]
			stat_seen=re.compile('"stats seen">(.+?)/(.+?)</').findall(link)[1]
			watchWishlist.append([name,stat_seen,stat_eps,aid])
	
	if(len(watchWishlist) < 1):
		print base_txt +  'Nothing was parsed from Wishlist: '
	
	return watchWishlist