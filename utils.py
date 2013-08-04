import urllib,urllib2,re,sys,httplib, chardet
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging
import gzip, io
import htmlentitydefs
import unicodedata
import hashlib
from datetime import datetime
try:
	import json
except ImportError:
	import simplejson as json


def grabUrlSource(url):
	# grab url source data
	# mozilla_user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
	mozilla_user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/0.2.153.1 Safari/525.19 '
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
		
def f2(seq): 
	# order preserving uniqify --> http://www.peterbe.com/plog/uniqifiers-benchmark
	checked = []
	for e in seq:
		if e not in checked:
			checked.append(e)
	return checked	
	
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
	except:
		print 'unescape(text): FAILED - Element failed to reconcile in function'
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