from . import NoSubsError
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
			'evuez'
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
		'url': <subtitle download url>,
		'language': <language>,
		'format': <subtitle format>,
		'rating': <subtitle rating>
	},
	...]
	'language' must be a 2-letters code according to the ISO 639-1 or a
	3-letters code (ISO 639-2).
	"""
	try:
		return [{
				'url': s['ZipDownloadLink'],
				'language': s['SubLanguageID'],
				'format': s['SubFormat'],
				'rating': s['SubRating'],
			} for s in Opensubtitles().search(filepath)
		]
	except KeyError:
		raise NoSubsError
