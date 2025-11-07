# -*- coding: utf-8 -*-

'''
    filmy_hu Add-on
    Copyright (C) 2025 heg, vargalex

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import sys
from resources.lib.indexers import navigator

if sys.version_info[0] == 3:
    from urllib.parse import parse_qsl
else:
    from urlparse import parse_qsl

params = dict(parse_qsl(sys.argv[2].replace('?', '')))

action = params.get('action')
url = params.get('url')

img_url = params.get('img_url')
hun_title = params.get('hun_title')
content = params.get('content')
year = params.get('year')
card_type = params.get('card_type')
imdb = params.get('imdb')
season_title = params.get('season_title')

if action is None:
    navigator.navigator().root()

elif action == 'get_categories':
    navigator.navigator().getCategories(url)

elif action == 'get_years':
    navigator.navigator().getYears(url)


elif action == 'get_items':
    navigator.navigator().getItems(url, img_url, hun_title, year, card_type, imdb)


elif action == 'extract_movie':
    navigator.navigator().extractMovie(url, img_url, hun_title, year, card_type, imdb)


elif action == 'extract_seasons':
    navigator.navigator().extractSeasons(url, img_url, hun_title, year, card_type, imdb, season_title, content)

elif action == 'extract_episodes':
    navigator.navigator().extractEpisodes(url, img_url, hun_title, year, card_type, imdb, season_title, content)

elif action == 'ext_ep_video_link':
    navigator.navigator().extEpVid(url, img_url, hun_title, year, card_type, imdb, season_title, content)


elif action == 'playmovie':
    navigator.navigator().playMovie(url)

elif action == 'newsearch':
    navigator.navigator().doSearch()