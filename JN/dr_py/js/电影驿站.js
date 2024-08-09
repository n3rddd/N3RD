var rule = {
author: '小可乐/2408/第一版',
title: '电影驿站',
类型: '影视',
host: 'https://www.dyyz.cc',
hostJs: '',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/',
url: '/index.php/api/vod?type=fyfilter&page=fypage',
filter_url: '{{fl.cateId}}&{{fl.area}}&{{fl.by}}&{{fl.class}}&{{fl.lang}}&{{fl.letter}}&{{fl.year}}',
detailUrl: 'voddetail/fyid.html',
searchUrl: '/vodsearch/**----------fypage---.html',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '电影&剧集&综艺&动漫&其他(短剧)',
class_url: '1&2&3&4&49',
filter_def: {
1: {cateId: '1'},
2: {cateId: '2'},
3: {cateId: '3'},
4: {cateId: '4'},
49: {cateId: '49'}
},

play_parse: true,
lazy: `js:
let kcode = JSON.parse(request(input).match(/var player_.*?=(.*?)</)[1]);
let kurl = kcode.url;
if (/\\.(m3u8|mp4)/.test(kurl)) {
input = { jx: 0, parse: 0, url: kurl };
} else {
input = { jx: 0, parse: 1, url: kurl };
}
`,

limit: 9,
double: false,
推荐: '.public-list-exp:has(.public-list-prb);a&&title;img&&data-src;.public-list-prb&&Text;a&&href',
一级: `js:
let furl=input.split("?")[0];
let fbody=input.split("?")[1];
let timestamp=Math.round(new Date/1e3).toString();
let key=md5("DS"+timestamp+"DCC147D11943AF75");
fbody=fbody+"&time="+timestamp+"&key="+key;
fetch_params.body=fbody;
let fhtml=post(furl,fetch_params);
let fdata=JSON.parse(fhtml);
VODS = fdata.list
`,
二级: {
title: 'h3&&Text;.slide-info--strong:eq(-1)&&Text',
img: '.detail-pic&&img&&data-src',
desc: '.slide-info:eq(0)&&span:eq(0)&&Text;.slide-info:eq(0)&&span:eq(1)&&Text;.slide-info:eq(0)&&span:eq(2)&&Text;.slide-info--strong:eq(2)&&Text;.slide-info--strong:eq(1)&&Text',
content: '.text&&Text',
tabs: '.anthology-tab&&a',
tab_text: 'body--span&&Text',
lists: '.anthology-list-play:eq(#id)&&a',
list_text: 'body&&Text',
list_url: 'a&&href',
},
搜索: '.public-list-box;.thumb-txt&&Text;img&&data-src;.public-list-prb&&Text;.public-list-exp&&href',

filter: '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'
}