var rule = {
  title: '免费电影vip',
  host: 'http://www.ifblog.cn/',
  url: '/vtshow/fyclass--------fypage---.html',
  searchUrl: '/search/**----------fypage---.html',
  searchable: 2,
  quickSearch: 0,
  filterable: 0,
  headers: {
    'User-Agent': 'UC_UA',
  },
  class_parse: '.header_uplist li:gt(0):lt(5);a&&Text;a&&href;.*/(.*?).html',
  play_parse: true,
  lazy: '',
  limit: 6,
  推荐: 'ul.dgifblog-vodlist.clearfix;li;a&&title;.lazyload&&data-original;.remark-tag&&Text;a&&href',
  double: true,
  一级: '.dgifblog-vodlist li;a&&title;a&&data-original;.remark-tag&&Text;a&&href',
  二级: {
    title: 'h1&&Text;.typeaclsdes&&Text',
    img: '.lazyload&&data-original',
    desc: '.stui-content__detail p:eq(0)&&Text;.stui-content__detail p:eq(1)&&Text;.stui-content__detail p:eq(2)&&Text',
    content: '.clearfix p&&Text',
    tabs: '.carousel_playlist',
    lists: '.dgifblog-content__playlist:eq(#id) li',
  },
  搜索: '.dgifblog-vodlist__media li;a&&title;.lazyload&&data-original;.remark-tag&&Text;a&&href',
  
}