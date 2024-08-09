var rule = {
  title: '天龙电影网',
  host: 'https://www.tlyy8.com/',
  url: '/tlyy/fyclass/page/fypage.html',
  searchUrl: '/tlso**/page/fypage.html',
  searchable: 2,
  quickSearch: 0,
  filterable: 0,
  headers: {
    'User-Agent': 'UC_UA',
  },
  class_parse: '.stui-header__menu li:gt(0):lt(5);a&&Text;a&&href;.*/(.*?).html',
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
  推荐: 'ul.stui-vodlist.clearfix;li;a&&title;.lazyload&&data-original;.pic-text&&Text;a&&href',
  double: true,
  一级: '.stui-vodlist li;a&&title;a&&data-original;.pic-text&&Text;a&&href',
  二级: {
    title: '.stui-content__detail .title&&Text;.stui-content__detail p:eq(-2)&&Text',
    img: '.stui-content__thumb .lazyload&&data-original',
    desc: '.stui-content__detail p:eq(0)&&Text;.stui-content__detail p:eq(1)&&Text;.stui-content__detail p:eq(2)&&Text',
    content: '.detail&&Text',
    tabs: '.stui-pannel__head li',
    lists: '.stui-content__playlist:eq(#id) li',
  },
  搜索: 'ul.stui-vodlist__media:eq(0),ul.stui-vodlist:eq(0),#searchList li;a&&title;.lazyload&&data-original;.text-muted&&Text;a&&href;.text-muted:eq(-1)&&Text',
  搜索1: 'ul.stui-vodlist&&li;a&&title;.lazyload&&data-original;.text-muted&&Text;a&&href;.text-muted:eq(-1)&&Text',
  搜索2: 'ul.stui-vodlist__media&&li;a&&title;.lazyload&&data-original;.text-muted&&Text;a&&href;.text-muted:eq(-1)&&Text',
}