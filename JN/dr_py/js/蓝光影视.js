var rule={
title: '蓝光影院',
host: 'https://www.languang.pro',
searchUrl: 'index.php/rss/index.xml?wd=**',
url: '/vodshow/fyclass--------fypage---.html',
headers: {'User-Agent': 'MOBILE_UA'},
class_parse: '.hl-nav li:gt(0):lt(4);a&&Text;a&&href;.*/(.*?).html',
//cate_exclude: '明星|专题|最新|排行|豆瓣',
play_parse: true,
lazy:`js: input = { jx: 0, parse: 1, url: input }`,
推荐: '*',
double: true,
一级: '.hl-vod-list li;a&&title;a&&data-original;.hl-pic-text&&span&&Text;a&&href',
二级: {
title: 'h2&&Text',
img: '.hl-lazy&&data-original',
desc: '.hl-full-box&&li:eq(1)&&Text;.hl-full-box&&li:eq(2)&&Text;.hl-full-box&&li:eq(3)&&Text;.hl-full-box&&li:eq(4)&&Text;.hl-full-box&&li:eq(5)&&Text;.hl-full-box&&li:eq(6)&&Text',
content: '.hl-content-text&&Text',
tabs: '.hl-tabs&&a',
lists: '.hl-plays-list:eq(#id)&&li'},
搜索: $js.toString(() => {let html = request(input);let items = pdfa(html, 'rss&&item');let d = [];items.forEach(it => {it = it.replace(/title|link|author|pubdate|description/g, 'p');let url = pdfh(it, 'p:eq(1)&&Text');d.push({title: pdfh(it, 'p&&Text'),url: url,desc: pdfh(it, 'p:eq(3)&&Text'),content: pdfh(it, 'p:eq(2)&&Text'),pic_url: 'https://img.soogif.com/qKCd8nJVrHpOaiRrh59615VCRe5DtvM5.gif',});});setResult(d);}),
searchable: 2,quickSearch: 0
}