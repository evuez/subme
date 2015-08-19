from subme import Subme
from zipfile import ZipFile


SUB_EXTENSIONS = Subme.SUB_EXTENSIONS
TMP = Subme.TMP
EXTRACTORS = {
	'zip': 'unzip',
}


"""
Extract functions are given the path of the file containing the subtitles.
They must return the path of the extracted file, and must extract it in the
`TMP` directory.
Extracted file's extension must match one of the `SUB_EXTENSIONS`.
"""


def unzip(filepath):
	with ZipFile(filepath) as f:
		subfile = next(s for s in f.namelist() if s.endswith(SUB_EXTENSIONS))
		return f.extract(subfile, TMP)
