var rule = {
  类型:'影视',//影视|听书|漫画|小说
  title:'M1949电影',
  host:'https://sosexxx.com/',
  url:'/index.php/vod/type/id/fyclass/page/fypage.html',
  searchUrl:'/index.php/vod/search.html?wd=**',
  searchable:2,
  quickSearch:0,
  filterable:1,
  filter:'',
  filter_url:'',
  filter_def:{},
  headers:{
      'User-Agent':'MOBILE_UA',
  },
  timeout:5000,
  class_parse:'.swiper-wrapper a:gt(0):lt(5);a&&Text;a&&href;.*/(.*?).html',
  cate_exclude:'',
  play_parse:true,
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
  double:true,
  推荐: '*',
  一级:'.row li;a&&title;.pic .lazyload&&data-original;.item-status.text-overflow&&Text;a&&href',
  二级:{
    title:'h3&&a&&Text',
    img:'.pic .lazyload&&data-original',
    desc:'.row&&Text;..col-sm-6:eq(3)&&TExt;.col-xs-12.col-sm-6:eq(1)&&TExt;',
    content:'.text.text-row&&Text',
    tabs:'.playlist-tab li',
    lists:'.ewave-playlist-content:eq(#id)&&li',
    tab_text:'body&&Text',
    list_text:'body&&Text',
    list_url:'a&&href',
    list_url_prefix: '',
  },
  搜索:'*',
}