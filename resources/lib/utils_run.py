import urllib,urllib2,re,sys,httplib, chardet
import gzip, io, htmlentitydefs, unicodedata, hashlib
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging
import xbmc,xbmcplugin,xbmcgui,xbmcaddon,urlresolver
from datetime import datetime
try:
	import json
except ImportError:
	import simplejson as json
import sqlite3 as sqlite

base_txt = 'animestream: '
plugin_name = "animestream"
dc=xbmcaddon.Addon(id='plugin.video.animestream')
import anidbQuick
from utils import *

monitor = xbmc.Monitor()

plug_path = xbmc.translatePath(dc.getAddonInfo("profile")).decode("utf-8")
user_path = os.path.join(plug_path, plugin_name+'.db')
# cache_path= os.path.join(plug_path, '../script.common.plugin.cache/commoncache.db')
cache_path= os.path.join(plug_path, '../../../temp/commoncache.db')
con_us = sqlite.connect(user_path)
con_cache = sqlite.connect(cache_path)

icon_sat_dish = 'f_001_53.png'

def remove_bad_substrings(s_list,badSubstrings):
	s_new = []
	try:
		# is badSubstrings is a single string turn it into a one entry list
		if isinstance(badSubstrings, basestring):
			badSubstrings = [badSubstrings]
	except:
		pass
	
	for s in s_list:
		for badSubstring in badSubstrings:
			s_new.append(s.replace(badSubstring, ''))
	return s_new
	
# streaming site plugin files
plugin_path = dc.getAddonInfo('path') + '/resources/lib/streamSites/'
files = os.listdir(plugin_path)
files = filter(lambda files: files[-3:] == ".py", files)
streamSiteList_full = remove_bad_substrings(files,'.py')
# streamSiteList_general = ['anilinkz',
				# 'anime44',
				# 'animecrazy',
				# 'animeflavor',
				# 'animefreak',
				# 'animefushigi',
				# 'animereboot',
				# 'animesubbed',
				# 'animetip',
				# 'animetoon',
				# 'lovemyanime',
				# 'myanimelinks',
				# 'tubeplus']
# streamSiteList_adult = ['hentaiseries',
				# 'hentaistream']
# streamSiteList_general.sort() 
streamSiteList_full.sort()

streamSiteList = []
	
for streamList in streamSiteList_full:
	siteOn = streamList + '_on'
	if (dc.getSetting(siteOn) == 'true'):
		streamSiteList.append(streamList)

for module in streamSiteList:
	vars()[module]=__import__(module)

try:
	import StorageServer
except:
	import storageserverdummy as StorageServer
	
cache = StorageServer.StorageServer(plugin_name, 24) # (Your plugin name, Cache time in hours)
cache7 = StorageServer.StorageServer(plugin_name, 24*7) # (Your plugin name, Cache time in hours)


# aniDB Public Wishlist
unid = dc.getSetting('uid')
pubpass = dc.getSetting('pubpass')

# aniDB Login
uname = dc.getSetting('username')
passwd = dc.getSetting('pass')


# check to see if urlresolver has the following plugins
plugin_add_path = dc.getAddonInfo('path') + '/resources/lib/urlresolver_additions/'
plugin_path = dc.getAddonInfo('path') + '/../script.module.urlresolver/lib/urlresolver/plugins/'

sys.path = [plugin_add_path, plugin_path] + sys.path

urlresolver_additions=['gogoanime.py',
						'auengine.py']
						
anime_list=['https://sites.google.com/site/anidblist/anime-list.xml?attredirects=0',
			'https://raw.github.com/torenado/plugin.video.animestream/master/anime-list_modded.xml']

for url_plugin in urlresolver_additions:
	path_add_lib = plugin_add_path + url_plugin
	path_lib = plugin_path + url_plugin
	if not os.path.exists(path_lib): # or os.path.getctime(path_lib) > os.path.getctime(path_add_lib):
			print base_txt +  path_add_lib
			print base_txt +  path_lib
			os.symlink(path_add_lib, path_lib)
			print base_txt + 'Symbolic link added: ' + path_lib
	
def f2(seq): 
	# order preserving uniqify --> http://www.peterbe.com/plog/uniqifiers-benchmark
	checked = []
	for e in seq:
		if e not in checked:
			checked.append(e)
	return checked	
			
def list_ord(txt):
	gg = []
	for v in txt:
		if ord(v)>128:
			gg.append([ord(v),v])
	gg.sort(key=lambda name: name[0])
	
	return f2(gg)

def list_ord_replace(txt):
	gg = []
	for v in txt:
		if ord(v)>128:
			gg.append(odd_decode(ord(v),v))
		else:
			gg.append(v)
	# print gg
	return ''.join(gg)	

def odd_decode(num,txt=''):

	htmlCodes = []
	for n in xrange(0,10):
		for i in xrange(128+n, 255, 16):
			htmlCodes.append([i,chr(i),'%'+str(0+n)])
			
	for code in htmlCodes:
		if int(code[0])==int(num):
			txt = code[2]
			return txt
	
	print 'odd_decode: NUM - ' + str(num) + ' not found'
	
chars = {
    '\xc2\x82' : ',',        # High code comma
    '\xc2\x84' : ',,',       # High code double comma
    '\xc2\x85' : '...',      # Tripple dot
    '\xc2\x88' : '^',        # High carat
    '\xc2\x91' : '\x27',     # Forward single quote
    '\xc2\x92' : '\x27',     # Reverse single quote
    '\xc2\x93' : '\x22',     # Forward double quote
    '\xc2\x94' : '\x22',     # Reverse double quote
    '\xc2\x95' : ' ',
    '\xc2\x96' : '-',        # High hyphen
    '\xc2\x97' : '--',       # Double hyphen
    '\xc2\x99' : ' ',
    '\xc2\xa0' : ' ',
    '\xc2\xa6' : '|',        # Split vertical bar
    '\xc2\xab' : '<<',       # Double less than
    '\xc2\xbb' : '>>',       # Double greater than
    '\xc2\xbc' : '1/4',      # one quarter
    '\xc2\xbd' : '1/2',      # one half
    '\xc2\xbe' : '3/4',      # three quarters
    '\xca\xbf' : '\x27',     # c-single quote
    '\xcc\xa8' : '',         # modifier - under curve
    '\xe2\x80\x93' : '-',    # long hyphen
    '\xc2\xb3' : '^3',       # superscript 3
    '\x92' : "'",       	 # right single quotation mark
	'\xe2\x80\x99' : "'",    # right single quotation mark
	'\xe2\x80\x93' : "-",    # en dash
    '\xfb' : 'u',    	 	 # latin small letter u with circumflex
    '\xcc\xb1' : ''          # modifier - under line
	}
	
