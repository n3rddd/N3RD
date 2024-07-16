var rule = {
author: '小可乐改编自道长/240701/第一版',
title: 'PTT视频',
类型: '影视',
host: 'https://ptt.red',
hostJs: '',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/zh-hans',
url: '/zh-cn/p/fyclassfyfilter',
filter_url: '{{fl.class}}?page=fypage&{{fl.area}}&{{fl.year}}&{{fl.by}}',
detailUrl: '',
searchUrl: '/zh-hans/q/**?page=fypage',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '电影&剧集&综艺&动漫&短剧&体育',
class_url: '1&3&2&4&66&53',
filter_def: {},

play_parse: true,
parse_url: '',
lazy: `js:
let kcode = JSON.parse(request(input).match(/json">(.*?)</)[1]);
if (kcode.contentUrl) {
    let kurl = kcode.contentUrl;
    if (/m3u8|mp4/.test(kurl)) {
        input = { jx: 0, parse: 0, url: kurl };
    } else {
        input = { jx: 0, parse: 1, url: kurl };
    };
} else {
    input;
}
`,

limit: 9,
double: false,
推荐: '*',
一级: '.embed-responsive;img&&alt;img&&src;.badge-success&&Text;a&&href',
二级: `js:
let html = request(input);
let kcode = html.split('node:')[1].split('},')[0] + '}';
let json = JSON.parse(kcode.trim());
VOD = {};
VOD.vod_id = input;
VOD.vod_name = json.title;
VOD.type_name = json.type;
VOD.vod_pic = urljoin(HOST, json.thumbnail);
VOD.vod_remarks = json.note;
VOD.vod_year = json.year;
VOD.vod_area = json._area;
VOD.vod_director = json.director;
VOD.vod_actor = json.actors;
VOD.vod_content = json.description;

let v_tabs = pdfa(html, '.nav-tabs&&a');
let v_tab = v_tabs.map(it => pdfh(it, 'a&&title'));
VOD.vod_play_from = v_tab.join('$$$');

let lists = [];
let v_tab_urls = v_tabs.map(it => pd(it, 'a&&href', input));   
let htmls=v_tab_urls.map((it) =>{return request(it, {headers:{"User-Agent":MOBILE_UA}})});   
htmls.forEach((ht) => {
    if (ht) {
        let list0 = pdfa(ht, '.mb-2.fullwidth&&a').map(it => pdfh(it, 'a&&Text') + '$' + pd(it, 'a&&href', input));
        lists.push(list0);
    } else {
        lists.push([]);
    }
});
let playUrls = lists.map(it => it.join('#'));
VOD.vod_play_url = playUrls.join('$$$')
`,
搜索: '*',

filter: 'H4sIAAAAAAAAA+2Y304aQRTG73mMvSaRnYX9Y8KTGNNsLRdNrU3ANiGEBCUYpK2AsVBSkjbRClqEbTQEsWtfhp1d3qI7lXLOTncSL/BGuZzzy8zsfOc7wxxyEUmWVtciOelVKiutShubZiYjRaUt83XKHzr7HVos+eN35uZbP7CWk7ZYuNSdFrss7A+kfPQu6tb2vP54Fl3ZWFGUOXIq3YndBpQA0mj7mwBRYbnyz9ned0QD0qk71zdA9DmhOzVaaAAxYE5l4NrnQOQYTCp/noz3EZLxd9NfPxAigObSzBCc1h2fO/YnJATaa7fnNuoIxfFe7hE6lYJEKg0nN+hYcTix1zn2Bldolv+F6/noPKFmOmWifLYt58P4nvl0TjrT1t4sytZ59vJFEgSYnrboaMBh9M1Vi17fchhOO/165nyxOSxDjmnzO233eI4y3eu4twccB/PQSytkeciD89Fyxqc8j4cr/o8rQWmzKTMN0tLmcNq8uqe0JEbisxhbJfl3jKDCQQVDwkGCocxBGcMYB2MIykYQygaGOgd1DDUOahiqHFQxTHAwgSGnEMsOlv95Fol/cOiMq/+J7xYv6OEFLz5tF2jDmkUzb9LbSf/S22aLR9ajEUlZ1H0YqB92QxjhteMjlIlA3bDLTQ6vCYaU8HJiiIRXCtuLhFcJuy6J8MohS/M/BfOTBzO/4JeBeVVcF7ouNL8RE5rfkIXmR7njHc6Ss3T4o3d4/KEcTlShV3VV6FVdE3qVaEKvEn3p1SfgVVVdWG9WtoNtFgjjdQuBRkYFQd2z396wAkgTNzIaapqqJ94xbtzQM6VoO6Nd5H5Y0D1qO/1vCIELvVaN7rxHSNwZafFlYTyBwkgs7JHuDS/dWhEMlIAcu4N+EMHJ6WhEy1WEDOR+KzBLRf8L2PUgEvSb7AmzfG4/eh9H8n8AiBEtTn4TAAA='
}
