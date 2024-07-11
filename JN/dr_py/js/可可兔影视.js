Object.assign(muban.海螺3.二级, {
    title: ';.hl-col-xs-12.hl-col-sm-4:eq(2)&&Text',
    desc: '.hl-text-conch:eq(4)&&Text;.hl-col-xs-12.hl-col-sm-4&&Text;.hl-col-xs-12.hl-col-sm-4:eq(1)&&Text;.clearfix:eq(8)&&.hl-col-xs-12:eq(3)&&Text;.clearfix:eq(8)&&.hl-col-xs-12:eq(4)&&Text',
    content: '.clearfix:eq(8)&&.hl-col-xs-12:eq(-1)&&Text',
});
var rule = {
  title: '可可兔影视',
  模板: '海螺3',
  host: 'https://abc.qilin8.com',
  searchUrl: '/index.php/vod/search/page/fypage/wd/**.html',
  url: '/index.php/vod/show/id/fyclass/page/fypage.html',
  class_parse: '.hl-menus&&li--em;a&&Text;a&&href;id/(.*?).html',
  cate_exclude: '直播',
}