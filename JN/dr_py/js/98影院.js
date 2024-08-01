var rule = {
author: '小可乐/240701/第一版',
title: '98影院',
类型: '影视',
host: 'http://www.98dyb.com',
hostJs: '',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/',
url: '/fyfilter/indexfypage.html[/fyfilter/index.html]',
filter_url: '{{fl.cateId}}',
detailUrl: '',
searchUrl: '/search.php?page=fypage&searchword=**&searchtype=',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '电影&剧集&综艺&动漫&短剧',
class_url: 'dianyingpian&dianshiju&zongyi&dongman&duanju',
filter_def: {
dianyingpian: {cateId: 'dianyingpian'},
dianshiju: {cateId: 'dianshiju'},
zongyi: {cateId: 'zongyi'},
dongman: {cateId: 'dongman'},
duanju: {cateId: 'duanju'}
},

play_parse: true,
lazy: `js: input = { jx: 0, parse: 1, url: input }`,

limit: 9,
double: false,
推荐: '*',
一级: '.lazyload;a&&title;a&&data-original;.text-right&&Text;a&&href',
二级: {
title: 'h1&&Text;.data--span:eq(-1)&&Text',
img: 'a.v-thumb&&data-original',
desc: '.data:eq(0)&&Text;.data:eq(-1)&&a:eq(-1)&&Text;.data:eq(-1)&&a:eq(-2)&&Text;.data--span:eq(2)&&Text;.data--span:eq(1)&&Text',
content: '.detail-content:eq(0)&&Text',
tabs: '.bottom-line:has(span) h3',
tab_text: 'body&&Text',
lists: '.stui-content__playlist:eq(#id)&&a',
list_text: 'body&&Text',
list_url: 'a&&href',
},
搜索: '.v-thumb;*;*;*;*',

filter: 'H4sIAAAAAAAAA63Q3U7CMBQH8Ps9Rq/3BLyBz0C4OEKzdkDnBzWyZYmEEJkmflyIJhK9MpvGRLnTkfk0axvegpKhXbn2qjntr//T08hBHQpsSJl3oFfUaDoR6uIhaqA2DPBeB7mIQR/rWi2W4ulS1yfQ43qjGSHtkZhkq3G22daFlRW7W3GRlcVcJee/KGBeyAPLqOlCjifGAD3cjVHprfheGtLFhAOziBzdyLNZjehO+9wm04cyTwwJCbCQ4N0nz+YiSY06pb4do/I3UdwZ4NOeDfR1ayCfm4FasdNyq48/Jjr5P369Cvrr/liUearfsBUeD9rAakB+fYjrzxoA5g2gHiHfU/VzZUTA+9g6v39ZPb+a8yNKqg6b6Zx4DZRfhxRZAgAA'
}