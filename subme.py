from importlib import import_module
from shutil import move
from os.path import join
from os.path import splitext
from os.path import dirname
from hashlib import md5
from zipfile import ZipFile
from urllib.request import Request
from urllib.request import urlopen
from plugins import logger
from plugins import NoSubsError


PLUGINS = {'opensubtitles'}

media = 'test/bkd.avi'


class DownloadError(Exception):
	pass

class ExtractError(Exception):
	pass

class MoveError(Exception):
	pass

class SubError(Exception):
	pass


class Subme(object):
	PLUGINS = {'opensubtitles'}
	VIDEO_EXTENSIONS = ('avi', 'mp4', 'mkv',)
	SUB_EXTENSIONS = ('srt',)
	ZIP_EXTENSIONS = ('zip',)
	TMP = 'tmp'

	def sub(self, video):
		subs = self.search(video)
		subpath = None
		for sub in subs:
			try:
				subpath = self._download(sub['url'])
				subpath = self._extract(subpath)
				subpath = self._move(subpath, video)
			except (DownloadError, ExtractError, MoveError) as e:
				logger.debug(e)
			else:
				break
		else:
			raise SubError

	def _download(self, suburl):
		subpath = join(TMP, md5(suburl).hexdigest() + splitext(suburl)[1])
		with open(subpath) as f:
			f.write(urlopen(Request(url)).read())
		return subpath

	def _extract(self, subpath):
		"""
		TODO: move "extractors" to a  subpackage for simpler extension
		"""
		if subpath.endswith(SUB_EXTENSIONS):
			return subpath
		if not subpath.endswith(ZIP_EXTENSIONS):
			raise ExtractError
		if subpath.endswith('zip'):
			with ZipFile(subpath) as f:
				subfile = next(
					(s for s in f.namelist() if s.endswith(SUB_EXTENSIONS)),
					None
				)
				return f.extract(subfile, TMP)
		raise ExtractError

	def _move(self, subpath, video):
		_subpath = join(
			dirname(video),
			splitext(basename(video))[0] + splitext(subpath)[1]
		)
		move(subpath, _subpath)

	def search(self, video):
		pass


# def check_path(media):
# 	if not path.exists(media):
# 		logger.error("Cannot find file or directory %s", media)
# 		exit(1)


# def search(media):
# 	subtitles = []
# 	for plugin in PLUGINS:
# 		logger.info("Looking for subtitles with %s...", plugin)
# 		wrapper = import_module('plugins.{}'.format(plugin))
# 		try:
# 			results = getattr(wrapper, 'search')(media)
# 			subtitles.extend(results)
# 			logger.info("Found %d subtitles with %s!", len(results), plugin)
# 		except NoSubsError:
# 			logger.error("No subtitles found with %s!", plugin)

# 	if not subtitles:
# 		logger.error("No subtitle found...")
# 		exit(1)
# 	else:
# 		logger.info("Found %d subtitles!", len(subtitles))
# 		return sorted(subtitles, key=lambda k: k['rating'], reverse=True)


# def download(media, subs):
# 	logger.info("Downloading best subtitle...")
# 	url = subs[0]['url']
# 	with open('tmp/sub.zip', 'wb') as subfile:
# 		subfile.write(urlopen(Request(url)).read())



# check_path(media)
# download(media, search(media))
