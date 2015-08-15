import plugins

PLUGINS = {'opensubtitles'}

from plugins import opensubtitles

print(opensubtitles.search('test/ins.mp4'))
