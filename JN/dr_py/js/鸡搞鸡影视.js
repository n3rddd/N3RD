var rule = {
  title: '鸡搞鸡影视',
  host: 'https://www.jigaoji.com',
  url: '/vodshow/fyclass/page/fypage.html',
  searchUrl: '/vodsearch.html?wd=**&submit=',
  searchable: 2,
  quickSearch: 0,
  filterable: 0,
  headers: {
    'User-Agent': 'MOBILE_UA',
  },
  class_parse: '.myui-header__menu li.hidden-sm:gt(0):lt(5);a&&Text;a&&href;.*/(.*?)/',
  play_parse: true,
  lazy: $js.toString(() => {
        let html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        let url = html.url;
        if (html.encrypt == '1') {
            url = unescape(url)
        } else if (html.encrypt == '2') {
            url = unescape(base64Decode(url))
        }
        if (/\.m3u8|\.mp4/.test(url)) {
            input = {
                jx: 0,
                url: url,
                parse: 0
            }
        } else {
            input
        }
    }),
  limit: 6,
  推荐: 'ul.myui-vodlist.clearfix;li;a&&title;a&&data-original;.pic-text&&Text;a&&href',
  double: true,
  一级: '.myui-vodlist li;a&&title;a&&data-original;.pic-text&&Text;a&&href',
  二级: {
    title: '.myui-content__detail .title&&Text;.myui-content__detail p:eq(-2)&&Text',
    img: '.myui-content__thumb .lazyload&&data-original',
    desc: '.myui-content__detail p:eq(0)&&Text;.myui-content__detail p:eq(1)&&Text;.myui-content__detail p:eq(2)&&Text',
    content: '.content&&Text',
    tabs: '.nav-tabs:eq(0) li',
    lists: '.myui-content__list:eq(#id) li',
  },
  搜索: '#searchList li;a&&title;.lazyload&&data-original;.text-muted&&Text;a&&href;.text-muted:eq(-1)&&Text',
}