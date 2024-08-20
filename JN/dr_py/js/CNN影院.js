var rule = {
title: 'CNN影院',
host: 'https://www.zhuoloufs.com',
hostJs: '',
headers: {
    'User-Agent': 'PC_UA',
    Referer: 'https://www.zhuoloufs.com',
  },
编码: 'utf-8',
homeUrl: '/',
url: '/vod/show/id/fyclass/page/fypage',
searchUrl: '/vod/search/**;page=fypage',
searchable: 2, quickSearch: 0,
class_name: '电影&电视剧&动漫&综艺',
class_url: '1&2&4&3',
play_parse: true,
parse_url: '',
lazy: "js:\n        let url_id = input.split('/')[5];\n        let jishu_id = input.split('/')[7];\n        let t = new Date().getTime();\n        eval(getCryptoJS);\n        let signkey = 'id=' + url_id + '&nid=' + jishu_id + '&key=cb808529bae6b6be45ecfab29a4889bc&t=' + t;\n        let key = CryptoJS.SHA1(CryptoJS.MD5(signkey).toString()).toString();\n        let json_data = JSON.parse(request('https://www.zhuoloufs.com/api/mw-movie/anonymous/video/episode/url?id=' + url_id + '&nid=' + jishu_id, {\n            headers: {\n                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',\n                'deviceid': '58a80c52-138c-48fd-8edb-138fd74d12c8',\n                'sign': key,\n                't': t\n            }\n        }));\n        let url = json_data.data;\n        log(url);\n        if (url) {\n            input = {parse: 0, url: url, header: rule.headers};\n        }\n\n    ",
  图片替换: "js:\n        // log(MY_URL);\n        let src = decodeURIComponent(input).split(',')[0].split(' ')[0];\n        input = urljoin(MY_URL, src) + '@Referer=https://obs.gduamoe.com/';\n    ",
推荐: '*',
一级: '.hover-card__Content-sc-3b60c4fc-0 .content-card;.title&&Text;.card-img&&img&&src;.tag&&Text;a&&href',
二级: {
"title": "h1&&Text;",
"img": ".bkHHjg&&img&&src",
//主要描述;年份;地区;演员;导演
"desc": ".ghArEv&&Text;",
"content": ".wrapper_more_text&&Text",
"tabs": ".player_name",
"lists": ".main-list-sections__BodyArea-sc-8bb7334b-2:eq(#id)&&a",
"list_url": "a&&href"
},
搜索: '*',

}