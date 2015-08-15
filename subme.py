import plugins

PLUGINS = {'opensubtitles'}

from plugins import opensubtitles

res = opensubtitles.search('test/ins.mp4')
print(len(res))
print(sorted(res, key=lambda k: k['rating']))
