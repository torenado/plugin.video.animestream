"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import re
from t0mm0.common.net import Net
import urllib2
from urlresolver import common
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import xbmcgui

class GogoanimeResolver(Plugin, UrlResolver, PluginSettings):
	implements = [UrlResolver, PluginSettings]
	name = "gogoanime"

	def __init__(self):
		p = self.get_setting('priority') or 100
		self.priority = int(p)
		self.net = Net()
		
		
	def get_media_url(self, host, media_id):
		web_url = self.get_url(host, media_id)
		try:
			link = self.net.http_GET(web_url).content
		except urllib2.URLError, e:
			common.addon.log_error(self.name + '- got http error %d fetching %s' % (e.code, web_url))
			return False
		
		link = ''.join(link.splitlines()).replace('\t','')
		videoUrl = re.compile('"url":"(.+?)"').findall(link)[-1]
		return videoUrl
		
		
	def get_url(self, host, media_id):
		return 'http://www.gogoanime.com/flowplayer/?w=660&h=400&file=%s&#038;sv=1' % media_id
		
		
	def get_host_and_id(self, url):
		r = re.search('//www\.(.+?)/flowplayer/\?w=660&h=400&file=(.+?)&', url)
		if r:
			return r.groups()
		else:
			return False
			
			
	def valid_url(self, url, host):
		return 'gogoanime.com' in url or self.name in host