def replace_chars(match):
	char = match.group(0)
	return chars[char]

def commonCacheKey(funct, *args):
	# hashkey created for use with the Common plugin cache
	name = repr(funct)
	if name.find(" of ") > -1:
		name = name[name.find("method") + 7:name.find(" of ")]
	elif name.find(" at ") > -1:
		name = name[name.find("function") + 9:name.find(" at ")]
	keyhash = hashlib.md5()
	for params in args:
		if isinstance(params, dict):
			for key in sorted(params.iterkeys()):
				if key not in ["new_results_function"]:
					keyhash.update("'%s'='%s'" % (key, params[key]))
		elif isinstance(params, list):
			keyhash.update(",".join(["%s" % el for el in params]))
		else:
			try:
				keyhash.update(params)
			except:
				keyhash.update(str(params))
	name += "|" + keyhash.hexdigest() + "|"
	return name
	
remove_ads = ['http://ads.',
	'adconscious.com',
	'animeflavor-gao-gamebox.swf',
	'facebook.com/plugins/',
	'http://www3.game',
	'INSERT_RANDOM_NUMBER_HERE']
	
def cleanSearchText(searchText,skipEnc=False):
	# cleans up the text for easier searching
	# print base_txt + 'Clean up the search term: ' +searchText
	searchText = unescape(searchText)
	searchText = U2A(searchText)
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
	searchText = searchText.replace('[B]','').replace('[/B]','')
	searchText = searchText.replace('[COLOR red]','').replace('[/COLOR]','')
	searchText = searchText.replace('[COLOR yellow]','').replace('[/COLOR]','')
	searchText = searchText.replace('[COLOR green]','').replace('[/COLOR]','')
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

def get_aniDB_list(url=''):	
	
	# xbmc.executebuiltin('XBMC.Notification(Retrieving Info!,aniDB Wishlist,5000,'+icon_sat_dish+')')
	
	if url == '':
		url = 'http://anidb.net/perl-bin/animedb.pl?show=mywishlist&uid=%(un)s&pass=%(pass)s' % {"un": unid, "pass": pubpass}
	
	# pb = xbmcgui.DialogProgressBG()
	# pb.create(base_txt + 'Grabbing aniDB Wishlist', '')
	multiPg = []	
	ii=0
	dirLength = 20
	for pg in xrange(0,dirLength):
		time.sleep(2.5)
		ii+=1
		urlPg = url + '&page=' + str(pg)
		updateText = 'Page ' + str(pg) + ': ' + urlPg
		print base_txt + updateText
		linkPg = grabUrlSource(urlPg)
		if 'No results.' in linkPg:
			print base_txt + 'No more pages to parse'
			break
		else:
			multiPg.append(linkPg)
		
		link = ''.join(multiPg)
		# pb.update(int(ii/float(dirLength)*100), message=updateText)
		if monitor.abortRequested():
			# Abort was requested while waiting. We should exit
			raise IOError('exit Kodi')
	# pb.close()
		
	# print link	
	watchWishlist = anidbQuick.Wishlist(link)	
	watchWishlist.sort(key=lambda name: name[0], reverse=True) 
	watchWishlist.sort(key=lambda name: name[1]) 
	
	return watchWishlist
	
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
	
def get_aniDB_mysummarylist(url=''):		
	
	# xbmc.executebuiltin('XBMC.Notification(Retrieving Info!,aniDB MyList,5000,'+icon_sat_dish+')')
	
	if url == '':
		url = 'http://anidb.net/perl-bin/animedb.pl?show=mylist&uid=%(un)s&pass=%(pass)s' % {"un": unid, "pass": pubpass}
	
	# pb = xbmcgui.DialogProgressBG()
	# pb.create(base_txt + 'Grabbing aniDB MyList', '')
	multiPg = []	
	ii=0
	dirLength = 40
	for pg in xrange(0,dirLength):
		time.sleep(3)
		ii+=1
		urlPg = url + '&page=' + str(pg)
		updateText = 'Page ' + str(pg) + ': ' + urlPg
		print base_txt + updateText
		linkPg = grabUrlSource(urlPg)
		if 'No results.' in linkPg:
			print base_txt + 'No more pages to parse'
			break
		else:
			multiPg.append(linkPg)
		
		link = ''.join(multiPg)
		# pb.update(int(ii/float(dirLength)*100), message=updateText)
		if monitor.abortRequested():
			# Abort was requested while waiting. We should exit
			raise IOError('exit Kodi')
	# pb.close()
		
	watchMylistSummary = anidbQuick.MyListSummary(link)	
	watchMylistSummary.sort(key=lambda name: name[0], reverse=True) 
	watchMylistSummary.sort(key=lambda name: name[1]) 
	
	return watchMylistSummary
	
def list_watchlisttotal():	
	watchListTotal = []
	watchListTotal = list_mylist() + list_wishlist()
	# watchMylistSummary = list_mylist()
	# watchListTotal = watchMylistSummary + watchListTotal
	watchListTotal.sort(key=lambda name: name[2][1], reverse=True) 
	watchListTotal = f2(watchListTotal)
	
	return watchListTotal
	
def html_special(text):
	text = text.replace('&lsquo;',"'")
	text = text.replace('&Lsquo;',"'")
	text = text.replace('&rsquo;',"'")
	text = text.replace('&Rsquo;',"'")
	text = text.replace('&quot;','"')
	text = text.replace('&Quot;','"')
	text = text.replace('&8217;',"'")
	return text
	
def get_tvdb_id(aid):
	
	tvdbid = ['0','1']
	
	aniInfo = cache.cacheFunction(get_ani_aid_list)
	
	for aidFound, name, tvdbidFound, season in  aniInfo:
		if tvdbidFound.isdigit() and str(aidFound) == str(aid):
			return [tvdbidFound,season]	
	
	return tvdbid	
	
def get_anidb_id(tvdbid):
	
	aidGroup = []
	
	aniInfo = cache.cacheFunction(get_ani_aid_list)
	
	dirLength = len(aniInfo)
	print base_txt + '# of Series Nodes: ' + str(dirLength) 
	
	print base_txt + 'Looking up aid regarding tvdbid: ' + str(tvdbid) 
	
	for aidFound, name, tvdbidFound, season in  aniInfo:
		if tvdbidFound.isdigit() and str(tvdbidFound) == str(tvdbid):	
			aidGroup.append([aidFound, name, tvdbidFound, season])
	
	aidGroup.sort(key=lambda name: name[0]) 
	aidGroup.sort(key=lambda name: name[3]) 
	aidGroup = f2(aidGroup)
	return aidGroup
	
