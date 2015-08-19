from importlib import import_module
from shutil import move
from shutil import rmtree
from os import makedirs
from os import listdir
from os.path import join
from os.path import splitext
from os.path import dirname
from os.path import basename
from os.path import isdir
from os.path import exists
from hashlib import md5
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
	TMP = 'tmp'

	def __init__(self, path_=None, languages=None):
		"""
		`path_` can be either a directory or a single file.
		`languages` must be a tuple for specific languages, None to search
		with available languages. Language code must be a 2-letters code
		according to the ISO 639-1 or a 3-letters code (ISO 639-2).
		"""
		self.path = path_
		self.languages = languages

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
		for f in listdir(directory):
			if not f.endswith(self.VIDEO_EXTENSIONS):
				continue
			self.subfile(join(directory, f))

	def subfile(self, video):
		logger.info("Searching subtitles for %s...", video)
		subs = self.search(video)
		subpath = None
		for sub in subs:
			try:
				subpath = self._download(sub['url'])
				subpath = self._extract(subpath)
				subpath = self._move(subpath, video)
			except (DownloadError, ExtractError, MoveError) as e:
				logger.error(e)
			else:
				logger.info("Found subtitles for %s...", video)
				break
		else:
			logger.error("No subtitles found for %s...", video)

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
		import extractors

		if subpath.endswith(self.SUB_EXTENSIONS):
			return subpath
		if not subpath.endswith(tuple(extractors.EXTRACTORS.keys())):
			raise ExtractError
		return getattr(
			extractors,
			extractors.EXTRACTORS[splitext(subpath)[1][1:]]
		)(subpath)

	def _move(self, subpath, video):
		_subpath = join(
			dirname(video),
			splitext(basename(video))[0] + splitext(subpath)[1]
		)
		move(subpath, _subpath)

	def search(self, video):
		"""
		Language filtering is done here to avoid as much restriciton as
		possible from the plugins. Not a big operation anyway.
		"""
		subs = []
		for plugin in self.PLUGINS:
			try:
				subs += getattr(
					import_module('plugins.{}'.format(plugin)),
					'search'
				)(video)
			except NoSubsError:
				pass
		if self.languages:
			subs = [s for s in subs if s['language'] in self.languages]
		return sorted(subs, key=lambda k: k['rating'], reverse=True)

	def teardown(self):
		rmtree(self.TMP)
		makedirs(self.TMP)



if __name__ == '__main__':
	LANGUAGES = ('eng', 'fra', 'fre', 'en', 'fr')

	subme = Subme(languages=LANGUAGES)

	while True:
		print("\n\n")
		video_path = input("Drag and drop a file or a directory here: ")
		subme.path = video_path.strip('\'"')

		if not subme.path:
			continue

		subme.start()
