from importlib import import_module
from shutil import move
from shutil import rmtree
from os import makedirs
from os.path import join
from os.path import splitext
from os.path import dirname
from os.path import basename
from os.path import isdir
from os.path import exists
from hashlib import md5
from zipfile import ZipFile
from urllib.request import Request
from urllib.request import urlopen
from plugins import logger
from plugins import NoSubsError


class DownloadError(Exception):
	def __init__(self, message="Download error"):
		super().__init__(message)

class ExtractError(Exception):
	def __init__(self, message="Extract error"):
		super().__init__(message)

class MoveError(Exception):
	def __init__(self, message="Move error"):
		super().__init__(message)

class SubError(Exception):
	def __init__(self, message="Sub error"):
		super().__init__(message)


class Subme(object):
	PLUGINS = {'opensubtitles'}
	VIDEO_EXTENSIONS = ('avi', 'mp4', 'mkv',)
	SUB_EXTENSIONS = ('srt',)
	ZIP_EXTENSIONS = ('zip',)
	TMP = 'tmp'

	def __init__(self, path_=None):
		self.path = path_

	def start(self):
		if not exists(self.path):
			raise SubError
		if isdir(self.path):
			self.subdir(self.path)
		elif self.path.endswith(self.VIDEO_EXTENSIONS):
			self.subfile(self.path)
		else:
			raise SubError
		self.teardown()

	def subdir(self, directory):
		pass

	def subfile(self, video):
		subs = self.search(video)
		subpath = None
		for sub in subs:
			try:
				subpath = self._download(sub['url'])
				subpath = self._extract(subpath)
				subpath = self._move(subpath, video)
			except (DownloadError, ExtractError, MoveError) as e:
				logger.info(e)
			else:
				break
		else:
			raise SubError

	def _download(self, suburl):
		request = urlopen(Request(suburl))
		subpath = join(
			self.TMP,
			md5(suburl.encode('utf-8')).hexdigest() +
			splitext(request.info().get_filename())[1]
		)
		with open(subpath, 'wb') as f:
			f.write(request.read())
		return subpath

	def _extract(self, subpath):
		"""
		TODO: move "extractors" to a  subpackage for simpler extension
		"""
		if subpath.endswith(self.SUB_EXTENSIONS):
			return subpath
		if not subpath.endswith(self.ZIP_EXTENSIONS):
			raise ExtractError
		if subpath.endswith('zip'):
			with ZipFile(subpath) as f:
				subfile = next((
					s for s in f.namelist()
					if s.endswith(self.SUB_EXTENSIONS)
				), None)
				return f.extract(subfile, self.TMP)
		raise ExtractError

	def _move(self, subpath, video):
		_subpath = join(
			dirname(video),
			splitext(basename(video))[0] + splitext(subpath)[1]
		)
		move(subpath, _subpath)

	def search(self, video):
		subs = []
		for plugin in self.PLUGINS:
			try:
				subs += getattr(
					import_module('plugins.{}'.format(plugin)),
					'search'
				)(video)
			except NoSubsError:
				pass
		return sorted(subs, key=lambda k: k['rating'], reverse=True)

	def teardown(self):
		rmtree(self.TMP)
		makedirs(self.TMP)


s = Subme()
s.path = "test/bkd.avi"
s.start()
