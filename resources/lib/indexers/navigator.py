# -*- coding: utf-8 -*-

'''
    filmy_hu Addon
    Copyright (C) 2023 heg, vargalex

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

import os, sys, re, xbmc, xbmcgui, xbmcplugin, xbmcaddon, locale, base64
from bs4 import BeautifulSoup
import requests
import urllib.parse
import resolveurl as urlresolver
from resources.lib.modules.utils import py2_decode, py2_encode
from resources.lib.modules import xmltodict

from urllib.parse import urljoin, urlparse, parse_qs
import struct
import random
import string

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

version = xbmcaddon.Addon().getAddonInfo('version')
kodi_version = xbmc.getInfoLabel('System.BuildVersion')
base_log_info = f'filmy.hu | v{version} | Kodi: {kodi_version[:5]}'

xbmc.log(f'{base_log_info}', xbmc.LOGINFO)

base_url = 'https://filmy.hu'

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'referer': f'{base_url}/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

if sys.version_info[0] == 3:
    from xbmcvfs import translatePath
    from urllib.parse import urlparse, quote_plus
else:
    from xbmc import translatePath
    from urlparse import urlparse
    from urllib import quote_plus

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
        except:
            try:
                locale.setlocale(locale.LC_ALL, "")
            except:
                pass
        self.base_path = py2_decode(translatePath(xbmcaddon.Addon().getAddonInfo('profile')))

    def root(self):
        self.addDirectoryItem("Filmek & Sorozatok", f"get_items&url={base_url}/", '', 'DefaultFolder.png')
        self.addDirectoryItem("Sorozatok", f"get_items&url={base_url}/sorozatok", '', 'DefaultFolder.png')
        self.addDirectoryItem("Rajzfilmek", f"get_items&url={base_url}/category/39", '', 'DefaultFolder.png')
        self.addDirectoryItem("Kategóriák", "get_categories", '', 'DefaultFolder.png')
        self.addDirectoryItem("Év szerint", "get_years", '', 'DefaultFolder.png')
        self.addDirectoryItem("Keresés", "newsearch", '', 'DefaultFolder.png')
        self.endDirectory()

    def getCategories(self, url):
        jsonData = {
          "categorys": [
            {
              "genre": "akció",
              "url": "https://filmy.hu/category/28"
            },
            {
              "genre": "thriller",
              "url": "https://filmy.hu/category/37"
            },
            {
              "genre": "horror",
              "url": "https://filmy.hu/category/32"
            },
            {
              "genre": "vígjáték",
              "url": "https://filmy.hu/category/27"
            },
            {
              "genre": "kaland",
              "url": "https://filmy.hu/category/29"
            },
            {
              "genre": "családi",
              "url": "https://filmy.hu/category/38"
            },
            {
              "genre": "animáció",
              "url": "https://filmy.hu/category/39"
            },
            {
              "genre": "dráma",
              "url": "https://filmy.hu/category/36"
            },
            {
              "genre": "misztikus",
              "url": "https://filmy.hu/category/42"
            },
            {
              "genre": "anime",
              "url": "https://filmy.hu/category/48"
            },
            {
              "genre": "zene",
              "url": "https://filmy.hu/category/44"
            },
            {
              "genre": "feliratos",
              "url": "https://filmy.hu/category/55"
            },
            {
              "genre": "sci-fi",
              "url": "https://filmy.hu/category/33"
            },
            {
              "genre": "fantasy",
              "url": "https://filmy.hu/category/43"
            }
          ]
        }
        
        for movie in jsonData['categorys']:
            category_name = movie['genre']
            category_url = movie['url']
            
            self.addDirectoryItem(f"{category_name}", f'get_items&url={category_url}', '', 'DefaultFolder.png')
        
        self.endDirectory('movies')

    def getYears(self, url):
        from datetime import datetime

        current_year = datetime.now().year
        years = list(range(current_year, 1909, -1))
        
        for year_nums in years:
            self.addDirectoryItem(f"{year_nums}", f'get_items&url={base_url}/videos/{year_nums}', '', 'DefaultFolder.png')

        self.endDirectory('movies')

    def getItems(self, url, img_url, hun_title, year, card_type, imdb):
        try:
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.text, 'html.parser')
            
            movie_cards = soup.find_all('div', class_='card tip')
            
            for card in movie_cards:
                
                if re.search(r'SOROZAT', str(card)):
                    card_type = 'Sorozat'
                else:
                    card_type = 'Film'
                
                hun_title = card.find('div', class_='card-title').a.text.strip()
                img_url = ''+base_url+'' + card.find('img')['src']
                card_link = ''+base_url+'' + card.find('a')['href']
            
                imdb_element = card.find('small', class_='float-right text-white font-weight-normal')
                if imdb_element:
                    imdb_text = imdb_element.get_text(strip=True)
                    imdb = imdb_text.split()[-1]
                else:
                    imdb = 'N/A'
                
                date_year_element = card.find('small', class_='float-right font-weight-normal')
                year = date_year_element.text.strip() if date_year_element else 'N/A'
                
                
                if card_type == 'Sorozat':
                    self.addDirectoryItem(f'[B] {card_type} | {hun_title}| [COLOR yellow]{imdb}[/COLOR][/B]', f'extract_seasons&url={card_link}&img_url={img_url}&hun_title={hun_title}&year={year}&card_type={card_type}&imdb={imdb}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title})
                
                else:
                    self.addDirectoryItem(f'[B] {card_type} | {hun_title}| [COLOR yellow]{imdb}[/COLOR][/B]', f'extract_movie&url={card_link}&img_url={img_url}&hun_title={hun_title}&year={year}&card_type={card_type}&imdb={imdb}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title})
        except AttributeError:
            xbmc.log(f'{base_log_info}| getItems | nincs találat', xbmc.LOGINFO)
            notification = xbmcgui.Dialog()
            notification.notification("filmy.hu", "nincs találat", time=5000)            
        
        
        try:
            #----for next page stuff
            get_resp_url_page = page.url
            
            pagination = soup.find('ul', class_='pagination')
            current_page_item = pagination.find('li', class_='page-item active') if pagination else None
            
            next_page_link = None
            if current_page_item:
                next_page_item = current_page_item.find_next_sibling('li', class_='page-item')
                next_page_link = next_page_item.find('a')['href'] if next_page_item else None
            
            if not next_page_link:
                next_page_tag = soup.find('a', class_='page-link', string='›')
                next_page_link = next_page_tag['href'] if next_page_tag else None
            
            if next_page_link:
                if next_page_link.startswith('?'):
                    next_page_link = urljoin(get_resp_url_page, next_page_link)
                elif not next_page_link.startswith(('http://', 'https://')):
                    base_url_x = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(initial_url))
                    next_page_link = urljoin(base_url_x, next_page_link)
                self.addDirectoryItem('[I]Következő oldal[/I]', f'get_items&url={quote_plus(next_page_link)}', '', 'DefaultFolder.png')
        
        except AttributeError:
            xbmc.log(f'{base_log_info}| getItems | next_page_link | csak egy oldal található', xbmc.LOGINFO)
        
        self.endDirectory('movies')

    def extractMovie(self, url, img_url, hun_title, year, card_type, imdb):
        html_soup_2 = requests.get(url, headers=headers)
        soup_2 = BeautifulSoup(html_soup_2.text, 'html.parser')
        
        content = soup_2.find('p', class_='mt-2 mb-5 col-12').get_text(strip=True)        
        
        iframe = soup_2.find('iframe')
        if iframe:
            iframe_src = iframe.get('src')
        
            if iframe_src and not iframe_src.startswith('https://'):
                iframe_src = 'https:' + iframe_src
        
            self.addDirectoryItem(f'[B]{hun_title} - {year}| [COLOR yellow]{imdb}[/COLOR][/B]', f'playmovie&url={quote_plus(iframe_src)}&img_url={img_url}&hun_title={hun_title}&year={year}', img_url, 'DefaultMovies.png', isFolder=False, meta={'title': hun_title, 'plot': content})
        
        self.endDirectory('movies')

    def extractSeasons(self, url, img_url, hun_title, year, card_type, imdb, season_title, content):
        html_soup_2 = requests.get(url, headers=headers)
        soup = BeautifulSoup(html_soup_2.text, 'html.parser')
        
        content = soup.find('p', class_='mt-2 mb-5 col-12').get_text(strip=True)
        season_section = soup.find('div', string='Évad:').find_parent('div')
        season_links = season_section.find_all('a')
        
        for season in season_links:
            season_title = season['title']
            season_link = ''+base_url+'' + season['href']
            
            self.addDirectoryItem(f'[B]{season_title}| [COLOR yellow]{imdb}[/COLOR][/B]', f'extract_episodes&url={quote_plus(season_link)}&img_url={img_url}&hun_title={hun_title}&year={year}&card_type={card_type}&imdb={imdb}&season_title={season_title}&content={content}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title, 'plot': content})

        self.endDirectory('movies')

    def extractEpisodes(self, url, img_url, hun_title, year, card_type, imdb, season_title, content, ep_title):
        html_soup_2 = requests.get(url, headers=headers)
        soup_2 = BeautifulSoup(html_soup_2.text, 'html.parser')

        episodes_section = soup_2.find('div', string='Rész:').find_parent('div')
        episodes_links = episodes_section.find_all('a')
        
        for episodes in episodes_links:
            ep_title = episodes['title']
            episode_link = ''+base_url+'' + episodes['href']
            
            self.addDirectoryItem(f'[B]{ep_title}[/B]', f'ext_ep_video_link&url={quote_plus(episode_link)}&img_url={img_url}&hun_title={hun_title}&year={year}&card_type={card_type}&imdb={imdb}&season_title={season_title}&content={content}&ep_title={ep_title}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': ep_title, 'plot': content})

        self.endDirectory('series')

    def extEpVid(self, url, img_url, hun_title, year, card_type, imdb, season_title, content, ep_title):
        html_soup_2 = requests.get(url, headers=headers)
        soup_2 = BeautifulSoup(html_soup_2.text, 'html.parser')
        
        iframe = soup_2.find('iframe')
        if iframe:
            iframe_src = iframe.get('src')
        
            if iframe_src and not iframe_src.startswith('https://'):
                iframe_src = 'https:' + iframe_src

            self.addDirectoryItem(f'[B]{ep_title} - {hun_title}| [COLOR yellow]{imdb}[/COLOR][/B]', f'playmovie&url={quote_plus(iframe_src)}&img_url={img_url}&hun_title={hun_title}&year={year}&card_type={card_type}&imdb={imdb}&season_title={season_title}&content={content}&ep_title={ep_title}', img_url, 'DefaultMovies.png', isFolder=False, meta={'title': ep_title, 'plot': content})

        self.endDirectory('series')

    def playMovie(self, url):
        if re.search('.*videa.*', url):
            
            STATIC_SECRET = 'xHb0ZvME5q8CBcoQi6AngerDu3FGO9fkUlwPmLVY_RTzj2hJIS4NasXWKy1td7p'
            
            def rc4(cipher_text, key):
                def compat_ord(c):
                    return c if isinstance(c, int) else ord(c)
            
                res = b''
            
                key_len = len(key)
                S = list(range(256))
            
                j = 0
                for i in range(256):
                    j = (j + S[i] + ord(key[i % key_len])) % 256
                    S[i], S[j] = S[j], S[i]
            
                i = 0
                j = 0
                for m in range(len(cipher_text)):
                    i = (i + 1) % 256
                    j = (j + S[i]) % 256
                    S[i], S[j] = S[j], S[i]
                    k = S[(S[i] + S[j]) % 256]
                    res += struct.pack('B', k ^ compat_ord(cipher_text[m]))
            
                if sys.version_info[0] == 3:
                    return res.decode()
                else:
                    return res
            
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            }
            
            session = requests.Session()
            response = session.get(url, cookies={"session_adult": "1"})
            
            video_page = response.text
            
            if '/player' in url:
                player_url = url
                player_page = video_page
            else:
                player_url = re.search(r'<iframe.*?src="(/player\?[^"]+)"', video_page).group(1)
                player_url = urljoin(url, player_url)
                response = session.get(player_url)
                player_page = response.text
            
            nonce = re.search(r'_xt\s*=\s*"([^"]+)"', player_page).group(1)
            
            l = nonce[:32]
            s = nonce[32:]
            result = ''
            for i in range(0, 32):
                result += s[i - (STATIC_SECRET.index(l[i]) - 31)]
            
            query = parse_qs(urlparse(player_url).query)
            
            random_seed = ''
            for i in range(8):
                random_seed += random.choice(string.ascii_letters + string.digits)
            
            _s = random_seed
            _t = result[:16]
            if 'f' in query or 'v' in query:
                _param = f'f={query["f"][0]}' if 'f' in query else f'v={query["v"][0]}'
            response = session.get(f'https://videa.hu/player/xml?platform=desktop&{_param}&_s={_s}&_t={_t}')
            
            videaXml = response.text
            if not videaXml.startswith('<?xml'):
                key = result[16:] + random_seed + response.headers['x-videa-xs']
                videaXml = rc4(base64.b64decode(videaXml), key)            
            
            try:        
                videaData = xmltodict.parse(videaXml)

                sources = videaData["videa_video"]["video_sources"]["video_source"]
                if isinstance(sources, list):
                    sorted_sources = sorted(sources, key=lambda x: int(x["@width"]), reverse=True)
                else:
                    sorted_sources = [sources]

                selected_source = sorted_sources[0]
                s_format = selected_source["@name"]
                s_url = selected_source["#text"]
                s_exp = selected_source["@exp"]

                hash_key = "hash_value_" + s_format
                hash_x_key = videaData["videa_video"]["hash_values"][hash_key]
                video_url = f'https:{s_url}?md5={hash_x_key}&expires={s_exp}'
                
                xbmc.log(f'{base_log_info}| playMovie | video_url: {video_url}', xbmc.LOGINFO)

                play_item = xbmcgui.ListItem(path=video_url)

                try:
                    subtitles = videaData["videa_video"]["subtitles"]["subtitle"]
                    subtitle_urls = []
            
                    if isinstance(subtitles, list):
                        for subtitle in subtitles:
                            subtitle_url = 'https:' + subtitle["@src"]
                            subtitle_urls.append(subtitle_url)
                    else:
                        subtitle_url = 'https:' + subtitles["@src"]
                        subtitle_urls.append(subtitle_url)

                    play_item.setSubtitles(subtitle_urls)
                    xbmc.log(f'{base_log_info}| playMovie | subtitles: {subtitle_urls}', xbmc.LOGINFO)
                except KeyError:
                    xbmc.log(f'{base_log_info}| playMovie | No subtitles found', xbmc.LOGINFO)

                xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
                
            except Exception as e:
                xbmc.log(f'{base_log_info}| playMovie | Error: {str(e)}', xbmc.LOGINFO)
                notification = xbmcgui.Dialog()
                notification.notification("filmy.hu", "Törölt tartalom", time=5000)            
            ###
        
        else:
            try:
                direct_url = urlresolver.resolve(url)
                
                xbmc.log(f'{base_log_info}| playMovie (else) | direct_url: {direct_url}', xbmc.LOGINFO)
                play_item = xbmcgui.ListItem(path=direct_url)
                xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
            except:
                xbmc.log(f'{base_log_info}| playMovie | name: No video sources found', xbmc.LOGINFO)
                notification = xbmcgui.Dialog()
                notification.notification("filmy.hu", "Törölt tartalom", time=5000)

    def doSearch(self):
        search_text = self.getSearchText()
        if search_text != '':
            if not os.path.exists(self.base_path):
                os.mkdir(self.base_path)
            url = f"{base_url}/?search={search_text}"
            self.getItems(url, '', '', '', '', '')

    def getSearchText(self):
        search_text = ''
        keyb = xbmc.Keyboard('', u'Add meg a keresend\xF5 film c\xEDm\xE9t')
        keyb.doModal()
        if keyb.isConfirmed():
            search_text = keyb.getText()
        return search_text

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = f'{sysaddon}?action={query}' if isAction else query
        if thumb == '':
            thumb = icon
        cm = []
        if queue:
            cm.append((queueMenu, f'RunPlugin({sysaddon}?action=queueItem)'))
        if not context is None:
            cm.append((context[0].encode('utf-8'), f'RunPlugin({sysaddon}?action={context[1]})'))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': banner})
        if Fanart is None:
            Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if not isFolder:
            item.setProperty('IsPlayable', 'true')
        if not meta is None:
            item.setInfo(type='Video', infoLabels=meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)