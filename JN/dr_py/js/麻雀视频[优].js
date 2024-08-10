var rule = {
author: '道门子弟/2408/第三版',
title: '麻雀视频',
host: 'https://www.mqtv.one',
hostJs: `js: 
	//HOST = pdfh(request(HOST),"ul#leo-pan-li&&a&&href");
	HOST="https://www.mqtv.cc/"
	`,
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,
homeUrl: '/libs/VodList.api.php?type=tv&page=1',
url: '/libs/VodList.api.php?type=fyclass&page=fypage&rank=&cat=&year=&area=',
filter_url: '',
detailUrl: '',
searchUrl: '/libs/VodList.api.php?search=**',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 
class_name: '电影&剧集&综艺&动漫',
class_url: 'movie&tv&va&ct',
filter_def: {},
isVideo: 'obj/tos',
parse_url: 'https://player.mqtv.cc/fun/?url=',
play_parse: true,
lazy: `js: 
let url=rule.parse_url+input;
let html=request(url);

const sortByKey = (_0x4d27a8, _0xefe71d, _0x3cc4d7) => _0xefe71d.sort(({
    [_0x4d27a8]: _0xf7c6bb
  }, {
    [_0x4d27a8]: _0x53258e
  }) => _0x3cc4d7(_0xf7c6bb, _0x53258e))
  
  let _0x17f483 = pdfh(html,'meta[name=viewport]&&id').replace("now_", ""),
    _0x34c878 = pdfh(html,'meta[charset=UTF-8]&&id').replace("now_", ""),
    _0x38c5ab = [],
    _0x22a2d9 = [],
    _0x12c64b = "";
  for (var _0x4fc61c = 0; _0x4fc61c < _0x34c878.length; _0x4fc61c++) {
    _0x38c5ab.push({
      "id": _0x34c878[_0x4fc61c],
      "text": _0x17f483[_0x4fc61c]
    });
  }
  _0x22a2d9 = sortByKey("id", _0x38c5ab, (_0x5738b, _0x20b822) => _0x5738b - _0x20b822);
  for (var _0x4fc61c = 0; _0x4fc61c < _0x22a2d9.length; _0x4fc61c++) {
    _0x12c64b += _0x22a2d9[_0x4fc61c].text;
  }
  
    let _0x445162 = md5(_0x12c64b + "lemon").toString();
  let key = _0x445162.substring(16);
  let iv = _0x445162.substring(0, 16);
  let str1=html.match(/"url": "(.*?"),/)[1].slice(0,-1);
console.log(key);
console.log(iv);
log(str1)
url= CryptoJS.AES.decrypt(str1, CryptoJS.enc.Utf8.parse(key), {
		iv: CryptoJS.enc.Utf8.parse(iv),
		mode: CryptoJS.mode.CBC,
		padding: CryptoJS.pad.Pkcs7
	}).toString(CryptoJS.enc.Utf8)
log(url)
input = {parse: 0, url: url}
`,
预处理: `js:
let {cookie, html} = reqCookie(HOST);
rule.headers["Cookie"]=cookie;
`,
limit: 9,
double: false,
推荐: '*',
一级: `js:
let {cookie, html} = reqCookie(HOST);
rule.headers["Cookie"]=cookie;
let kjson=JSON.parse(request(input));
let kdata=[];
kjson.data.map((it)=>{
    kdata.push({
        vod_name: it.title,
        vod_pic: it.img,
        vod_remarks: it.remark,
        vod_id: it.url,  
        vod_content: it.desc
    })
});
VODS = kdata
`,
二级: `js:
let {cookie, html} = reqCookie(HOST);
rule.headers["Cookie"]=cookie;
VOD = {};
let ctid = input.match(/.*\\/(\\d+)/)[1];
let detailUrl = HOST+ '/libs/VodInfo.api.php?ctid=' + ctid;
let kdata = JSON.parse(request(detailUrl)).data;
VOD.vod_id = input;
VOD.vod_name = kdata.title;
VOD.type_name = kdata.type;
VOD.vod_pic = kdata.img;
VOD.vod_remarks = kdata.remark;
VOD.vod_year = kdata.year;
VOD.vod_area = kdata.area;
VOD.vod_actor = kdata.actor;
VOD.vod_director = kdata.director;
VOD.vod_content = kdata.title+'_'+kdata.des;
VOD.vod_play_from = kdata.playinfo.map(it => it.cnsite).join('$$$');
let playUrls = [];
kdata.playinfo.forEach((it) => {
let plist = it.player.map(it => it.no + '$' + it.url).join('#');
playUrls.push(plist)
});
VOD.vod_play_url = playUrls.join('$$$')
`,
搜索: `js:
let {cookie, html} = reqCookie(HOST);
rule.headers["Cookie"]=cookie;
let kjson=JSON.parse(request(input));
let kdata=[];
kjson.data.vod_all[0].show.map((it)=>{
    kdata.push({
        vod_name: it.title,
        vod_pic: it.img,
        vod_remarks: it.remark,
        vod_id: it.url
    })
});
VODS = kdata
`,
filter: {}
}