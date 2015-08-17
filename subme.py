from importlib import import_module
from os import path
from urllib.request import Request
from urllib.request import urlopen
from plugins import logger
from plugins import NoSubsError


PLUGINS = {'opensubtitles'}

media = 'test/bkd.avi'

def check_path(media):
	if not path.exists(media):
		logger.error("Cannot find file or directory %s", media)
		exit(1)


def search(media):
	subtitles = []
	for plugin in PLUGINS:
		logger.info("Looking for subtitles with %s...", plugin)
		wrapper = import_module('plugins.{}'.format(plugin))
		try:
			results = getattr(wrapper, 'search')(media)
			subtitles.extend(results)
			logger.info("Found %d subtitles with %s!", len(results), plugin)
		except NoSubsError:
			logger.error("No subtitles found with %s!", plugin)

	if not subtitles:
		logger.error("No subtitle found...")
		exit(1)
	else:
		logger.info("Found %d subtitles!", len(subtitles))
		return sorted(subtitles, key=lambda k: k['rating'], reverse=True)


def download(media, subs):
	logger.info("Downloading best subtitle...")
	url = subs[0]['url']
	with open('tmp/sub.zip', 'wb') as subfile:
		subfile.write(urlopen(Request(url)).read())



check_path(media)
download(media, search(media))
