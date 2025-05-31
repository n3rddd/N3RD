# -*- coding: utf-8 -*-
# @Author  : Doubebly
# @Time    : 2025/5/19 21:19

import sys
import requests
import base64
sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    def getName(self):
        return "BeeSport"

    def init(self, extend):
        pass

    def getDependence(self):
        return []

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass


    def liveContent(self, url):
        data_list = [{'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/TNT_SPORTS_1.png', 'group-title': 'BeeSport', 'name': 'TNT SPORTS 1', 'fun': 'beesport', 'pid': 'TNT_Sports_1'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/TNT_SPORTS_2.png', 'group-title': 'BeeSport', 'name': 'TNT SPORTS 2', 'fun': 'beesport', 'pid': 'TNT_Sports_2'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/TNT_SPORTS_3.png', 'group-title': 'BeeSport', 'name': 'TNT SPORTS 3', 'fun': 'beesport', 'pid': 'TNT_Sports_3'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/TNT_SPORTS_4.png', 'group-title': 'BeeSport', 'name': 'TNT SPORTS 4', 'fun': 'beesport', 'pid': 'TNT_Sports_4'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SKY_SPORTS_FOOTBALL.png', 'group-title': 'BeeSport', 'name': 'SKY SPORTS FOOTBALL', 'fun': 'beesport', 'pid': 'Sky_Sports_Football_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SKY_SPORTS_MAIN_EVENT.png', 'group-title': 'BeeSport', 'name': 'SKY SPORTS MAIN EVENT', 'fun': 'beesport', 'pid': 'Sky_Sports_Main_Event'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SKY_SPORTS_PREMIER_LEAGUE.png', 'group-title': 'BeeSport', 'name': 'SKY SPORTS PREMIER LEAGUE', 'fun': 'beesport', 'pid': 'Sky_Sports_Premier_League'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SKY_SPORTS_ACTION.png', 'group-title': 'BeeSport', 'name': 'SKY SPORTS ACTION', 'fun': 'beesport', 'pid': 'Sky_Sports_Action_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SKY_SPORTS_MIX.png', 'group-title': 'BeeSport', 'name': 'SKY SPORTS MIX', 'fun': 'beesport', 'pid': 'Sky_Sports_Mix_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SKY_SPORTS_ARENA.png', 'group-title': 'BeeSport', 'name': 'SKY SPORTS ARENA', 'fun': 'beesport', 'pid': 'Sky_Sports_Arena_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SKY_SPORTS_NEWS.png', 'group-title': 'BeeSport', 'name': 'SKY SPORTS NEWS', 'fun': 'beesport', 'pid': 'Sky_Sports_News_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SKY_SPORTS_CRICKET.png', 'group-title': 'BeeSport', 'name': 'SKY SPORTS CRICKET', 'fun': 'beesport', 'pid': 'Sky_Sports_Cricket_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Sky_Sports_Tennis.png', 'group-title': 'BeeSport', 'name': 'Sky Sports Tennis', 'fun': 'beesport', 'pid': 'Sky_Sports_Tennis'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SKY_SPORTS_F1.png', 'group-title': 'BeeSport', 'name': 'SKY SPORTS F1', 'fun': 'beesport', 'pid': 'Sky_Sports_F1_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SKY_SPORTS_GOLF.png', 'group-title': 'BeeSport', 'name': 'SKY SPORTS GOLF', 'fun': 'beesport', 'pid': 'Sky_Sports_Golf_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SKY_SPORTS_RACING.png', 'group-title': 'BeeSport', 'name': 'SKY SPORTS RACING', 'fun': 'beesport', 'pid': 'Sky_Sports_Racing_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Sky_Sports_Darts.png', 'group-title': 'BeeSport', 'name': 'Sky Sports Darts', 'fun': 'beesport', 'pid': 'Sky_Sports_Darts'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/BEIN_SPORTS_USA.png', 'group-title': 'BeeSport', 'name': 'BEIN SPORTS USA', 'fun': 'beesport', 'pid': 'Bein_Sports_USA_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/TENNIS_CHANNEL.png', 'group-title': 'BeeSport', 'name': 'TENNIS CHANNEL', 'fun': 'beesport', 'pid': 'Tennis_Channel_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/LALIGA_TV_HD.png', 'group-title': 'BeeSport', 'name': 'LALIGA TV HD', 'fun': 'beesport', 'pid': 'La_Liga_TV_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/HBO_1.png', 'group-title': 'BeeSport', 'name': 'HBO 1', 'fun': 'beesport', 'pid': 'HBO_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/HBO_2.png', 'group-title': 'BeeSport', 'name': 'HBO 2', 'fun': 'beesport', 'pid': 'HBO_2_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Discovery_Channel.png', 'group-title': 'BeeSport', 'name': 'Discovery Channel', 'fun': 'beesport', 'pid': 'Discovery_Channel_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Discovery_Life.png', 'group-title': 'BeeSport', 'name': 'Discovery Life', 'fun': 'beesport', 'pid': 'Discovery_Life_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Cinemax_West.png', 'group-title': 'BeeSport', 'name': 'Cinemax West', 'fun': 'beesport', 'pid': 'Cinemax_West_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Great_Movies.png', 'group-title': 'BeeSport', 'name': 'Great Movies', 'fun': 'beesport', 'pid': 'UK_Great_Movies_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Sky_Cinema_Comedy.png', 'group-title': 'BeeSport', 'name': 'Sky Cinema Comedy', 'fun': 'beesport', 'pid': 'UK_Sky_Cinema_Comedy_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Sky_Cinema_Family.png', 'group-title': 'BeeSport', 'name': 'Sky Cinema Family', 'fun': 'beesport', 'pid': 'UK_Sky_Cinema_Family_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Cartoon_Network.png', 'group-title': 'BeeSport', 'name': 'Cartoon Network', 'fun': 'beesport', 'pid': 'UK_Cartoon_Network_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Virgin_2.png', 'group-title': 'BeeSport', 'name': 'Virgin 2', 'fun': 'beesport', 'pid': 'UK_Virgin_2'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Virgin_3.png', 'group-title': 'BeeSport', 'name': 'Virgin 3', 'fun': 'beesport', 'pid': 'UK_Virgin_3'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Virgin_1.png', 'group-title': 'BeeSport', 'name': 'Virgin 1', 'fun': 'beesport', 'pid': 'UK_Virgin_1'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Bein_Sports_English_2.png', 'group-title': 'BeeSport', 'name': 'Bein Sports English 2', 'fun': 'beesport', 'pid': 'Bein_Sports_English_2_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SuperSport_Premier_League.png', 'group-title': 'BeeSport', 'name': 'SuperSport Premier League', 'fun': 'beesport', 'pid': 'SuperSport_Premier_League_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SuperSport_LaLiga.png', 'group-title': 'BeeSport', 'name': 'SuperSport LaLiga', 'fun': 'beesport', 'pid': 'SuperSport_LaLiga_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SuperSport_Action.png', 'group-title': 'BeeSport', 'name': 'SuperSport Action', 'fun': 'beesport', 'pid': 'SuperSport_Action_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SuperSport_Blitz.png', 'group-title': 'BeeSport', 'name': 'SuperSport Blitz', 'fun': 'beesport', 'pid': 'SuperSport_Blitz_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SuperSport_Cricket.png', 'group-title': 'BeeSport', 'name': 'SuperSport Cricket', 'fun': 'beesport', 'pid': 'SuperSport_Cricket_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SuperSport_Football.png', 'group-title': 'BeeSport', 'name': 'SuperSport Football', 'fun': 'beesport', 'pid': 'SuperSport_Football_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SuperSport_Golf.png', 'group-title': 'BeeSport', 'name': 'SuperSport Golf', 'fun': 'beesport', 'pid': 'SuperSport_Golf_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SuperSport_Rugby.png', 'group-title': 'BeeSport', 'name': 'SuperSport Rugby', 'fun': 'beesport', 'pid': 'SuperSport_Rugby_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/SuperSport_Tennis.png', 'group-title': 'BeeSport', 'name': 'SuperSport Tennis', 'fun': 'beesport', 'pid': 'SuperSport_Tennis_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Variety_1.png', 'group-title': 'BeeSport', 'name': 'Variety 1', 'fun': 'beesport', 'pid': 'Variety_1_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Variety_2.png', 'group-title': 'BeeSport', 'name': 'Variety 2', 'fun': 'beesport', 'pid': 'Variety_2_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Variety_3.png', 'group-title': 'BeeSport', 'name': 'Variety 3', 'fun': 'beesport', 'pid': 'Variety_3_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Variety_4.png', 'group-title': 'BeeSport', 'name': 'Variety 4', 'fun': 'beesport', 'pid': 'Variety_4_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Eurosport_1.png', 'group-title': 'BeeSport', 'name': 'Eurosport 1', 'fun': 'beesport', 'pid': 'Eurosport_1_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Eurosport_2.png', 'group-title': 'BeeSport', 'name': 'Eurosport 2', 'fun': 'beesport', 'pid': 'Eurosport_2_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Premier_Sports_1.png', 'group-title': 'BeeSport', 'name': 'Premier Sports 1', 'fun': 'beesport', 'pid': 'Premier_Sports_1'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Premier_Sports_2.png', 'group-title': 'BeeSport', 'name': 'Premier Sports 2', 'fun': 'beesport', 'pid': 'Premier_Sports_2'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Golf_Channel.png', 'group-title': 'BeeSport', 'name': 'Golf Channel', 'fun': 'beesport', 'pid': 'Golf_Channel_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/MLB_Network.png', 'group-title': 'BeeSport', 'name': 'MLB Network', 'fun': 'beesport', 'pid': 'MLB_Network_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/NBA_TV.png', 'group-title': 'BeeSport', 'name': 'NBA TV', 'fun': 'beesport', 'pid': 'NBA_TV_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/NFL_Network.png', 'group-title': 'BeeSport', 'name': 'NFL Network', 'fun': 'beesport', 'pid': 'NFL_Network_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/NFL_REDZONE.png', 'group-title': 'BeeSport', 'name': 'NFL REDZONE', 'fun': 'beesport', 'pid': 'NFL_REDZONE_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/NHL_Network.png', 'group-title': 'BeeSport', 'name': 'NHL Network', 'fun': 'beesport', 'pid': 'NHL_Network_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/WWE.png', 'group-title': 'BeeSport', 'name': 'WWE', 'fun': 'beesport', 'pid': 'WWE_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Willow_Cricket.png', 'group-title': 'BeeSport', 'name': 'Willow Cricket', 'fun': 'beesport', 'pid': 'Willow_Cricket_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Willow_Extra.png', 'group-title': 'BeeSport', 'name': 'Willow Extra', 'fun': 'beesport', 'pid': 'Willow_Extra_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/World_Fishing_Network.png', 'group-title': 'BeeSport', 'name': 'World Fishing Network', 'fun': 'beesport', 'pid': 'World_Fishing_Network_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/ESPN.png', 'group-title': 'BeeSport', 'name': 'ESPN', 'fun': 'beesport', 'pid': 'ESPN_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/ESPN_2.png', 'group-title': 'BeeSport', 'name': 'ESPN 2', 'fun': 'beesport', 'pid': 'ESPN_2_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/ESPN_News.png', 'group-title': 'BeeSport', 'name': 'ESPN News', 'fun': 'beesport', 'pid': 'ESPN_News_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/ESPN_U.png', 'group-title': 'BeeSport', 'name': 'ESPN U', 'fun': 'beesport', 'pid': 'ESPN_U_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/ITV_1.png', 'group-title': 'BeeSport', 'name': 'ITV 1', 'fun': 'beesport', 'pid': 'ITV_1'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/ITV_2.png', 'group-title': 'BeeSport', 'name': 'ITV 2', 'fun': 'beesport', 'pid': 'ITV_2'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/ITV_3.png', 'group-title': 'BeeSport', 'name': 'ITV 3', 'fun': 'beesport', 'pid': 'ITV_3'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/ITV_4.png', 'group-title': 'BeeSport', 'name': 'ITV 4', 'fun': 'beesport', 'pid': 'ITV_4'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/MUTV.png', 'group-title': 'BeeSport', 'name': 'MUTV', 'fun': 'beesport', 'pid': 'MUTV_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/LFC_TV.png', 'group-title': 'BeeSport', 'name': 'LFC TV', 'fun': 'beesport', 'pid': 'LFC_TV_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/FOX_NEWS.png', 'group-title': 'BeeSport', 'name': 'FOX NEWS', 'fun': 'beesport', 'pid': 'FOX_NEWS_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/ACC_Network.png', 'group-title': 'BeeSport', 'name': 'ACC Network', 'fun': 'beesport', 'pid': 'ACC_Network_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Fight_Network.png', 'group-title': 'BeeSport', 'name': 'Fight Network', 'fun': 'beesport', 'pid': 'Fight_Network_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/CBS_Sports_Network.png', 'group-title': 'BeeSport', 'name': 'CBS Sports Network', 'fun': 'beesport', 'pid': 'CBS_Sports_Network_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/CNBC.png', 'group-title': 'BeeSport', 'name': 'CNBC', 'fun': 'beesport', 'pid': 'CNBC_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Fox_Sports_1.png', 'group-title': 'BeeSport', 'name': 'Fox Sports 1', 'fun': 'beesport', 'pid': 'Fox_Sports_1_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Fox_Sports_2.png', 'group-title': 'BeeSport', 'name': 'Fox Sports 2', 'fun': 'beesport', 'pid': 'Fox_Sports_2_Live_TV'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/Nat_Geo_Wild_HD.png', 'group-title': 'BeeSport', 'name': 'Nat Geo Wild HD', 'fun': 'beesport', 'pid': 'Nat_Geo_Wild_HD'}, {'tvg-id': '', 'tvg-name': '', 'tvg-logo': 'https://logo.doube.eu.org/beesport/ABC_Channel.png', 'group-title': 'BeeSport', 'name': 'ABC Channel', 'fun': 'beesport', 'pid': 'ABC'}]

        tv_list = ['#EXTM3U']
        for i in data_list:
            tvg_id = i['tvg-id']
            tvg_name = i['tvg-name']
            tvg_logo = i['tvg-logo']
            group_name = i['group-title']
            name = i['name']
            fun = i['fun']
            pid = i['pid']
            tv_list.append(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{tvg_name}" tvg-logo="{tvg_logo}" group-title="{group_name}",{name}')
            tv_list.append(f'{self.getProxyUrl()}&fun={fun}&pid={pid}&Author=Doubebly&TG=t.me/doubebly001')

        return '\n'.join(tv_list)

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


    def fun_beesport(self, params):
        pid = params['pid']
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://beesport.net',
            'referer': 'https://beesport.net/live-tv',
        }

        json_data = {
            'channel': f'https://live_tv.starcdnup.com/{pid}/index.m3u8',
        }
        try:
            response = requests.post('https://beesport.net/authorize-channel', headers=headers, json=json_data)
            url = response.json()['channels'][0]
            return [302, "text/plain", None, {'Location': url}]
        except Exception as e:
            return [302, "text/plain", None, {'Location': 'https://sf1-cdn-tos.huoshanstatic.com/obj/media-fe/xgplayer_doc_video/mp4/xgplayer-demo-720p.mp4'}]

    def destroy(self):

        return '正在Destroy'

    def b64encode(self, data):
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')

    def b64decode(self, data):
        return base64.b64decode(data.encode('utf-8')).decode('utf-8')

if __name__ == '__main__':
    pass
