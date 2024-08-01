var rule = {
author: '小可乐/240701/第一版',
title: '疯狗电影',
类型: '影视',
host: 'https://m.itvbox3.com',
hostJs: '',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/',
url: '/list-select-id-fyclass-fyfilter-p-fypage.html',
filter_url: 'type-{{fl.class}}-area-{{fl.area}}-year-{{fl.year}}-star--state--order-{{fl.by or "addtime"}}',
detailUrl: '',
searchUrl: '/vod-search-wd-**-p-fypage.html',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '电影&剧集&综艺&动漫',
class_url: '1&2&4&3',
filter_def: {},

play_parse: true,
lazy: `js:
let kcode = JSON.parse(request(input).match(/var cms_player=(.*?);</)[1]);
let kjx = kcode.jiexi;
let kurl = kcode.url;
if (/\\.(m3u8|mp4)/.test(kurl)) {
input = { jx: 0, parse: 0, url: kurl };
} else {
input = { jx: 0, parse: 1, url: kjx+kurl };
}
`,

limit: 9,
double: false,
推荐: '*',
一级: '.col-xs-4 .image;img&&alt;img&&data-original;.continu&&Text;a&&href',
二级: {
title: 'h2:eq(0)&&a&&Text;dl&&dd:eq(2)&&Text',
img: '.media-left&&img&&data-original',
desc: 'h2:eq(0)&&span&&Text;dl&&dd:eq(-2)&&Text;dl&&dd:eq(-3)&&Text;dl&&dd:eq(0)&&Text;dl&&dd:eq(1)&&Text',
content: '.vod-nav-content&&Text',
tabs: 'h2:has(.glyphicon-facetime-video)',
tab_text: 'body&&Text',
lists: '.ff-playurl:eq(#id)&&a',
list_text: 'body&&Text',
list_url: 'a&&href',
},
搜索: '*',

filter: 'H4sIAAAAAAAAA+2YW28aRxTH3/kY++xKuzgXk68S5YE2lho1jao4qWRZlrAJBFOHmxywy/pWX+MaB2ziwlLgy+zMwrfowJzLoDYrVLlpHnjjd87OmTlnmP+Z3ZWI5ViPHkdWrB8Wl61H1nfP40tL1pz1Iv7jokKxcSaTKcU/x5+/VobHK9aLkTl1Pkyej8wKrNU5sJZd9TxYAdAXZBoQiAF9cq0gE2XwAVDM7LnfdTGmBop5VhTtDsbUQONo4Qw0X2bb9zZwPg3oG9ROxeYF+ABovuzHoIs+AGOdwVaH1zkC8p285XUC0Fpqp37vANeigcalS8OdDzhOA43bu1Arx3EayLd+GZSL6NNAvmRWrv+KPg2UXycvUi3MTwP6hrsluX0CPgCKWX472PAwpgbKoXcVbH0S3QamQUxP5I8HR7RTGsiXS4v8Nfo00E71C6rOuFMauHKu3C1S5cZAvjf94HfMBIAq0C0GHXdiwROm1Serc3RU4i8X48ZJceti05v2pKRT6nla3xhoDb2cqHZxdg20C6c7svURd0ED17Eu2z2q4xho3P4HjglAu1c5ke4l7p4G8t2853EAVP9fGuwD4F3/g30AHLNuxqxPjHtXF94pjtNA4y7PZBP/CwDo81uueFfxPfxjM1Pk1K3fQY0BmNjN5cX4S95NWbkdVppT7mbUjt4D2/inYZ9n+7xpj7I9atodtjum3Wa7bdidGNnVT8O+wPYF0/6Q7Q9N+wO2PzDt99l+37Rzvo6Zr8P5Oma+DufrmPk6nK9j5uvY30Rtm5O27ZGNHojZot30O0fgd2IxlX6MCyCrTVlB4XQWbOVdiE1u97fLxmbnSsLL/22zpZsY9ItBsiZLNYj1/bNXSzyLm5Dlut/Kym0U8PjTp6+eqZh0ltfbg0976kFxjH/N1z+NFhJ5MhexonfWeEMkNKzZaR0Xa7cimZ+QdjBN09jF1a3wsD4AUzbMzzb2sIYZ1tjD2kVYc/Pbh9wuALhhpuQOSi4Azfc+zU0YwGglXDOAqcXoP2otYW3g37aWsPYR1srC2kBYa1FHTmQPxO4h3TeQZ1I/k/qvVerv3ZXUDxMbwVkCj6kGU6re7BtSpYCO1FV/UM/gkdJA40o1mcUbMQAf75RsoWwCsJzc+O0CyckYjKM/PMK1AJDPuxBXe+jTwPt5bbxLaKBxW/uySe97GmhcqyUzed8r8TvBhInq0PxNiT/WQQPFaKwP1jZxtIYvIctKapWo0qrHYMirEmqW1xEYN2JVWb4Rj2AmdDOh+z+Fbv6uhC5MzMI+/KjcBocokAAUM3ceFNIYUwP5CnvBJX000cCH9/MfYgaF3UEO79cAFPPgUFSxzgDT3H+l6xkfdzRM89kj7K4v6qpMTZxPg+k7uTF8Cqiexz3/T9xoAL5v74tMle7bY6A7tXctatgcAChmNSt3UOQBuC4N0a9QXcbwRe7N1a7v0TuOhmnuuP8owrOb6Eygv0aBjqz+BQJ/H07wFwAA'
}