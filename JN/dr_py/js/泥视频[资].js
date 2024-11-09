var rule = {
author: '小可乐/2408/第一版',
title: '泥视频[资]',
类型: '影视',
host: 'https://nivod.fun',
hostJs: '',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/',
url: '/index.php/api/vod?type=fyfilter&page=fypage',
filter_url: '{{fl.cateId}}&{{fl.area}}&{{fl.by}}&{{fl.class}}&{{fl.lang}}&{{fl.letter}}&{{fl.year}}',
detailUrl: '/index.php/vod/detail/id/fyid.html',
searchUrl: '/index.php/vod/search/page/fypage/wd/**.html',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '电影&剧集&综艺&动漫&短剧',
class_url: '1&2&3&4&97',
filter_def: {
1: {cateId: '1'},
2: {cateId: '2'},
3: {cateId: '3'},
4: {cateId: '4'},
97: {cateId: '97'}
},

play_parse: true,
lazy: `js:
let kcode = JSON.parse(request(input).match(/var player_.*?=(.*?)</)[1]);
let kurl = kcode.url;
if (/\\.(m3u8|mp4)/.test(kurl)) {
    input = { jx: 0, parse: 0, url: kurl }
} else {
    input = { jx: 0, parse: 1, url: input }
}
`,

limit: 9,
double: false,
推荐: '.public-list-exp;a&&title;img&&data-src;.public-list-prb&&Text;a&&href',
一级: `js:
let furl=input.split("?")[0];
let fbody=input.split("?")[1];
let timestamp=Math.round(new Date/1e3).toString();
let key=md5("DS"+timestamp+"DCC147D11943AF75");
fbody=fbody+"&time="+timestamp+"&key="+key;
fetch_params.body=fbody;
let fhtml=post(furl,fetch_params);
let fdata=JSON.parse(fhtml);
VODS = fdata.list
`,
二级: {
title: '.this-desc-title&&Text;.this-desc-tags&&Text',
img: '.this-pic-bj&&style',
desc: '.this-desc-info&&span:eq(-1)&&Text;.this-desc-info&&span:eq(1)&&Text;.this-desc-info&&span:eq(2)&&Text;.this-info--strong:eq(1)&&Text;.this-info--strong:eq(0)&&Text',
content: '.top26--em&&Text',
tabs: '.anthology-tab&&a',
tab_text: 'body--span&&Text',
lists: '.anthology-list-play:eq(#id)&&a',
list_text: 'body&&Text',
list_url: 'a&&href',
},
搜索: '.public-list-exp;a&&title;img&&data-src;.public-list-prb&&Text;a&&href',

filter: 'H4sIAAAAAAAAA+2aWU8jRxDH3/kYfiYSY06v5Ie9l73vU/vg3VjJKoRIQCIhhGTONZcNq8VegwOsOAwsjs0hBGOMv4x7Zvwt0kO3q7saZccRCCVSvyD5/ytXt2uamn+Npq/OZ/guvanr8/0S7vVd8r0P9YTbf/TV+zpDv4bpZ3u7QBYm6Oc/Qh2/U+FNn6+TymRkvTK07sr0g+Hrr+fyWMYaGrHHPlaJhBJpSgVqFWR8vVxMC9ICxI5uo3RtQKyBaSuSkBZqEF/KzJDDgkABeSH7s0T80krmJinOSkhaKvqlbI5JiCZ8218vKtYR6u4WBWMl+H7BlHpx9SRRkEu4bDiCSbh8OIJJ8AuGxq3BORTBJVxoFMElXHCcg0mQYzxnFzdxDibBTkc/VVIbeKdMgojVj/Ta4QgmwT4Gt+zEDN4Hk/D1x/tgEqzy1z4xs3gVJuGTotbUlSAiNkriOziCSf90pPhWQMXnC/8iJlUjKou75cNpFMEldBBDXeGQdA7TeTJp1ngOywdZMl8kK5lKapQzN1sQ6fDDjmNUlMO4Iva7oQRwBQLWUtZBDgUwBaobz1uHx3IAV6BoyVUrvSUHcKUa4ExsK3vgCmTYzSsBXIEMqyU7nrXHUigJiOKoLFkTJVoitFsQxXKzp5ablZcjU3lirqEkTIEMx7s0IYlulM05lEfW0YHoCHX+JA6Ek8s665FaG9N8kcZz1c0T5IpUXyWAK3BKdlaUAK7AIUgWyVRSiRGidJjUGKZIR0EJ4AqqRW841CVqYSX3K8m9Gmvhb/A3cc3NEjz5LMFGBTbK0K9AvwwNBRoybFBggwSNAIZGQIZtCmyTYasCW2XYosAWGTYrsFmGSoUMuUKGUiFDrpChVMiQK2QoFTLkChlKhVwPgI5/uKcnLF10kk1auakaL/rl6oE6SRK8DOAKBlcAXMXgKoBrGFwDcB2D6wBuYHADwE0MbgK4hcEtAO0YtAO4jcFtAHcwuAPgLgZ3AdzD4B6A+xjcB/AAgwcAHmLwEMAjDB4BeIzBYwBPMHgC4CkGTwE8w+AZgOcYPAfwAoMXAF5i8BLAKwxeAXiNwWsADT8EMHIFdNDf9UqdLfaJmPFTh9xKR6xEnud51xvs+UCjoYOmI/ZQVsCfP/R0i0afGybRUQG73//WFXbXr3tbX+fzn3V2EP/trtEAp9sm2pJrLoQuOpLrKYQuWgrt/pIumpR7exe6NJjEZV3y/Qc5Sff/t0y/t9k+F6PsOVp4Dw7eZvv8jDIZLtnfVvFaTJJMnbgiLIJLtVt/Z3ibxJftTASnARV+V3qxbJpqnFBrHyWs7KQTXcC/nEl6ANADgB4A9ACgBwA9AOgBQA8AFz4ANJ51AJCM+1aG+gi7cOSMmVXbLT28P/EgiAZER3TNejyPqWgV9H5A7xmYnqOhr9noedr6mq1lrZZ5e9AZmMTGkUn/wp57P9f3HGi8hxFv6/6dp+DVVRL5ShJbdy5pm6xtsrbJ2iZrm6xtsrbJ2iZfuE1uOqtNFn2CmVkyvm4dfauaWdVEYyp998QmYyraE711lc0Mpi3nZ5NppDW8iO0Zk+Be6PlEmtbf+ar4bCbBKrF1e3oUr8IkiJhesLcUM8okKITniyrO9J9ODD+L5hKssvSVzGNjzSXhiDxf3EmbVvQLzsEk2Edpmn4H74NJkMP7qXmelngP74NJcsTq7qkIKsF1WTkuH+FXjLgEOWKLJDqPczAJzLW5Q7LY4HMJVpkft1ImXoVJoqbbpJRUanoi6RFAjwB6BNAjgB4B9AigRwA9Alz4CBBoPesMEBANqPJxyv68aFETBnfKgOhd9kbJ2R+nDq5cWK5S0fbsWJ7q9AYnHtoaDaJlkviUU9yyo0UrId6ul16XWd21BiasSMFZHgAsGlEluUk25uhfe60AWDSxylCRHAw6wzPW3gLgJmntFWd5pFxIlY+XADf/P29Pur/q/qr76wX117r+vwH9RvHdyTQAAA=='
}