def get_ani_aid_v2(searchText):
	
	aid = '0'
	if not searchText=='':
		aniInfo = cache.cacheFunction(get_ani_aid_list)
		searchText_org = searchText		
		searchAlts = []
		
		searchAlts.append(searchText)
		
		subLoc = searchText.find('(')
		if subLoc > 0:
			searchText = searchText[:subLoc]
		searchText = urllib.unquote(searchText).title()
		
		searchAlts = searchAlts + getAltNames(searchText)
		
		searchAlts.sort(key=lambda name: name[0]) 
		print base_txt + 'Searching ' + str(len(searchAlts)) + ' alternate names + variations of:' + searchText_org	
		for aidfound, name, tvdbid, season in aniInfo:
			for nameSearch in searchAlts:			
				if name.lower() == nameSearch.lower():
					return aidfound
	return aid	
	
def get_ani_aid_list():

	groupUrl = anime_list
	# groupUrl.append('https://sites.google.com/site/anidblist/anime-list.xml?attredirects=0')
	# groupUrl.append('https://raw.github.com/torenado/plugin.video.animestream/master/anime-list_modded.xml')
	
	linkAID = ''
	for url in groupUrl:
		linkAID = linkAID + str(grabUrlSource(url))

	linkAID = linkAID.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('> <','><')
	match=re.compile('<anime (.+?)</anime>').findall(linkAID)
	aniInfo = []
	aid = ''
	name = ''
	tvdbid = ''
	season='1'
	for aniInfoRaw in match:
		# aniRow=re.compile('anidbid="(.+?)" tvdbid="(.+?)"(.+?)><name>(.+?)</name>').findall(aniInfoRaw)
		# aid = aniRow[0][0]
		# tvdbid = aniRow[0][1]
		aid = re.compile('anidbid="(.+?)"').findall(aniInfoRaw)[0]
		tvdbid = re.compile('tvdbid="(.+?)"').findall(aniInfoRaw)[0]
		season=re.compile('defaulttvdbseason="(.+?)"').findall(aniInfoRaw)[0]
		# aniRow=re.compile('defaulttvdbseason="(.+?)"').findall(aniInfoRaw)
		# season = aniRow[0]
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
	
	dirLength = len(aniInfo)
	print base_txt + '# of Series Nodes: ' + str(dirLength) 
	return aniInfo
	
def streamSiteSeriesList_aniUrl_old():
	# Searches the various websites for the searched content
	
	searchSiteList = []
	
	
	for streamList in streamSiteList:
		siteBase = streamList + '.base_url_name'
		site_base_url = eval(siteBase)
		searchSiteList.append([streamList, site_base_url])
	
	if(len(searchSiteList) < 1):
		searchSiteList = [animefushigi.base_url_name]
		print base_txt +  'No sites choosen in the settings.  Using animefushigi.com'
	
	searchRes = []
	aniUrl_list = []
	
	for streamList, url in searchSiteList:
		siteBase = streamList + '.base_url_name'
		site_base_url = eval(siteBase)
		if (site_base_url in url):
			siteBase = streamList + '.aniUrls'
			site_aniUrls = eval(siteBase)
			for aniUrl, type in site_aniUrls:
				aniUrl_list.append([streamList,aniUrl, type])
				if monitor.abortRequested():
					# Abort was requested while waiting. We should exit
					raise IOError('exit Kodi')
	
	dirLength = len(aniUrl_list)
	print base_txt + '# of items: ' + str(dirLength)
	
	ii=0
	pb = xbmcgui.DialogProgressBG()
	pb.create(base_txt + 'Grabbing Series URLs', '')
	for streamList,aniUrl,type in aniUrl_list:
		ii+=1
		updateText = str(ii) + ' of ' + str(dirLength) + ': ' + streamList + ': '
		print base_txt + updateText + aniUrl
		link = ''
		link = grabUrlSource(aniUrl)	
		siteBase = streamList + '.Total_Video_List(link)'
		searchRes = searchRes + eval(siteBase)
		pb.update(int(ii/float(dirLength)*100), message=updateText)
		if monitor.abortRequested():
			# Abort was requested while waiting. We should exit
			raise IOError('exit Kodi')
	pb.close()
		
	searchRes = U2A_List(searchRes)
	searchRes = f2(searchRes)
	searchRes.sort(key=lambda name: name[1], reverse=True) 
	
	return searchRes
	
def streamSiteSeriesList_aniUrl():
	# Searches the various websites for the searched content
	
	searchSiteList = []
	
	
	for streamList in streamSiteList:
		siteBase = streamList + '.base_url_name'
		site_base_url = eval(siteBase)
		searchSiteList.append([streamList, site_base_url])
	
	if(len(searchSiteList) < 1):
		searchSiteList = [animefushigi.base_url_name]
		print base_txt +  'No sites choosen in the settings.  Using animefushigi.com'
	
	searchRes = []
	aniUrl_list = []
	
	
	dirLength = len(searchSiteList)
	print base_txt + '# of items: ' + str(dirLength)
	
	ii=0
	pb = xbmcgui.DialogProgressBG()
	pb.create(base_txt + 'Grabbing Series URLs', '')
	for streamList, url in searchSiteList:
		ii+=1
		siteBase = streamList + '.base_url_name'
		site_base_url = eval(siteBase)
		if (site_base_url in url):
			siteBase = streamList + '.aniUrls'
			site_aniUrls = eval(siteBase)
			# for aniUrl, type in site_aniUrls:
				# aniUrl_list.append([streamList,aniUrl, type])
				# searchRes = []
			for url, type in site_aniUrls:
				updateText = str(ii) + ' of ' + str(dirLength) + ': ' + streamList + ': '
				print base_txt + updateText + url
				pb.update(int(ii/float(dirLength)*100), message=updateText)
				link = grabUrlSource(url)
				siteBase = streamList + '.Total_Video_List(link)'
				searchRes = searchRes + [x + [type] for x in eval(siteBase)]
				if monitor.abortRequested():
					# Abort was requested while waiting. We should exit
					raise IOError('exit Kodi')
	pb.close()
		
	searchRes = U2A_List(searchRes)
	searchRes = f2(searchRes)
	searchRes.sort(key=lambda name: name[1], reverse=True) 
	
	return searchRes
	
