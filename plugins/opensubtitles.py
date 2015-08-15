from . import os_hash
import xmlrpc.client


URL = 'http://www.opensubtitles.org'
API = 'http://api.opensubtitles.org/xml-rpc'


class Opensubtitles(object):
	def __init__(self):
		self.proxy = xmlrpc.client.ServerProxy(API, allow_none=True)
		self.login()

	def login(self):
		self.token = self.proxy.LogIn(
			None,
			None,
			'en',
			'OSTestUserAgent'
		)['token']

	def search(self, filepath):
		return self.proxy.SearchSubtitles(self.token, (
			{'moviehash': os_hash(filepath)},
			{'limit': 50})
		)



def search(filepath):
	return Opensubtitles().search(filepath)
