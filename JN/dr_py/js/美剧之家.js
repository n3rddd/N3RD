var rule = {
author: '小可乐/240701/第一版',
title: '美剧之家',
类型: '影视',
host: 'https://www.mjzj.me',
hostJs: '',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/',
url: '/vod/fyclass-fyfilter.html',
filter_url: '{{fl.area}}-{{fl.by}}-{{fl.class}}--{{fl.letter}}---fypage---{{fl.year}}',
detailUrl: '',
searchUrl: '/vodsearch/**----------fypage---.html',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '电影&剧集',
class_url: '21&20',
filter_def: {},

play_parse: true,
parse_url: '',
lazy: `js:
var kcode = JSON.parse(request(input).match(/var player_.*?=(.*?)</)[1]);
var kurl = kcode.url;
if (/\\.(m3u8|mp4)/.test(kurl)) {
input = { jx: 0, parse: 0, url: kurl };
} else {
input = { jx: 0, parse: 1, url: kurl };
}
`,

limit: 9,
double: false,
推荐: '*',
一级: '.pic;a:eq(0)&&title;img&&data-src;.s4&&Text;a:eq(0)&&href',
二级: `js:
let html = request(input);
VOD = {};
VOD.vod_id = input;
VOD.vod_name = pdfh(html, 'h1&&Text');
VOD.type_name = pdfh(html, '.type&&Text');
VOD.vod_pic = HOST + pdfh(html, '.pic:eq(0)&&img&&data-src');
VOD.vod_remarks = pdfh(html, '.zhuangtai&&Text');
VOD.vod_year = pdfh(html, '.type&&a:eq(-2)&&Text');
VOD.vod_area = pdfh(html, '.type&&a:eq(-1)&&Text');
VOD.vod_director = pdfh(html, '.clamp2--span:eq(0)&&Text');
VOD.vod_actor = pdfh(html, '.clamp2--span:eq(1)&&Text');
VOD.vod_content = pdfh(html, '.juqing--a&&Text');

let ninput = input.replace('voddetail', 'vodplay').replace('.html', '-1-1.html');
let ktabs = pdfa(request(ninput),'.mxianlu&&a');
let ktab = ktabs.map(it => pdfh(it, 'a--small&&Text'));
VOD.vod_play_from = ktab.join('$$$');

let klists = [];
let ktab_urls = ktabs.map(it => pd(it, 'a&&href', input));
ktab_urls.forEach((vtu) => {
    if (/javascript/.test(vtu)) {
    let klist = pdfa(request(ninput), '.jisu&&a').map(it => pdfh(it, 'a&&Text') + '$' + pd(it, 'a&&href', input));
    klists.push(klist);           
    } else {
    let klist = pdfa(request(vtu), '.jisu&&a').map(it => pdfh(it, 'a&&Text') + '$' + pd(it, 'a&&href', input));
    klists.push(klist);
    }
});
let playUrls = klists.map(it => it.join('#'));
VOD.vod_play_url = playUrls.join('$$$')
`,
搜索: 'ul:eq(-1) li;*;*;.state&&Text;*',

filter: 'H4sIAAAAAAAAA+2WWU/bQBSF3/Mz/JxK41CW9o1933cQDymKVFRKJUgrIYTEvkMCgqShtFCVvSymVKiYJvkzsU3+RR3mzr2DikaIB57y5vOdzHiOZ+ycEY/m07XX3Z4R7V1gWHut9fb7h4Y0rzbgfx9wpTV/YE9Ou/qTv/+jC7pHtIEMnj5MTx5msCu0US9Q/DEJ9CJbLhEeF+gtHKbiW8LjQnjO3AXNCUJ49uSCPbEJHgj0xsP2WER4XOCcC+dO/FjMyQWOmzhxIqtiHBc4zjy24htiHBeYYW/Wur4RGbjAcQer5IHAcTNr6diRGMcFemdXlnkqPC7QW5mxQr+ExwVmmPucMudFBi6El/q7c3tmgAcC5wzt3v7A/eMCvfCSPYb7x4Xw0tuXqesweCCkvXXWb2hvM0J4t8mwS8ADgc9s+9SZnxXPjAvMd7qfSuyIfFyQt3Q79w29O4FrmUo6P/fEWrjA+40n0psJcT8ucJ17STrtIEZ7Rr340vgHA37pndkyrCXzke+Mk1ixvsTFfbnA9e4epGMzYr1cYM7onr11InJygetdvKA5QeC4yw3yQNA+HpEHAr39mP3nXHhc4DqXDcvcF+vkgvZ/x15MuovHIyA0nTrDvk7gqbsT0pN3Qu7ex+jhg6Y8hpzHkNecSk458agdEcsmjaMjhrsg6+t3MQHqe/s7HPAP0v7a0at09Pcj99fHfC+B3V1KPId4jsx9xH0y14nrMmfEmcT1V8jdS4kXEC+QeT7xfJnnEc+TeS7xXJlTXl3Oq1NeXc6rU15dzqtTXl3Oq1NeXc7LKC+T8zLKy+S8jPIyOS+jvEzOyygvk/MyysvkvIzyMjkvo7xMzssoL5PzMsrrXt47l/2BYDAgnUzrNGqfLz/yZBYCKERSBKQISTGQYiQlQEqQlAIpRVIGpAxJOZByJBVAKpBUAqlEUgWkCkk1kGokNUBqkNQCqUVSB6QOST2QeiQNQBqQNAJpRNIEpAlJM5BmJC1AWpC0AmlF0gakDUk7kHYkHUA6kHQC6UTSBaQLCXshXoLM1b2z8mZY+oKtrFlm6L9zQh82VwT73J/il9Q0bWMdnLd9wSH6Qp9PWXPiP2qo98NgIHNbT4/XLZbsOYqlqiCqSudTS6CqJKkKqaogqgqwqgQqi+UTC6Kq6ClLtaocK0quqpCqip6qIKoK6YOl8xnKnKqUqYqXsgQ+VH6yxSVbXLLFJVtcssVFe0px8Yz+A3ULwm0UEwAA'
}