var rule = {
author: '小可乐/2408/第一版',
title: '厂长资源',
类型: '影视',
//host: 'https://www.czys.pro',
host: 'https://www.cz01.vip',
hostJs: 'HOST = pdfh(request(HOST), "h2:eq(1)&&a&&href")',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/',
url: '/fyfilter/page/fypage',
filter_url: '{{fl.cateId}}{{fl.year}}{{fl.class}}{{fl.zilei}}',
detailUrl: '/movie/fyid.html',
searchUrl: 'http://czzy.210985.xyz/czzy_search8.php?wd=**&page=fypage',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '全部&最新电影&国产剧&番剧',
class_url: 'movie_bt&zuixindianying&gcj&fanju',
filter_def: {
movie_bt: {cateId: 'movie_bt'},
zuixindianying: {cateId: 'zuixindianying'},
gcj: {cateId: 'gcj'},
fanju: {cateId: 'fanju'}
},

play_parse: true,
// lazy代码源于香雅情大佬
lazy: `js:
pdfh = jsp.pdfh;
var html = request(input);
var ohtml = pdfh(html, '.videoplay&&Html');
var url = pdfh(ohtml, "body&&iframe&&src");
if (url) {
    var _obj={};
    eval(pdfh(request(url),'body&&script&&Html')+'\\n_obj.player=player;_obj.rand=rand');
    function js_decrypt(str, tokenkey, tokeniv) {
        eval(getCryptoJS());
        var key = CryptoJS.enc.Utf8.parse(tokenkey);
        var iv = CryptoJS.enc.Utf8.parse(tokeniv);
        return CryptoJS.AES.decrypt(str, key, {iv: iv,padding: CryptoJS.pad.Pkcs7}).toString(CryptoJS.enc.Utf8)
    };
    let config = JSON.parse(js_decrypt(_obj.player,'VFBTzdujpR9FWBhe', _obj.rand));
    input = {jx: 0, url: config.url, parse: 0}
} else if (/decrypted/.test(ohtml)) {
    var phtml = pdfh(ohtml, "body&&script:not([src])&&Html");
    eval(getCryptoJS());
    var script = phtml.match(/var.*?\\)\\);/g)[0];
    var data = [];
    eval(script.replace(/md5/g, 'CryptoJS').replace('eval', 'data = '));
    input = {jx: 0, url: data.match(/url:.*?['"](.*?)['"]/)[1], parse: 0}
} 
`,

limit: 9,
double: false,
推荐: '*',
一级: `js:
VODS = [];
let klists = pdfa(request(input),'li:has(img)');
klists.forEach((it) => {
    VODS.push({
        vod_name: pdfh(it,'img&&alt'),
        vod_pic: pdfh(it,'img&&data-original'),
        vod_remarks: pdfh(it,'.jidi&&Text')||pdfh(it,'.qb&&Text')||pdfh(it,'.furk&&Text'),
        vod_id: pdfh(it,'a:eq(0)&&href')    
    })
})
`,
二级: `js:
let khtml = request(input);
let kdetail = pdfh(khtml, '.dytext');
VOD = {};
VOD.vod_id = input;
VOD.vod_name = pdfh(kdetail, 'h1&&Text');
VOD.vod_pic = pdfh(khtml, '.dyimg&&img&&src');
VOD.type_name = pdfh(kdetail, 'li:eq(0)&&Text').replace('类型：','');
VOD.vod_remarks =/上映/.test(kdetail) ? kdetail.match(/上映：<span>(.*?)<\\/span>/)[1] : '未知';
VOD.vod_year = pdfh(kdetail, 'li:eq(2)&&Text').replace('年份：','');
VOD.vod_area = pdfh(kdetail, 'li:eq(1)&&Text').replace('地区：','');
VOD.vod_director =/导演/.test(kdetail) ? kdetail.match(/导演：(.*?)<\\/li>/)[1] : '未知';
VOD.vod_actor =/主演/.test(kdetail) ? kdetail.match(/主演：(.*?)<\\/li>/)[1] : '未知';
VOD.vod_content = pdfh(khtml, '.yp_context&&Text');

let ktabs = [];
let i = 1;
pdfa(khtml, '.paly_list_btn').map((it) => { 
    ktabs.push('👶厂长在线' + i);
    i++
});
VOD.vod_play_from = ktabs.join('$$$');

let kplists = [];
pdfa(khtml, '.paly_list_btn').forEach((pl) => {
    let plist = pdfa(pl, 'body&&a').map((it) => { return pdfh(it, 'a&&Text') + '$' + pdfh(it, 'a&&href') });
    plist = plist.join('#');
    kplists.push(plist)
});
VOD.vod_play_url = kplists.join('$$$')
`,
搜索: `js:
VODS = [];
let klists = request(input).split('$$$');
klists.forEach((it) => {
    let p = it.split('|');
    VODS.push({
        vod_name: p[1],
        vod_pic: p[2],
        vod_remarks: p[3],
        vod_id: p[0]
    })
})
`,

filter: 'H4sIAAAAAAAAA6WXX1PaTBTG7/kYuXZGSGtb+w1637tOpxMgwkZIFBIVHN+htVKgarGt1FqmOqMWqlK1ffvHCPJlkixc9St0F4Fdwm609EJnss/v7Mme3fNsWPQJcW0OyE+CunD/kW9RmJZTwn0hJUsJYUxQpbiMnuzz/62LBnqek2IGGni0KKh4eKXaXq7iYfQgLI1djQYm/f7/RL/f34na68rjeMZxrGFJDfdx9BhAeICFYw1LA3gg4GICgUFddOsird5yq7do9bZbvU2rE251glbvuNU7tHrXrd6l1Xtu9R6tTrrVSUoV/S4VDVCqu1pogFLdtRLpWonuWol0rUR3rdDA0uOlsf4ZCsWkZJI6RI0zmH8Bzy7sjy9veJSs+m7ry2kvTe+cPtGlSHI8FDUkVQF91n7ehEcHbFbWZZ2A2dft95/ZYFzSFoCkEjZfcZZX2KxizAI1QtBC1WqU2WhYSxsaTTr1Ix4Zp9MXqvDtBYeMRgm3nrVffWVzMZCMUlV6td/a4ywoYqRxTaklFVedTIUN65oaWRhYf6mMqsWGF4BiEPDghX3OWdQswG9A0C8/bLPGKT+QdDq/87ToZEpsdtoIkvzOs2NY2uC8KMqeItVCe9/Kc+qKNz8pU2jBebbNSY9RjX7X3JZl5tlwOiqp6ahM07XVVu4jZ8/mKeyTdbnLxuYNdKz7JHx62d6+5KSXgErtAMydcRtAAgMNAAsnsHHIRqfQmgxSV1jesUwTVjKcd0gsEHSnhlyD0wIzBKtscA/VNGkUaB7ajU3uhEpshkzZOmgSS3KfkyDBmkXUpmwsRe6l9s4367zIwVIEO647GU4Ru9qAx6ZBTAaUx9aKyGBv7K7b9saW9euNvWoOZUzKCSAnx6MGSBn4QKJ/s6SH4NH79mbTWa+21obX1A3FBzmE/iK6ARTaVOHb7+gu4IWFqWrYa+utk5o3j94sZYQB7lu6Z44r8HLdOzIug4ihDYW2dz7bHxrXJEXLYoQ67w6c8rF3aAIEZXUo0l47tc1P3pEoIDy8Uqv5HDbeOaUT72A5ZmhJMJy3sOu8bNr7Fe9ovH9SWBoKR1GtSpbl+73dRBHo/qHt/0PDMiseIaiw+NhQIWgnPfi4MrB1fDCq0BvlASYo8PtPe7+E2N/1nL3yw7oo/a4PG3cvwbxCFZZ5dffKoqFjizvZ93jMJyBrRFdpv7jUZ3hI0uUHYdLfnK8np5xxSqcDW+ias+9WZ1n4Zu+KfKjNiBO9j8dwUL967NfyaMvOZRGGNrjLRCRtSu7MR39SwOWas7Vr/erd0wkZE+kofeExrGZ0pxnNaP7SZ0a2mdFdZnSTGdlj/sVi/slhrjWYbmtEQsoI/eD2GDwL00zQ5iiGrrMNpGNC+hzX7K73ugGbuYnL8E4CNpZuRaY61vj3NYGbhyTB1IC/onG7bMJ8rucFqHXjmOh0VZD3g8TD1HxLfwAggnVNWBAAAA=='
}