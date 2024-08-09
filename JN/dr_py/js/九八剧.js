var rule = {
author: '小可乐/2408/第一版',
title: '九八剧',
类型: '影视',
host: 'https://www.jiubaj.com',
hostJs: '',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/',
url: '/vodshow/fyfilter.html',
filter_url: '{{fl.cateId}}-{{fl.area}}-{{fl.by}}-{{fl.class}}-{{fl.lang}}-{{fl.letter}}---fypage---{{fl.year}}',
detailUrl: '',
searchUrl: '/vodsearch/**----------fypage---.html',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '电影&剧集&综艺&动漫',
class_url: '1&2&3&4',
filter_def: {
1: {cateId: '1'},
2: {cateId: '2'},
3: {cateId: '3'},
4: {cateId: '4'}
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
推荐: '*',
一级: '.lazyload;a&&title;a&&data-original;.text-right&&Text;a&&href',
二级: {
title: 'h1--span&&Text;.data--span:eq(0)&&Text',
img: '.v-thumb&&img&&data-original',
desc: '.data:eq(-1)&&Text;.data:eq(0)&&a:eq(-1)&&Text;.data:eq(0)&&a:eq(-2)&&Text;.data--span:eq(1)&&Text;.data--span:eq(2)&&Text',
content: 'p.col-pd&&Text',
tabs: '.bottom-line:has(span) h3',
tab_text: 'body&&Text',
lists: '.stui-content__playlist:eq(#id)&&a',
list_text: 'body&&Text',
list_url: 'a&&href',
},
搜索: '*',

filter: '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'
}