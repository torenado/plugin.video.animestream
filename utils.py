import urllib,urllib2,re,sys,httplib
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
	mozilla_user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
	try:
		print 'grabUrlSource: ' + url
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
		link = urllib.unquote(link)
		try:
			link = unescape(link)
		except:
			pass
		# link=link.replace(u'\xa0',u'')
		
		return link
	except urllib2.URLError, e:
		print 'grabUrlSource: got http error %d fetching %s' % (e.code, url)
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
			[' ', '&nbsp;']
		]
		for code in htmlCodes:
			url = url.replace(code[1], code[0])
		return url
	
	return re.sub("&#?\w+;", fixup, text)

def U2A(text):
	# convert Unicode into ASCII
	try:
		return unicodedata.normalize('NFKD', text).encode('ascii','ignore')
	except:
		pass
	
def U2A_List(iterable):
	iterated_object=[]
	for elem in iterable:
		if hasattr(elem,"__iter__"):
			iterated_object.append(U2A_List(elem))
		else:
			iterated_object.append(U2A(elem))
	return iterated_object