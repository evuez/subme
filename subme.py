from plugins import logger
from plugins import NoSubsError
from importlib import import_module


PLUGINS = {'opensubtitles'}


path = 'test/bkd.avi'
subtitles = []
for plugin in PLUGINS:
	logger.info("Looking for subtitles with %s", plugin)
	wrapper = import_module('plugins.{}'.format(plugin))
	try:
		results = getattr(wrapper, 'search')(path)
		subtitles.extend(results)
		logger.info("Found %d subtitles with %s", len(results), plugin)
	except NoSubsError:
		logger.error("No subtitles found with %s", plugin)
	except FileNotFoundError:
		logger.error("Cannot find file or directory %s", path)

subtitles = sorted(subtitles, key=lambda k: k['rating'])
