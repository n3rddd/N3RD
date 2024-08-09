var rule = {
author: '小可乐/240701/第一版',
title: '爱你短剧',
类型: '影视',
host: 'https://www.ainidj.com',
hostJs: '',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/',
url: '/vodshwo/fyfilter---fypage---.html',
filter_url: '{{fl.cateId}}--{{fl.by}}---{{fl.letter}}',
detailUrl: '',
searchUrl: '/vodsearch/**----------fypage---.html',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '穿越&爱情&古代',
class_url: 'fenle&fenlei4&gudai',
filter_def: {
fenle: {cateId: 'fenle'},
fenlei4: {cateId: 'fenlei4'},
gudai: {cateId: 'gudai'}
},

play_parse: true,
lazy: `js:
if (/quark/.test(input)) {
let confirm="";
input = getProxyUrl().replace('js','quark')+'&type=push'+confirm+'&url='+encodeURIComponent(input)
} else {
let kcode = JSON.parse(request(input).match(/var player_.*?=(.*?)</)[1]);
let kurl = kcode.url;
if (/\\.(m3u8|mp4)/.test(kurl)) {
input = { jx: 0, parse: 0, url: kurl };
} else {
input = { jx: 0, parse: 1, url: kurl };
}
}
`,

limit: 9,
double: false,
推荐: '*',
一级: '.module-item;img&&alt;img&&data-src;.module-item-text&&Text;a:eq(0)&&href',
二级: `js:
let khtml = request(input);
VOD = {};
VOD.vod_id = input;
VOD.vod_name = pdfh(khtml, 'h1&&Text');
VOD.vod_pic = pdfh(khtml, '.video-cover&&img&&data-src');
VOD.type_name = pdfh(khtml, '.tag-link:eq(0)&&Text') + pdfh(khtml, '.tag-link:eq(1)&&Text');
VOD.vod_remarks = pdfh(khtml, '.video-info-items:eq(-3)&&Text');
VOD.vod_year = pdfh(khtml, '.tag-link:eq(-2)&&Text');
VOD.vod_area = pdfh(khtml, '.tag-link:eq(-1)&&Text');
VOD.vod_director = pdfh(khtml, '.video-info-actor:eq(0)&&Text');
VOD.vod_actor = pdfh(khtml, '.video-info-actor:eq(1)&&Text');
VOD.vod_content = pdfh(khtml, '.vod_content&&span&&Text');

let ktabs = [];
if ( pdfh(khtml,'.tab-item span&&Text') !== 0 ) { ktabs.push("爱你专线") };
if ( pdfh(khtml,'.video-info-items:has([href^=https://pan.quark])') !== 0 ) { ktabs.push("夸克网盘") };
VOD.vod_play_from = ktabs.join('$$$');

let klists = [];
ktabs.forEach((tab) => {
if (/夸克网盘/.test(tab)) {
    let qk_plist = '夸克_合集' + '$' + pdfh(khtml,'.video-info-items:eq(0)&&a&&href') ;
    klists.push(qk_plist)
} else  {
    let zx_plist = pdfa(khtml, '.sort-item&&a').map((it) => { return pdfh(it, 'a&&Text') + '$' + pd(it, 'a&&href', input) });
    zx_plist = zx_plist.join('#');
    klists.push(zx_plist)
}
});
VOD.vod_play_url = klists.join('$$$')
`,
搜索: '.module-search-item;.video-serial&&title;*;.video-serial&&Text;.video-serial&&href',

filter: 'H4sIAAAAAAAAA+3Tz0vCYBgH8Lt/xnteEOWlbpWa2u/UTKPDqpUjXWQzEhkEWkn5IyKwkx0qWIcwIYL00D/jO/O/aKOvz5Ju3YQdBtvnO973OTzfnIvtSkpSYpMbrhzbl7Jskm2LqhTYYQJTxJQZsG6zzetX5vexmMxYf+aYYvHz59f7pcXmx88hmvATGcW77lP9dySPUdi7KHdv7wfCcaZtagINkJRUVUrbA/CXmtEo/xmAn+m9vI6D6PgpwBTJNGSaZAYyQ+KBeEi8EC+JD+IjmYXMkvghfpIAJEAShARJ5iBzJPOQeZIFyALJImSRZAmyRLIMWSZZgayQrEJWSUKQEEkYEiaJQCIka5A1kigkSrIOWSeJQWIkcUicZHRkAma9DezKVtbeE6Nyw1vVP3ti1N57tTccoMope087rZbxeoskIatHlHw1Crx4juRo+yAtWde6NgX0RXb/pzHFppE/G9h8t33jdYnreYR7mR2RErNKvNTuz5KQlKzs9MXpy7D0xdpl+R9t4dXHTvvhVyFkuxGVAv/oN+IkIyoJ87Fn0U/tmmVF5VBW9pzCOIUZisK4tG+PIybYkwkAAA=='
}