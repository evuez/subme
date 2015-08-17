import logging
from struct import calcsize
from struct import unpack
from os.path import getsize


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class NoSubsError(Exception):
	pass


def os_hash(filepath):
	"""
	Implementation of Opensubtitles' hash function.
	"""
	longlong = '<q'
	bytesize = calcsize(longlong)

	with open(filepath, 'rb') as f:
		filesize = getsize(filepath)
		hash_ = filesize

		if filesize < 65536 * 2:
			return False

		for x in range(65536 // bytesize):
				buf = f.read(bytesize)
				(l_value,) = unpack(longlong, buf)
				hash_ += l_value
				hash_ = hash_ & 0xffffffffffffffff


		f.seek(max(0, filesize - 65536), 0)
		for x in range(65536 // bytesize):
				buf = f.read(bytesize)
				(l_value,)= unpack(longlong, buf)
				hash_ += l_value
				hash_ = hash_ & 0xffffffffffffffff

	return '{:16x}'.format(hash_)
