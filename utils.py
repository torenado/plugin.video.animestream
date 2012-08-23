import urllib,urllib2,re,sys,httplib, chardet
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging
import gzip, io
import htmlentitydefs
import unicodedata
from datetime import datetime
try:
	import json
except ImportError:
	import simplejson as json


def grabUrlSource(url):
	# grab url source data
	# mozilla_user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
	mozilla_user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/0.2.153.1 Safari/525.19 '
	try:
		print 'grabUrlSource: ' + url
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
			['<', '&lt;'],
			['>', '&gt;'],
			['"', '&quot;'],
			[' ', '&nbsp;'],
			["'", '&#039;'],
			["'", '&#8217;'],
			[' ', '&#8211;']
		]
		for code in htmlCodes:
			url = url.replace(code[1], code[0])
		return url
	
	return re.sub("&#?\w+;", fixup, text)


def escapeall(str):
	match = re.compile('([A-Z\~\!\@\#\$\*\{\}\[\]\-\+\.])').findall(str)
	
	for ii in match:
		str = str.replace(ii,'')
		
	return str
	
	
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