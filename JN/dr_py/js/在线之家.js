var rule = {
author: '小可乐/2408/第一版',
title: '在线之家',
类型: '影视',
//host: 'https://www.zxzja.com',
host: 'https://www.zxzj.site',
hostJs: 'js: HOST = pdfh(request(HOST), "ul:eq(0)&&a:eq(0)&&href")',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/',
url: '/vodshow/fyfilter.html',
filter_url: '{{fl.cateId}}-{{fl.area}}-{{fl.by}}--{{fl.lang}}-{{fl.letter}}---fypage---{{fl.year}}',
detailUrl: '',
searchUrl: '/vodsearch/**----------fypage---.html',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '电影&剧集(美剧)&动漫',
class_url: '1&2&6',
filter_def: {
1: {cateId: '1'},
2: {cateId: '2'},
6: {cateId: '6'}
},

tab_remove: ['迅雷网盘', '百度网盘'],
play_parse: true,
lazy: `js:
let kcode = JSON.parse(request(input).match(/var player_.*?=(.*?)</)[1]);
let kurl = kcode.url;
if (/quark/.test(kurl)) {
    let type = 'quark';
    let confirm = '';
    input = getProxyUrl().replace('js',type)+'&type=push'+confirm+'&url='+encodeURIComponent(kurl)
} else {
    input = { parse: 1, url: input, header: {'User-Agent': 'MOBILE_UA', 'Referer': 'HOST'} }
} 
`,

limit: 9,
double: false,
推荐: '*',
一级: '.lazyload;a&&title;a&&data-original;.text-right&&Text;a&&href',
二级: `js: 
let khtml = request(input);
let kdetail = pdfh(khtml, '.stui-content__detail');
VOD = {};
VOD.vod_id = input;
VOD.vod_name = pdfh(kdetail, 'h1&&Text');
VOD.vod_pic = pdfh(khtml, '.pic&&img&&data-original');
VOD.type_name = kdetail.match(/类型：(.*?)\\//)[1];
VOD.vod_remarks = pdfh(kdetail, '.data:eq(-1)&&Text');
VOD.vod_year = kdetail.match(/年份：(.*?)</)[1];
VOD.vod_area = kdetail.match(/地区：(.*?)\\//)[1];
VOD.vod_director = kdetail.match(/导演：(.*?)</)[1];
VOD.vod_actor = kdetail.match(/主演：(.*?)</)[1];
VOD.vod_content = pdfh(kdetail, '.detail-content&&Text');

let ktabs = [];
pdfa(khtml,'.stui-vodlist__head:has(span) h3').map((it) => ktabs.push(pdfh(it, 'body&&Text')) );
VOD.vod_play_from = ktabs.join('$$$');

let klists = [];
let plists = pdfa(khtml, '.stui-content__playlist');
plists.forEach((pl) => {
    let plist = pdfa(pl, 'a').map((it) => { return pdfh(it, 'a&&Text') + '$' + pd(it, 'a&&href', input) });
    plist = plist.join('#');
    klists.push(plist)
});
VOD.vod_play_url = klists.join('$$$')
`,
搜索: '*',

filter: 'H4sIAAAAAAAAA+2XXU8TQRSG7/sz9romM8UCcsf39/c3hIsVN0rEmpRq0jRNTCgGgtDEKE1TojdAMQFb1KCWtPyZ7rb9F27dM+ecDUmtil7t3b7P2WnnPTO772zMp0mtY9kX0x4bUa1D08OGrvm1kP7EsJV5mDdfFWz9XF9/ZoPlmBaq463T2uZpHdtCi/uBHmVr6ZdAQaha7SRtfctBDQSOS+at7yU1zhGqZp1lK6V9qIHA33z/wcwU1W86Aseljq3DMzXOEVj7nKdxIHAue3mzcKLm4ghVK18nKsWUdaBskMbRW5flqwM12hHxlbgfu7uuhx5Sd6u58+rpiya7W929sO8HCoJ1gmogWCeoBoI68ZbVHMG6xGt5XjNLX6kGwt1BVkaNd2SKrOwIVat8OqIaCNZ/qoHA7hxfV5LnlZ006xFH6CqRtHemuc365UJsJc2Pm7SSdeFayaihh2klrdRlLfWlyZUMiMBdYD8vGW8h3sJ5gHiAc0lcci6IC8blPeT2JePtxNs5byPexnkr8VbOg8SDnJNfyf1K8iu5X0l+Jfcrya/kfiX5ldyvIL+C+xXkV3C/gvwK7leQX8H9CvIruF9BfgX3K8iv4H4F+RXcryC/gvsV5Ne+dL9hjEjEYDvTPE9Zub0md2YngE4kXUC6kHQD6UbSA6QHSS+QXiR9QPqQ9APpRzIAZADJIJBBJENAhpAMAxlGMgJkBMkokFEkY0DGkIwDGUcyAWQCySSQSSRTQKaQTAOZRjIDZAbJLJBZJHNA5pDMA5lHsgBkAckikEUkS0CWkIg76iGoX7n2yv0oe4PtvzYLyRv7hF5stois2bfi27hQsPJvoPJoLbJB7+JcwtxW54CN1adho/63vhW/Twvwo8aqHjEGH9AUKhdX5rvdG1OwI9/cyaoN70p/xPQw2QlHmJ69eswjDrrb8BdHnls9nvyHg0KjwP/tQ4QXh14cenHoxaEXh9ofxmHrbX15Z4rlgko3EA2jpon4+pffso2+ABt9rzaKtl/O14soL6K8iPIiyouopiPKF/8BdG+NSh8WAAA='
}