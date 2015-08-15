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
			{'limit': 500})
		)['data']



def search(filepath):
	"""
	Return a list of dicts of the form
	[{
		'link': <subtitle download link>,
		'language': <language>,
		'format': <subtitle format>,
		'rating': <subtitle rating>
	},
	...]
	"""
	return [{
			'link': s['SubDownloadLink'],
			'language': s['LanguageName'],
			'format': s['SubFormat'],
			'rating': s['SubRating'],
		} for s in Opensubtitles().search(filepath)
	]
