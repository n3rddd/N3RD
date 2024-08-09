var rule = {
author: '小可乐/2408/第一版',
title: '七味网',
类型: '影视',
//host: 'https://www.qnmp4.com',
host: 'https://www.qn63.com',
hostJs: 'js: HOST = pdfh(request(HOST),"ul&&a:eq(5)&&href")',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/',
url: '/ms/fyclass-fyfilter.html',
filter_url: '{{fl.area}}-{{fl.by}}-{{fl.class}}-{{fl.lang}}-{{fl.letter}}---fypage---{{fl.year}}',
detailUrl: '/mv/fyid.html',
searchUrl: '/index.php/ajax/suggest?mid=1&wd=**&page=fypage&limit=30',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '电影&剧集&综艺&动漫&短剧',
class_url: '1&2&3&4&30',
filter_def: {},

tab_remove: ['下载-百度网盘', '下载-迅雷网盘', '下载-天翼网盘'],
play_parse: true,
lazy: `js:
if (/magnet/.test(input)) {
    input = { jx: 0, parse: 1, url: input };
} else if (/quark|aliyundrive|alipan/.test(input)) {
    let type = "ali";
    if (/quark/.test(input)) {
        let type = "quark"
    } else if (/aliyundrive|alipan/.test(input)) {
        let type = "ali"
    };
    let confirm="";
    input = getProxyUrl().replace('js',type)+'&type=push'+confirm+'&url='+encodeURIComponent(input)
} else {
    let kcode = JSON.parse(request(input).match(/var player_.*?=(.*?)</)[1]);
    let kurl = kcode.url;
    if (/\\.(m3u8|mp4)/.test(kurl)) {
        input = { jx: 0, parse: 0, url: kurl }
    } else {
        input = { jx: 0, parse: 1, url: kurl }
    }
}
`,

limit: 9,
double: false,
推荐: '*',
一级: 'a:has(article);a&&title;img&&src;.s1--i&&Text;a&&href',
二级: `js: 
let khtml = request(input);
let kdetail = pdfh(khtml, '.content-rt');
VOD = {};
VOD.vod_id = input;
VOD.vod_name = pdfh(kdetail, 'h1--span&&Text');
VOD.vod_pic = pdfh(khtml, '.img&&img&&src');
VOD.type_name = pdfh(kdetail, 'p--span:eq(2)&&Text');
VOD.vod_remarks = pdfh(kdetail, 'p:eq(0)&&Text');
VOD.vod_year = pdfh(kdetail, '.year&&Text');
VOD.vod_area = pdfh(kdetail, 'p--span:eq(3)&&Text');
VOD.vod_director = '未知' ;
VOD.vod_actor = pdfh(kdetail, 'p--span:eq(1)&&Text');
VOD.vod_content = pdfh(khtml, '.sqjj_a--span&&Text');

let ktabs = [];
let zx_tabs = pdfa(khtml,'.py-tabs&&option');
if (zx_tabs.length !== 0) { zx_tabs.map((it) => { return ktabs.push('在线-' + pdfh(it, 'body&&Text')) }) };
let xz_tabs = pdfa(khtml,'.nav-tabs li');
if (xz_tabs.length !== 0) { xz_tabs.map((it) => { return ktabs.push('下载-' + pdfh(it, 'body&&Text')) }) };
VOD.vod_play_from = ktabs.join('$$$');

let klists = [];
let zx_plists = pdfa(khtml, 'ul.player');
let xz_plists = pdfa(khtml, 'ul.content');
let i = 0;
let j = 0;
ktabs.forEach((tab) => {
    if (/在线/.test(tab)) {
        let zx_plist = pdfa(zx_plists[i], 'a').map((it) => { return pdfh(it, 'a&&Text') + '$' + pd(it, 'a&&href', input) });
        i++;
        zx_plist = zx_plist.join('#');
        klists.push(zx_plist)
    } else if (/下载/.test(tab) ) {
        let xz_plist = pdfa(xz_plists[j], 'a').map((it) => { return pdfh(it, 'a&&Text') + '$' + pdfh(it, 'a&&href') });
        j++;
        xz_plist = xz_plist.join('#');
        klists.push(xz_plist)        
    }
});
VOD.vod_play_url = klists.join('$$$')
`,
搜索: 'json:list;name;pic;en;id',

filter: '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'
}