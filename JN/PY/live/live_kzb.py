# -*- coding: utf-8 -*-
# @Author  : Doubebly
# @Time    : 2025/5/22 20:23

# -*- coding: utf-8 -*-
# @Author  : Doubebly
# @Time    : 2025/5/19 21:19

import sys
import requests
import base64
import os
import time
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return "Kzb"

    def init(self, extend):
        self.extend = extend
        self.ext_time = 600
        self.cache_path = '/storage/emulated/0/TV/Cache_Kzb'
        if not os.path.exists(self.cache_path):
            os.mkdir(self.cache_path, 0o755)
        pass

    def getDependence(self):
        return []

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass


    def liveContent(self, url):
        cache_data = self.cache_get('live_kzb')
        if cache_data != 'False':
            return cache_data
        keys = ['578', '579', '580', '581', '582', '583', '584', '585', '586', '587', '588', '589', '590', '591', '592', '593', '594', '595', '596', '597', '598', '599', '600', '601', '602', '603', '604', '605', '606', '607', '608', '609', '610', '611', '612', '613', '614', '615', '616', '617', '618', '619', '620', '621', '622', '623', '624']
        values = {}
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36 EdgA/136.0.0.0"
        }
        response = requests.get(bytes.fromhex(self.extend).decode(), params={'liveType': "0",'deviceType': "1"}, headers=headers)
        for i in response.json()['list']:
            values[str(i['id'])] = i
        tv_list = ['#EXTM3U']
        for ii in keys:
            c = values[ii]
            name = c['play_source_name']
            group_name = '卫视频道' if '卫视' in name else '央视频道'
            tv_list.append(f'#EXTINF:-1 tvg-id="" tvg-name="" tvg-logo="https://logo.doube.eu.org/{name}.png" group-title="{group_name}",{name}')
            tv_list.append(c['play_source_url'])
        data = '\n'.join(tv_list)
        self.cache_set('live_kzb', data)
        return data

    def homeContent(self, filter):
        return {}

    def homeVideoContent(self):
        return {}

    def categoryContent(self, cid, page, filter, ext):
        return {}

    def detailContent(self, did):
        return {}

    def searchContent(self, key, quick, page='1'):
        return {}

    def searchContentPage(self, keywords, quick, page):
        return {}

    def playerContent(self, flag, pid, vipFlags):
        return {}

    def localProxy(self, params):
        _fun = params.get('fun', None)
        _type = params.get('type', None)
        if _fun is not None:
            fun = getattr(self, f'fun_{_fun}')
            return fun(params)
        return [302, "text/plain", None, {'Location': 'https://sf1-cdn-tos.huoshanstatic.com/obj/media-fe/xgplayer_doc_video/mp4/xgplayer-demo-720p.mp4'}]

    def destroy(self):
        return '正在Destroy'

    def b64encode(self, data):
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')

    def b64decode(self, data):
        return base64.b64decode(data.encode('utf-8')).decode('utf-8')


    def cache_get(self, key):
        t = time.time()
        path = self.cache_getkey(key)
        if not os.path.exists(path):
            return 'False'
        if t - os.path.getmtime(path) > self.ext_time:
            return 'False'
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()
        return data

    def cache_set(self, key, data):
        path = self.cache_getkey(key)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)
        return True

    def cache_getkey(self, key):
        return self.cache_path + '/' + key + '.png'

if __name__ == '__main__':
    pass