garbage_links = ['Http:',
	'Http',
	'<Span',
	'<Imgsrc',
	'**',
	'</Div>',
	'<Span>',
	'--//<',
	'Document.Write',
	'Genres No Genres Yet',
	'<Img']
	
def streamSiteSeriesList():
	# Searches the various websites for the searched content
	
	searchRes = streamSiteSeriesList_aniUrl()
	dirLength = len(searchRes)
	print base_txt + '# of URLs: ' + str(dirLength)
	
	row=[]
	searchRes2 = []
	ii=0
	pb = xbmcgui.DialogProgressBG()
	pb.create(base_txt + 'Removing Garbage Links', '')
	for row in searchRes:
		ii+=1
		name = convertName(row[1])
		link = row[0]
		type = row[2]
		updateText = str(ii) + ' of ' + str(dirLength) + ': ' + name
		pb.update(int(ii/float(dirLength)*100), message=updateText)
		# print base_txt + updateText
		if (not(any(skip_ads in row for skip_ads in garbage_links) or name.startswith('*'))):
			# if not (row[1]=='' and 'Http:' in row[1] and '<Span' in row[1] and '<Imgsrc' in row[1]): 
			searchRes2.append([link,name,type])
		if monitor.abortRequested():
			# Abort was requested while waiting. We should exit
			raise IOError('exit Kodi')
	pb.close()
	
	searchRes2.sort(key=lambda name: name[1])
	searchRes = f2(searchRes2)
	
	dirLength = len(searchRes)
	print base_txt + '# of URLs remaining (after garbage links removed): ' + str(dirLength)
	
	return searchRes

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
	# name = name.replace('Dragonball','Dragon Ball')
	# name = name.replace('Diamonddust','Diamond Dust')
	# name = name.replace('Highschool','High School')
	# name = name.replace('Fatestaynightunlimitedbladeworks','Fate Stay Night Unlimited Blade Works')
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

def getAltNames(name):
	
	searchAlts = []	
	if isinstance(name,list):
		for nameTxt in name:
			searchAlts = searchAlts + getAltNames2(nameTxt)
	else:
		searchAlts = searchAlts + getAltNames2(name)
		
	searchAlts = f2(searchAlts)	
	return searchAlts

def getAltNames2(name):
	searchAlts = []		
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
	searchAlts = searchAlts + altName(name,'+')
	searchAlts = searchAlts + altName(name,',')
	searchAlts = searchAlts + altName(name,'/')
	searchAlts = searchAlts + altName(name,'\\')
	searchAlts = searchAlts + altName(name,' and ')
	searchAlts = searchAlts + altName(name,' &Amp; ')
	if name.startswith('The'):
		searchAlts.append(name.replace('The ',''))
	searchAlts = searchAlts + altName(searchAlts,' ')
	searchAlts = f2(searchAlts)	
	return searchAlts
	
def getSeriesEpisodeList(groupUrls, aid=0, tvdbid=0, seriesName=''):
	
	try:
		urls = groupUrls.split(' <--> ')
	except:
		urls = groupUrls
		
	epListAll = []
	epList = []
		
	dirLength = len(urls)	
	print base_txt + '# of episode URLs: ' + str(dirLength)
	
	ii=0	
	updateText = ''
	
	for url in urls:
		ii += 1
		
		link = ''
		link = grabUrlSource(url)
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
			if monitor.abortRequested():
				# Abort was requested while waiting. We should exit
				raise IOError('exit Kodi')				
		epListAll = epListAll + epList
		
	epListAllClean = []
	for episodePageLink, episodePageName, episodeMediaThumb, epNum, epSeason in epListAll:		
		episodePageName = episodePageName.title().replace(' Episode','').replace('#','').replace(' - ',' ').replace(':',' ').replace('-',' ').strip()
		epListAllClean.append([aid, tvdbid, seriesName, episodePageLink, episodePageName, '', int(epNum), int(epSeason)])
	
	epListAll = epListAllClean
	epListAll.sort(key=lambda a:(a[7],a[6]), reverse=True) 
	epListAll = f2(epListAll)
	# epListAll.append(['','END','','',''])
	epListAll = U2A_List(epListAll)
	
	return epListAll
	
def getEpisodeMediaURL(episodeLinkInfo):
	
	[aid, tvdbid, seriesName, episodePageName, epNum, epSeason, groupUrl] = episodeLinkInfo
	urls=[]
	try:
		urls = groupUrl.split(' <--> ')
	except:
		urls = groupUrl
	
	urls = f2(urls)
	epMediaAll = []
	epMedia = []
	
	dirLength = len(urls)	
	print base_txt + '# of media URLs: ' + str(dirLength)
	
	# grab media link from the streaming episode page
	ii=0
	for url in urls:
		print base_txt + url
		ii += 1
		epMedia_subdub = []	
		for streamList in streamSiteList:
			siteBase = streamList + '.base_url_name'
			site_base_url_name = eval(siteBase)
			if (site_base_url_name in url):
				updateText = 'Streaming Media from: ' + streamList
				print base_txt + str(ii) + ' of ' + str(dirLength) +' - '+ updateText
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
			if monitor.abortRequested():
				# Abort was requested while waiting. We should exit
				raise IOError('exit Kodi')				
				
		epMediaAll = epMediaAll + epMedia
	
	# print epMediaAll
		
	epMediaAll_2=[]
	siteNnameTest=''
	mirrorTest=0 
	partTest=0
	for siteNname, url, mirror, part, subdub in reversed(epMediaAll):
		if not(siteNnameTest==siteNname and mirrorTest==mirror):
			totParts = part
			siteNnameTest = siteNname 
			mirrorTest = mirror
		epMediaAll_2.append([aid, tvdbid, seriesName, episodePageName, epNum, epSeason, siteNname, url, mirror, part, totParts, subdub])
		
	epMediaAll_2.sort(key=lambda a:(a[6],a[8],a[9]))
	return epMediaAll_2
	
def resolveMediaURL(mediaInfo):
	return cache.cacheFunction(resolveMediaURL_Src,mediaInfo)

