var rule = {
title: '风车动漫',
host: 'http://d.fengche531.com',
hostJs: '',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,
homeUrl: '',
url: '/list/fyclass-fypage.html',
searchUrl: '/common/search.aspx?hso=hso&keyww=',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 
class_name: '国产动漫&日本动漫&其它动漫&动漫电影',
class_url: '137&138&157&158',
play_parse: true,
parse_url: 'https://www.pouyun.com/?url=',
推荐: 'body&&.list&&li;.itemtext&&Text;.imgblock&&style;.itemimgtext&&Text;a&&href',
一级: 'body&&.list&&li;.itemtext&&Text;.imgblock&&style;.itemimgtext&&Text;a&&href',
二级: {
"title": "h1&&Text;.show&&p:eq(0)&&Text",
"img": "img&&src",
"desc": "",
"content": ".info&&Text",
"tabs": ".plist",
"lists": "#playlists&&a",
"list_url": "a&&href"
},
搜索: '*'

}