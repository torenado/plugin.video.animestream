import urllib,urllib2,re,sys,httplib
import cookielib,os,string,cookielib,StringIO
import os,time,base64,logging
import gzip, io
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
