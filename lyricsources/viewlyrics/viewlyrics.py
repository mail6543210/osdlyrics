# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 PedroHLC <pedro.laracampos@gmail.com>
#
# This file is part of OSD Lyrics.
#
# OSD Lyrics is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OSD Lyrics is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OSD Lyrics. If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import bytes

import hashlib
import http.client
import string
import unicodedata
import xml.etree.ElementTree as xet

from osdlyrics.lyricsource import BaseLyricSourcePlugin, SearchResult
from osdlyrics.utils import get_proxy_settings, http_download

VIEWLYRICS_HOST = 'search.crintsoft.com'
VIEWLYRICS_SEARCH_URL = '/searchlyrics.htm'
VIEWLYRICS_BASE_LRC_URL = 'http://viewlyrics.com/'

VIEWLYRICS_QUERY_FORM = '<?xml version=\'1.0\' encoding=\'utf-8\' ?><searchV1 artist="%artist" title="%title"%etc />'
VIEWLYRICS_AGENT = 'MiniLyrics'
VIEWLYRICS_KEY = b'Mlv1clt4.0'


def normalize_str(s):
    """ If s is a unicode string, only keep alphanumeric characters and remove
        diacritics
    """
    try:
        return ''.join(x for x in unicodedata.normalize('NFKD', s)
                       if x in string.ascii_letters or x in string.digits).lower()
    except TypeError:
        return s


class ViewlyricsSource(BaseLyricSourcePlugin):
    def __init__(self):
        BaseLyricSourcePlugin.__init__(self, id='viewlyrics', name='ViewLyrics')

    def do_search(self, metadata):
        # type: (osdlyrics.metadata.Metadata) -> List[SearchResult]
        if metadata.title:
            title = metadata.title
        else:
            title = ''
        if metadata.artist:
            artist = metadata.artist
        else:
            artist = ''

        result = []
        page = 0
        pagesleft = 1
        while(pagesleft > 0):
            pageresult, pagesleft = self.real_search(title, artist, page)
            result += pageresult
            page += 1

        # Remove non-lrc (plain text) results, they cannot be displayed by
        # OSDLyrics for now
        result = [r for r in result if r._downloadinfo.endswith('.lrc')]

        # Prioritize results whose artist matches
        if metadata.artist and metadata.title:
            n_artist = normalize_str(artist)

            def res_has_same_artist(result):
                return normalize_str(result._artist) == n_artist
            result.sort(key=res_has_same_artist, reverse=True)

        return result

    def real_search(self, title='', artist='', page=0):
        query = VIEWLYRICS_QUERY_FORM
        query = query.replace('%title', title)
        query = query.replace('%artist', artist)
        query = query.replace('%etc', ' client="MiniLyrics" RequestPage=\'%d\'' % page)  # Needs real RequestPage
        query = query.encode('utf-8')

        queryhash = hashlib.md5()
        queryhash.update(query)
        queryhash.update(VIEWLYRICS_KEY)

        masterquery = b'\2\0\4\0\0\0' + queryhash.digest() + query

        url = VIEWLYRICS_HOST + VIEWLYRICS_SEARCH_URL
        status, content = http_download(url=url,
                                        method='POST',
                                        params=masterquery,
                                        proxy=get_proxy_settings(self.config_proxy))

        if status < 200 or status >= 400:
            raise http.client.HTTPException(status, '')

        contentbytes = bytearray(content)
        codekey = contentbytes[1]
        deccontent = bytes(map(codekey.__xor__, contentbytes[22:]))

        root = xet.fromstring(deccontent)  # tagName == 'return'
        pagesleft = int(next((v for k, v in root.items() if k.lower() == 'PageCount'.lower()), 0))
        result = [
            SearchResult(
                title=entry.get('title', ''),
                artist=entry.get('artist', ''),
                album=entry.get('album', ''),
                sourceid=self.id,
                downloadinfo=VIEWLYRICS_BASE_LRC_URL + entry.get('link'),
            )
            for entry in root.findall('fileinfo[@link]')
        ]
        return result, (pagesleft - page)

    def do_download(self, downloadinfo):
        # type: (Any) -> bytes
        # downloadinfo is what you set in SearchResult
        status, content = http_download(url=downloadinfo,
                                        proxy=get_proxy_settings(self.config_proxy))
        if status < 200 or status >= 400:
            raise http.client.HTTPException(status, '')
        return content


if __name__ == '__main__':
    viewlyrics = ViewlyricsSource()
    viewlyrics._app.run()