def resolveMediaURL_Src(mediaInfo):
	
	[aid, tvdbid, seriesName, episodePageName, epNum, epSeason, siteNname, url, mirror, part, totParts, subdub] = mediaInfo
	mediaValid = []
	hostName = ''
	media_url = ''
	mediaOrder = 100
	if 'vidxden' in url:
		url = 'http://www.vidxden.com/CAPTCHA/nuisance'
	if 'vidbux' in url:
		url = 'http://www.vidbux.com/CAPTCHA/nuisance'
	if 'dailymotion' in url:
		url = 'http://www.dailymotion.com/CAPTCHA/nuisance'
		
	try:
		media_url = urlresolver.HostedMediaFile(url).resolve()
		# print base_txt + media_url
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
	
	url = urllib.unquote(url)
	if media_url:
		# print base_txt + 'Mirror: ' + str(mirror) + ' Part: ' + str(part)
		media_url = urllib.unquote(media_url)
		print base_txt + episodePageName + ' - ' + media_url
		hostName = urlresolver.HostedMediaFile(url).get_host()
		if len(hostName)<1:
			hostName = media_url.split('/')[2]
		if 'auengine' in hostName:
			mediaOrder = 10
		elif 'mp4upload' in hostName:
			mediaOrder = 20
		elif 'video44' in hostName:
			mediaOrder = 30
		elif 'videoweed' in hostName:
			mediaOrder = 40
		else:
			mediaOrder = 100
			
		mediaValid = [aid, tvdbid, seriesName, episodePageName, epNum, epSeason, siteNname, url, mirror, part, totParts, subdub, hostName, media_url, mediaOrder]
		
	return mediaValid
	
