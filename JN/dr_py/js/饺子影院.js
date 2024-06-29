var rule = {
    模板: '首图',
    title: '饺子影院',
    host: 'https://www.jiaozi.me',
    url: '/mlist/fyclass-fypage.html',
    searchUrl: '/search.php?page=fypage&searchword=**&searchtype=',
    class_parse: '.myui-header__menu&&li:gt(0):lt(5);a&&Text;a&&href;.*/(.*?).html',
}