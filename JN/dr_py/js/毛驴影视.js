var rule = {
  title:'毛驴影视',
  host:'https://www.maolvys.com/',
  class_name: '电影&电视剧&综艺&动漫',
  class_url: '1&2&3&4',
  searchUrl:'/index.php/vod/search/page/fypage/wd/**.html?key=2apUOPaCaR',
  searchable: 2,
  quickSearch: 0,
  headers: {
    'User-Agent': 'MOBILE_UA',
  },
  url:'/index.php/vod/show/id/fyclass/page/fypage.html?key=2apUOPaCaR',
  filterable: 0,
  filter_url: '',
  filter: {},
  filter_def: {},
  detailUrl: '/index.php/vod/show/id/fyid.html',
  play_parse: true,
  lazy:$js.toString(()=>{
   let html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
   let url = html.url;
   if (url) {
       input = url
    }
  }),
  limit: 6,
  推荐:'.public-list-bj a;a&&title;.lazy&&data-src;.public-prt&&Text;a&&href',
  一级: '.public-list-bj a;a&&title;.lazy&&data-src;.ft2&&Text;a&&href',
  二级: {
    title: '.slide-info-title&&Text',
    img: '.lazy&&data-src',
    desc: '.slide-info&&Text;.slide-info-remarks:eq(0)&&Text;.slide-info-remarks:eq(1)&&Text;.slide-info:eq(2)--strong&&Text;.slide-info:eq(1)--strong&&Text',
    content: '#height_limit&&Text',
    tabs: '.anthology.wow.fadeInUp.animated&&.swiper-wrapper&&a',
    tab_text: '.swiper-slide&&Text',
    lists: '.anthology-list-box:eq(#id) li',
  },
  搜索: 'json:list;name;pic;en;id',
}