def addHours(tm, hrs):
	#http://stackoverflow.com/questions/100210/what-is-the-standard-way-to-add-n-seconds-to-datetime-time-in-python
    fulldate = datetime.datetime(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + datetime.timedelta(hours=hrs)
    return fulldate
	
def search_aid_tvid(searchText, aidGet=False, tvdbGet=True):
	
	con = sqlite.connect(user_path)
	aid = '0'
	tvdbid = '0'
	
	if searchText=='' or any(skip_ads in searchText for skip_ads in garbage_links):
		print base_txt + ' SKIPPED ===> ' + searchText
		return aid,tvdbid
	
	aid = get_ani_aid_v2(searchText)	
	tvdbid = get_tvdb_id(aid)[0]
	
	if aid=='0':
		searchText = cleanSearchText(searchText)
		aid = get_ani_aid_v2(searchText)	
		tvdbid = get_tvdb_id(aid)[0]
		serDBaid= 'aid='+aid
	
	if not aid=='0':
		return aid,tvdbid
	
	search2 = 'name LIKE "%'+cleanSearchText(searchText)+'%" or altName LIKE "%'+cleanSearchText(searchText)+'%"'
	with con:
		cur = con.cursor()
		con.text_factory = str
		sql = 'SELECT aid,tvdbSer FROM AIDSeries WHERE '+search2+' GROUP BY aid'
		print base_txt + sql
		cur.execute(sql)
		getTvdbSer = cur.fetchall()
		
	if len(getTvdbSer)==1:
		aid = getTvdbSer[0][0]
		tvdbid = getTvdbSer[0][1]
	elif len(getTvdbSer)>1:
		aid = getTvdbSer[0][0]
		tvdbid = getTvdbSer[0][1]
	
	if aid is not None and tvdbid is not None and not aid=='0':
		return aid,tvdbid
	
	tvdb_detail_search=[]
	if tvdbGet and tvdbid=='0':	
		time.sleep(2.5)		
		tvdbUrl = 'http://www.thetvdb.com/api/GetSeries.php?seriesname='
		seachTitle = '+'.join(searchText.replace('.','').split())
		
		url = tvdbUrl + seachTitle
		linkTVDB = grabUrlSource(url)
	
		# tvdb_detail_search = anidbQuick.TVDBID_Search(linkTVDB)
		tvdb_detail_search = cache.cacheFunction(anidbQuick.TVDBID_Search,linkTVDB)
	
	if aidGet and aid=='0':
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
		aidFound = aid
	elif len(tvdb_detail_search)==1:
		tvdbid = str(tvdb_detail_search[0][1])
		name = str(tvdb_detail_search[0][0])
		print ' ---- '
		print '  <anime anidbid="t' + tvdbid + '" tvdbid="' + tvdbid + '" defaulttvdbseason="1">	<name>' + name + '</name>  </anime>'
		print ' ---- '	
		aidFound = 't' + tvdbid
	elif len(tvdb_detail_search)>1:
		print base_txt + 'Multiple matches found...Please choose one.'
	
	if len(tvdb_detail_search)==1:
		with con:
			cur = con.cursor()
			con.text_factory = str
			synAniList = []
			if not aid == '0':
				sql = 'SELECT name FROM SynonymSeries WHERE aid="%s"' % aid
				cur.execute(sql)
				synAniList = cur.fetchall()
				synAniList = [x[0] for x in synAniList]
				
			searchAlts = []
			searchAlts.append(cleanSearchText(name))
			searchAlts = searchAlts + getAltNames(name)
			searchAlts = searchAlts + getAltNames(name) + getAltNames(synAniList)
			searchAlts = f2(searchAlts)
			
			sql_para = (name, aidFound, ' <--> '.join(searchAlts))
			try:
				print base_txt + sql
				cur.execute('INSERT OR REPLACE INTO SeriesNameAID (name,aid,altName) VALUES ("%s","%s","%s")'% sql_para)
			except:
				err_txt = 'database insertion failed: %s, %s, %s'% sql_para
				print base_txt + err_txt
	
	
	return aid,tvdbid

def allAnimeList(url=''):
	# Searches the various websites for the searched content
	
	searchSiteList = []
	
	con = sqlite.connect(user_path)
	with con:
		cur = con.cursor()
		con.text_factory = str
	
		# print base_txt + sql
		
		searchRes = []
		searchRes = streamSiteSeriesList()
		row=[]
		dirLength = len(searchRes)
		print base_txt + '# of items: ' + str(dirLength)
		pb = xbmcgui.DialogProgressBG()
		updateText = 'Updating Series Links DB'
		print base_txt + updateText
		pb.create(base_txt + updateText, '# of items: ' + str(dirLength))
		ii=0
		name2=''
		for row in searchRes:
			ii+=1
			name = convertName(row[1])
			link = row[0]
			type = row[2]
			if not(any(skip_ads in link for skip_ads in garbage_links)):
				if '"' in link:
					link = link.replace('"',"%22")	
				# sql_para = (link, name, type)	
				cur.execute('SELECT * FROM SeriesContentLinks WHERE link="%s"' % link)   
				rows = cur.fetchall()
				if len(rows)==0: 
					(aid,tvdbid) = search_aid_tvid(name, aidGet=True, tvdbGet=True)
					if '"' in name:
						name = name.replace('"',"&Quot;")
					
					if aid=='0':
						sql = 'SELECT aid FROM SeriesContentLinks WHERE aid LIKE "un%" ORDER BY aid DESC'
						print base_txt + sql
						cur.execute(sql)
						rows = cur.fetchall() 
						if len(rows)==0:
							aid = 'un%07d' % (1,)
						else:
							# print str(rows[0][0]).split('un')
							last_un = str(rows[0][0]).split('un')[1]
							aid = 'un%07d' % (int(last_un)+1,)
						
					season = int(get_tvdb_id(aid)[1])
					sql_para = (link, name, aid, season, type)
					name2 = name
					updateText = str(ii) + ' of ' + str(dirLength) + ': ' + name + ': '
					print base_txt + updateText
					sql = 'INSERT INTO SeriesContentLinks VALUES(?,?,?,?,?)' 
					# sql = 'INSERT INTO SeriesContentLinks VALUES(?,?,?)' 	
					cur.execute(sql,sql_para)
				# else:
					# print base_txt + 'RECORD ALREADY EXISTS - INSERT INTO SeriesContentLinks ... link = ' + sql_para[0]
				
			pb.update(int(ii/float(dirLength)*100), updateText,name2)
			if monitor.abortRequested():
				# Abort was requested while waiting. We should exit
				raise IOError('exit Kodi')
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

def get_ani_searchText(aid):

	aidList = cache.cacheFunction(get_ani_aid_list)

	print base_txt + 'Searching anime-list for aid: ' + str(aid)
	
	searchText = []
	for aidFound, name, tvdbid, season in  aidList:
		if aidFound == aid:
			searchText.append(name)
			
	return searchText
	
def name2aid2(replace_all=0):
	# create/update content name to aid map
	
	con = sqlite.connect(user_path)
	with con:
		cur = con.cursor()
		sql = 'CREATE TABLE IF NOT EXISTS SeriesNameAID(name TEXT PRIMARY KEY, aid TEXT, altName TEXT)'
		cur.execute(sql)
		sql = 'CREATE VIEW IF NOT EXISTS linkAID AS SELECT SeriesContentLinks.link,SeriesContentLinks.name,SeriesNameAID.aid,SeriesNameAID.altName FROM SeriesContentLinks '
		sql = sql + 'LEFT JOIN SeriesNameAID ON SeriesContentLinks.name = SeriesNameAID.name ORDER BY SeriesContentLinks.name'
		cur.execute(sql)
		sql = 'CREATE VIEW IF NOT EXISTS AIDSeries AS SELECT linkAID.*, '
		sql = sql + 't1.tvdbSer, t1.description, t1.fanart, t1.iconimage, t1.genre, t1.year, t1.season, t1.adult, t1.epwatch, t1.eptot, t1.playcount '
		sql = sql + 'FROM linkAID '
		sql = sql + 'LEFT JOIN Series AS t1 ON linkAID.aid = t1.aid ORDER BY name'
		cur.execute(sql)
		
	# from anime-list.xml
	aidList = cache.cacheFunction(get_ani_aid_list)
	aidList.sort(key=lambda name: name[1]) 
	dirLength = len(aidList)
	print base_txt + '# of items: ' + str(dirLength)
	pb = xbmcgui.DialogProgress()
	if replace_all:
		updateText = 'Refreshing SeriesNameAID DB: anime-list'
		print base_txt + updateText
		pb.create(updateText, '# of items: ' + str(dirLength))
	else:
		updateText = 'Updating SeriesNameAID DB: anime-list'
		print base_txt + updateText
		pb.create(updateText, '# of items: ' + str(dirLength))
	ii=0
	name2=''
	sql = 'INSERT INTO SeriesNameAID VALUES(?,?,?)' 
	with con:
		cur = con.cursor()
		con.text_factory = str
		# nameList = '"' + '","'.join(extract_column(aidList,[1])) + '"'		
		cur.execute('SELECT name FROM SeriesNameAID')   
		SeriesNameAID_rows = cur.fetchall() 
	aidList = remove_like_elements(aidList,SeriesNameAID_rows,1)
	dirLength = len(aidList)
	print base_txt + str(dirLength) + ' rows being added to ' + str(len(SeriesNameAID_rows)) + ' rows in SeriesNameAID table'
	for aidFound, name, tvdbid, season in  aidList:
		ii+=1		
		# if name not in  extract_column(SeriesNameAID_rows,[0]):	
		name2 = name	
		with con:
			cur = con.cursor()
			con.text_factory = str
			searchAlts = []
			searchAlts.append(cleanSearchText(name))
			searchAlts = searchAlts + getAltNames(name)
			searchAlts = f2(searchAlts)
			
			sql_para = (name, aidFound, ' <--> '.join(searchAlts))
			try:
				if replace_all:
					cur.execute('INSERT OR REPLACE INTO SeriesNameAID (name,aid,altName) VALUES ("%s","%s","%s")'% sql_para)
				else:
					cur.execute('INSERT INTO SeriesNameAID (name,aid,altName) VALUES ("%s","%s","%s")'% sql_para)
					
			except:
				if replace_all:
					err_txt = 'database insertion failed: %s, %s, %s'% sql_para
					print base_txt + err_txt	
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
	updateText = 'Updating SeriesNameAID DB: aniDBFullList'
	print base_txt + updateText
	pb.create(updateText, '# of items: ' + str(dirLength))
	ii=0
	name2=''
	sql = 'INSERT INTO SeriesNameAID VALUES(?,?,?)' 
	
	# with con:
		# cur = con.cursor()
		# con.text_factory = str
		# nameList = '"' + '","'.join(extract_column(aidList,[1])) + '"'		
		# cur.execute('SELECT name FROM SeriesNameAID')   
		# rows = cur.fetchall() 
	
	aidList = remove_like_elements(aidList,SeriesNameAID_rows,1)
	dirLength = len(aidList)
	print base_txt + str(dirLength) + ' rows being added to ' + str(len(SeriesNameAID_rows)) + ' rows in SeriesNameAID table'
	for aidFound, name, eps in  aidList:
		ii+=1	
		# with con:
			# cur = con.cursor()
			# con.text_factory = str
			# cur.execute('SELECT * FROM SeriesNameAID WHERE name="%s"' % name)   
			# rows = cur.fetchall() 
			
		name2 = name
		updateText = str(ii) + ' of ' + str(dirLength) + ': ' + name2
		print base_txt + updateText
		searchAlts = []
		searchAlts.append(cleanSearchText(name))
		searchAlts = searchAlts + getAltNames(name)
		searchAlts = f2(searchAlts)
		
		sql_para = (name, aidFound, ' <--> '.join(searchAlts))
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
	updateText = 'Updating SeriesNameAID DB: Series'
	print base_txt + updateText
	pb.create(updateText, '# of items: ' + str(dirLength))
	ii=0
	name2=''
	sql = 'INSERT INTO SeriesNameAID VALUES(?,?,?)' 
	with con:
		cur = con.cursor()
		con.text_factory = str
		# nameList = '"' + '","'.join(extract_column(aidList,[1])) + '"'		
		cur.execute('SELECT name FROM SeriesNameAID')   
		# rows = cur.fetchall() 
		
	searchRes = remove_like_elements(searchRes,SeriesNameAID_rows)
	dirLength = len(searchRes)
	print base_txt + str(dirLength) + ' rows being added to ' + str(len(SeriesNameAID_rows)) + ' rows in SeriesNameAID table'
	# print searchRes
	for searchText in searchRes:
		ii+=1			
		name = searchText[0]
		# with con:
			# cur = con.cursor()
			# con.text_factory = str
			# cur.execute('SELECT * FROM SeriesNameAID WHERE name="%s"' % searchText[0])   
			# rows = cur.fetchall() 
			
		name2 = name 
		aidFound = searchText[1]
		updateText = str(ii) + ' of ' + str(dirLength) + ': ' + name2
		print base_txt + updateText
		searchAlts = []
		searchAlts.append(cleanSearchText(name))
		searchAlts = searchAlts + getAltNames(name)
		searchAlts = f2(searchAlts)
		
		sql_para = (name, aidFound, ' <--> '.join(searchAlts))
		print sql_para		
		with con:
			cur = con.cursor()
			con.text_factory = str
			cur.execute(sql,sql_para)
		pb.update(int(ii/float(dirLength)*100),name2,str(ii) + ' of ' + str(dirLength))	
		if (pb.iscanceled()): return
	pb.close()
	
	# remove garbage links
	with con:
		cur = con.cursor()
		con.text_factory = str		
		for rm_record in garbage_links:
			sql = 'DELETE FROM SeriesContentLinks WHERE name LIKE "%'+ rm_record +'%"'
			print base_txt + sql
			cur.execute(sql)
			
		sql = 'SELECT * FROM SeriesNameAID ORDER BY name'
		print base_txt + sql
		cur.execute(sql)
		return cur.fetchall()
	
def name2aid(replace_all=0):
	# create/update content name to aid map
	
	con = sqlite.connect(user_path)
	with con:
		cur = con.cursor()
		sql = 'CREATE TABLE IF NOT EXISTS SeriesNameAID(name TEXT PRIMARY KEY, aid TEXT, altName TEXT)'
		cur.execute(sql)
		sql = 'CREATE VIEW IF NOT EXISTS linkAID AS SELECT SeriesContentLinks.link,SeriesContentLinks.name,SeriesNameAID.aid,SeriesNameAID.altName FROM SeriesContentLinks '
		sql = sql + 'LEFT JOIN SeriesNameAID ON SeriesContentLinks.name = SeriesNameAID.name ORDER BY SeriesContentLinks.name'
		cur.execute(sql)
		sql = 'CREATE VIEW IF NOT EXISTS AIDSeries AS SELECT linkAID.*, '
		sql = sql + 't1.tvdbSer, t1.description, t1.fanart, t1.iconimage, t1.genre, t1.year, t1.season, t1.adult, t1.epwatch, t1.eptot, t1.playcount '
		sql = sql + 'FROM linkAID '
		sql = sql + 'LEFT JOIN Series AS t1 ON linkAID.aid = t1.aid ORDER BY name'
		cur.execute(sql)
		
	# from anime-list.xml
	aidList = cache.cacheFunction(get_ani_aid_list)
	
	# from aniDBFullList
	groupUrl = []
	groupUrl.append('http://anidb.net/api/animetitles.xml.gz')
	
	# linkAID = ''
	# for url in groupUrl:
		# linkAID = linkAID + str(grabUrlSource(url))
		
	# aidList = aidList + anidbQuick.aniDBFullList(linkAID)
	
	aidList.sort(key=lambda name: name[1]) 
	aidList = f2(aidList)
	dirLength = len(aidList)
	print base_txt + '# of items: ' + str(dirLength)
	pb = xbmcgui.DialogProgress()
	if replace_all:
		updateText = 'Refreshing SeriesNameAID DB'
		print base_txt + updateText
		pb.create(updateText, '# of items: ' + str(dirLength))
	else:
		updateText = 'Updating SeriesNameAID DB'
		print base_txt + updateText
		pb.create(updateText, '# of items: ' + str(dirLength))
	ii=0
	name2=''
	sql = 'INSERT INTO SeriesNameAID VALUES(?,?,?)' 
	dirLength = len(aidList)
	# print base_txt + str(dirLength) + ' rows being added to ' + str(len(SeriesNameAID_rows)) + ' rows in SeriesNameAID table'
	for aidFound, name, tvdbid, season in  aidList:
		ii+=1		
		# if name not in  extract_column(SeriesNameAID_rows,[0]):		
		with con:
			cur = con.cursor()
			con.text_factory = str
			cur.execute('SELECT * FROM SeriesNameAID WHERE name="%s"' % name)   
			rows = cur.fetchall() 
			
			if len(rows)==0:
				synAniList = []
				if not aidFound == '0':
					sql = 'SELECT name FROM SynonymSeries WHERE aid="%s"' % aidFound
					cur.execute(sql)
					synAniList = cur.fetchall()
					synAniList = [x[0] for x in synAniList]
				
				name2 = name	
				searchAlts = []
				searchAlts.append(cleanSearchText(name))
				searchAlts = searchAlts + getAltNames(name) + getAltNames(synAniList)
				searchAlts = f2(searchAlts)
				
				sql_para = (name, aidFound, ' <--> '.join(searchAlts))
				try:
					if replace_all:
						cur.execute('INSERT OR REPLACE INTO SeriesNameAID (name,aid,altName) VALUES ("%s","%s","%s")'% sql_para)
					else:
						cur.execute('INSERT INTO SeriesNameAID (name,aid,altName) VALUES ("%s","%s","%s")'% sql_para)
					print base_txt + name + ' aid=' + aidFound + ' being added to SeriesNameAID table'
				except:
					if replace_all:
						err_txt = 'database insertion failed: %s, %s, %s'% sql_para
						print base_txt + err_txt	
		pb.update(int(ii/float(dirLength)*100),name2,str(ii) + ' of ' + str(dirLength))
		if (pb.iscanceled()): return
	pb.close()
	
	# remove garbage links
	with con:
		cur = con.cursor()
		con.text_factory = str		
		for rm_record in garbage_links:
			sql = 'DELETE FROM SeriesContentLinks WHERE name LIKE "%'+ rm_record +'%"'
			print base_txt + sql
			cur.execute(sql)
			
		sql = 'DELETE FROM SeriesContentLinks WHERE aid IS NULL OR trim(aid) = ""'
		print base_txt + sql
		cur.execute(sql)
		
		sql = 'SELECT * FROM SeriesNameAID ORDER BY name'
		print base_txt + sql
		cur.execute(sql)
		return cur.fetchall()
		
def initializeTables():
	# Initialize SQL Tables
	print base_txt + 'Initialize SQL Tables'
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
		
		sql = 'CREATE TABLE IF NOT EXISTS SeriesContentLinks(link TEXT PRIMARY KEY, name TEXT, aid TEXT, season INT, type TEXT)'
		cur.execute(sql)
		
		sql = 'CREATE TABLE IF NOT EXISTS SeriesEpisodeLinks(link TEXT PRIMARY KEY, seriesName TEXT, epName TEXT, aid TEXT, season INT, epNum INT, type TEXT)'
		cur.execute(sql)
		
		sql = 'CREATE TABLE IF NOT EXISTS SeriesNameAID(name TEXT PRIMARY KEY, aid TEXT, altName TEXT)'
		cur.execute(sql)
		
		sql = 'DROP VIEW IF EXISTS linkAID'
		cur.execute(sql)		
		
		sql = 'CREATE VIEW IF NOT EXISTS linkAID AS SELECT SeriesContentLinks.link,SeriesContentLinks.name,SeriesNameAID.aid,SeriesNameAID.altName FROM SeriesContentLinks '
		sql = sql + 'LEFT JOIN SeriesNameAID ON SeriesContentLinks.name = SeriesNameAID.name ORDER BY SeriesContentLinks.name'
		cur.execute(sql)
		
		sql = 'DROP VIEW IF EXISTS AIDSeries'
		cur.execute(sql)	
		
		sql = 'CREATE VIEW IF NOT EXISTS AIDSeries AS SELECT linkAID.*, '
		sql = sql + 't1.tvdbSer, t1.description, t1.fanart, t1.iconimage, t1.genre, t1.year, t1.season, t1.adult, t1.epwatch, t1.eptot, t1.playcount '
		sql = sql + 'FROM linkAID '
		sql = sql + 'LEFT JOIN Series AS t1 ON linkAID.aid = t1.aid ORDER BY name'
		cur.execute(sql)
		
		for rm_record in garbage_links:
			sql = 'DELETE FROM SeriesContentLinks WHERE name LIKE "%'+ rm_record +'%"'
			cur.execute(sql)
		
		sql = 'DELETE FROM SeriesContentLinks WHERE aid IS NULL OR trim(aid) = ""'
		cur.execute(sql)
		
		sql = 'DELETE FROM SeriesNameAID WHERE aid IS NULL OR trim(aid) = ""'
		cur.execute(sql)
		
		sql = 'DELETE FROM Series WHERE aid IS NULL OR trim(aid) = ""'
		cur.execute(sql)
		
def searchCollection(searchText='',aid='0'):
	
	# searchRes = searchCollection_2(searchText,aid)
	
	searchRes = []
	con = sqlite.connect(user_path)
	with con:
		cur = con.cursor()
		con.text_factory = str
		search1 = ''
		search2 = ''
		if not(aid == '0' or aid == 0):
			search1 = 'aid = "' + aid + '"'
			# sql = 'SELECT aid,name, Group_Concat(link," <--> ") as links FROM linkAID WHERE aid = "'+aid+'" ORDER BY name'
			# print base_txt + sql
			# cur.execute(sql)
			# print base_txt + '# of items found: ' + str(cur.fetchall())
			# searchRes = searchRes + cur.fetchall()
		if not searchText == '':
			txt1 = searchText
			txt2 = cleanSearchText(searchText.split(' [')[0])
			if len(txt1)<3:
				search2 = 'name LIKE "'+txt2+'%" or name LIKE "'+txt2+'%"'
			else:
				search2 = 'name LIKE "%'+txt2+'%" or altName LIKE "%'+txt2+'%"'
		
		if search1=='' and search2=='':
			print base_txt + 'no text or aid to search'
			return searchRes
		elif not search1=='' and not search2=='':
			searchAll = search1 + ' or ' + search2
		elif search2=='' and not search1=='':
			searchAll = search1
		elif search1=='' and not search2=='':
			searchAll = search2
		
		sql = 'SELECT aid,name, Group_Concat(link," <--> ") as links FROM linkAID WHERE '+searchAll+' GROUP BY aid'
		print base_txt + sql
		cur.execute(sql)
		searchRes = searchRes + cur.fetchall()		
		print searchRes
		
		sql = 'SELECT tvdbSer FROM AIDSeries WHERE '+searchAll+' GROUP BY tvdbSer'
		print base_txt + sql
		cur.execute(sql)
		getTvdbSer = cur.fetchall()
		print getTvdbSer
		for tvdbSer in getTvdbSer:
			if not tvdbSer[0]==None and not tvdbSer[0]=='0' and not tvdbSer[0]==0:
				sql = 'SELECT aid,name, Group_Concat(link," <--> ") as links FROM AIDSeries WHERE tvdbSer = "'+tvdbSer[0]+'" GROUP BY aid'
				print base_txt + sql
				cur.execute(sql)
				searchRes = searchRes + cur.fetchall()
	
				
	print base_txt + '# of items found: ' + str(len(searchRes))
	searchRes = f2(searchRes)
	# print searchRes
	tempsearchRes = searchRes
	searchRes = []
	for aid, name, url in tempsearchRes:
		if aid is not None:
			name = convertName(name, url)
			if name.endswith('The') or name.endswith('The '):
				name = name[:-3] + ', The'
			searchRes.append([aid,name,url])
	
	searchRes = U2A_List(searchRes)
	try:
		searchRes.sort(key=lambda name: name[1]) 
	except:
		print base_txt + 'Sorting failed in SEARCH()'
	
	searchRes = f2(searchRes)
	print searchRes 
	# print searchRes
	# searchRes = filter(None, searchRes)
	# print searchRes
	
	# return combinedSearchCollect(searchRes)
	return searchRes