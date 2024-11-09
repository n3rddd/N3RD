var rule = {
  title: '电影兔',
  host: 'https://www.dianyingtu.com',
  class_name: '电影&电视剧&综艺&动漫&微电影&短剧',
  class_url: 'dianying&dianshiju&zongyi&dongman&weidianying&dianshiju/duanju',
  searchUrl: '/search/**/page/fypage',
  searchable: 2,
  quickSearch: 0,
  headers: {
    'User-Agent': 'MOBILE_UA',
  },
  url: '/fyclass/page/fypage',
  filterable: 0,
  filter_url: '',
  filter: {},
  filter_def: {},
  detailUrl: '',
  play_parse: true,
  lazy: '',
  limit: 6,
  推荐: '*',
  一级: '.movie-item li;a&&title;.lazy-load-img&&_src;.rs-state&&Text;a&&href',
  二级: {
    title: 'h1&&Text',
    img: '.lazy-load-img&&_src',
    //主要信息;年代;地区;演员;导演,
    desc: '.movie-txt&&p:eq(2)&&Text;.movie-txt&&p:eq(4)&&Text;.movie-txt&&p:eq(5)&&Text;.movie-txt&&p:eq(1)&&Text;.movie-txt&&p:eq(0)&&Text',
    content: '.content--p&&Text',
    tabs: '.tab-list li',
    lists: '.episodes-list:eq(#id)&&a'
  },
  搜索: '.collect-list.mt15 li;h5&&Text;.lazy-load-img&&_src;.rstype&&Text;*;.line-two&&Text'
}