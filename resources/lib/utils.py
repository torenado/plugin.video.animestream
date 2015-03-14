import urllib,urllib2,re,sys,httplib, chardet
import gzip, io, htmlentitydefs, unicodedata, hashlib

base_txt = 'animestream: '
plugin_name = "animestream"

remove_ads = ['http://ads.',
	'adconscious.com',
	'animeflavor-gao-gamebox.swf',
	'facebook.com/plugins/',
	'http://www3.game',
	'INSERT_RANDOM_NUMBER_HERE',
	'twitter.com']

try:
	import StorageServer
except:
	import storageserverdummy as StorageServer
	
cache = StorageServer.StorageServer(plugin_name, 24) # (Your plugin name, Cache time in hours)
cache7 = StorageServer.StorageServer(plugin_name, 24*7) # (Your plugin name, Cache time in hours)

def grabUrlSource_Src(url):
	# grab url source data
	# mozilla_user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
	mozilla_user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/0.2.153.1 Safari/525.19'
	mozilla_user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'
	base_txt = 'grabUrlSource: '
	try:
		print base_txt + url
		req = urllib2.Request(url)
		req.add_header('User-Agent', mozilla_user_agent)
		response = urllib2.urlopen(req)
		charset = response.headers.getparam('charset')
		link=response.read()
		encoding = chardet.detect(link)
		if link[:2]=='\x1f\x8b':
			bi = io.BytesIO(link)
			gf = gzip.GzipFile(fileobj=bi, mode="rb")
			link = gf.read()
		response.close()
		link = ''.join(link.splitlines()).replace('\t','')		
		link = urllib.unquote(link)
		
		try:
			link = unescape(link)
			# link = link
		except:
			pass
		# link=link.replace(u'\xa0',u'')
		
		try:
			link = U2A(link)
		except:
			pass
			
		try:
			link = srt(link)
		except:
			pass
		
		return link
	except urllib2.URLError, e:
		try:
			print 'grabUrlSource: got http error %d fetching %s' % (e.code, url)
		except:
			print 'grabUrlSource: FAILED - got UNKNOWN http error'
			
		return 'No Dice'

def grabUrlSource(url):
	try:
		link = cache.cacheFunction(grabUrlSource_Src,url)
		# link = cache.cacheFunction(grabUrlSource_Src,url)
	except:		
		print base_txt + 'grabUrlSource FAILED'
		link = 'No Dice'
		print base_txt + link + ' - ' + url
		
	return link
	
def unescape(text):
	## http://effbot.org/zone/re-sub.htm#unescape-html
	# Removes HTML or XML character references and entities from a text string.
	#
	# @param text The HTML (or XML) source text.
	# @return The plain text, as a Unicode string, if necessary.
	def fixup(m):
		text = m.group(0)
		if text[:2] == "&#":
			# character reference
			try:
				if text[:3] == "&#x":
					return unichr(int(text[3:-1], 16))
				else:
					return unichr(int(text[2:-1]))
			except ValueError:
				pass
		else:
			# named entity
			try:
				text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
			except KeyError:
				pass
		return unescape_m(text) # leave as is
	
	def unescape_m(url):
		htmlCodes = [
			['&', '&amp;'],
			['&', '&Amp;'],
			['<', '&lt;'],
			['<', '&Lt;'],
			['>', '&gt;'],
			['>', '&Gt;'],
			['"', '&quot;'],
			['"', '&Quot;'],
			[' ', '&nbsp;'],
			[' ', '&Nbsp;'],
			["'", '&#039;'],
			["'", '&#8217;'],
			["'", '&8217;'],
			[' ', '&#8211;'],
			['x', '&#215;']
		]
		for code in htmlCodes:
			url = url.replace(code[1], code[0])
		return url
	try:
		return re.sub("&#?\w+;", fixup, text)
		print 'unescape(text): succeeded'
	except:
		pass
		return text

def escapeall(str):
	match = re.compile('([A-Z\~\!\@\#\$\*\{\}\[\]\-\+\.])').findall(str)
	
	for ii in match:
		str = str.replace(ii,'')
		
	return str
		
def U2A_over(text):
	# overwrite encoded character with user defined character	
	try:
		return re.sub('(' + '|'.join(chars.keys()) + ')', replace_chars, text)
	except:
		print 'U2A_over: Conversion to user defined character failed on: ' + text
		return text
		
def U2A(text):
	# convert Unicode into ASCII		
	try:
		str(text)
		return text
	except:
		try:
			return unicodedata.normalize('NFKD', text).encode('ascii','ignore')
		except:
			print 'U2A: Conversion to ASCII failed on: ' + text
			return text
	
def U2A_List(iterable):
	iterated_object=[]
	for elem in iterable:
		if hasattr(elem,"__iter__"):
			iterated_object.append(U2A_List(elem))
		else:
			iterated_object.append(U2A(elem))
	return iterated_object
	
def U2A_List_over(iterable):
	iterated_object=[]
	for elem in iterable:
		if hasattr(elem,"__iter__"):
			iterated_object.append(U2A_List_over(elem))
		else:
			iterated_object.append(U2A_over(elem))
	return iterated_object
	
def find(q):
	return [(k,v) for k, v in aliases.items() if q in k or q in v]
	
def list_decode(txt):
	ll = find('')
	
	for codec, alias in ll:
		try:
			print txt.decode(alias)
		except:
			print 'FAILED: ' + str(alias)
			
def extract_column(whatList,whichCol):
	# Extract specific columns from list - http://stackoverflow.com/questions/12609714/python-extract-specific-columns-from-list
	list1 = whichCol
	list2 = whatList
	newList = [[each_list[ii] for ii in list1] for each_list in list2]
	if len(whichCol)==1:
		newList = [newList[ii][0] for ii in range(0, len(newList))]
	return newList