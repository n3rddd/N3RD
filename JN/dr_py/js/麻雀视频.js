var rule = {
author: '道门子弟/2408/第三版',
title: '麻雀视频',
host: 'https://www.mqtv.one',
hostJs: 'js: HOST = pdfh(request(HOST),"ul#leo-pan-li&&a&&href")',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/libs/VodList.api.php?type=tv&page=1',
url: '/libs/VodList.api.php?type=fyclass&page=fypage&rank=&cat=&year=&area=',
filter_url: '',
detailUrl: '',
searchUrl: '/libs/VodList.api.php?search=**',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '电影&剧集&综艺&动漫',
class_url: 'movie&tv&va&ct',
filter_def: {},

isVideo: 'obj/tos',
parse_url: 'https://player.mqtv.cc/fun/?url=',
play_parse: true,
lazy: `js: 
input = {parse: 1, url: rule.parse_url+input, js: '$(".player-btn").click()', parse_extra: '&is_pc=1&custom_regex=' + rule.is_video}
`,

//预处理来自a佬
预处理: `js:
let xrequest = request;
(function() {
    request = function(url, obj) {
        function setCookie() {
            let {cookie} = reqCookie(HOST);
            rule.headers["Cookie"] = cookie;
            return rule.headers
        };
    let result = xrequest(url, obj);
    if (result == "") { result = xrequest(url, {headers: setCookie()} ) };
    return result
    }
})()
`,

limit: 9,
double: false,
推荐: '*',
一级: 'json:data;title;img;remark;url;desc',
二级: `js:
VOD = {};
let ctid = input.match(/.*\\/(\\d+)/)[1];
let detailUrl = HOST+ '/libs/VodInfo.api.php?ctid=' + ctid;
let kdata = JSON.parse(request(detailUrl)).data;
VOD.vod_id = input;
VOD.vod_name = kdata.title;
VOD.type_name = kdata.type;
VOD.vod_pic = kdata.img;
VOD.vod_remarks = kdata.remark;
VOD.vod_year = kdata.year;
VOD.vod_area = kdata.area;
VOD.vod_actor = kdata.actor;
VOD.vod_director = kdata.director;
VOD.vod_content = kdata.title+'_'+kdata.des;
VOD.vod_play_from = kdata.playinfo.map(it => it.cnsite).join('$$$');
let playUrls = [];
kdata.playinfo.forEach((it) => {
let plist = it.player.map(it => it.no + '$' + it.url).join('#');
playUrls.push(plist)
});
VOD.vod_play_url = playUrls.join('$$$')
`,
搜索: 'json:data.vod_all[0].show;*;*;*;*',

filter: {}
}