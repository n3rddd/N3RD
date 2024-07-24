var rule = {
    title: '0855影视',
    模板: '海螺3',
    host: 'https://www.085518.com',
    searchUrl: '/vod/search/page/fypage/wd/**.html',
    url: '/vod/show/id/fyclass/page/fypage.html',
    class_parse: 'body&&.hl-nav li:gt(0);a&&Text;a&&href;.*/(.*?)/',
    cate_exclude: '伦理|明星|专题|最新|排行|美图',
    二级: {
        "title": ".hl-full-box li--em&&Text;.hl-full-box li:eq(4)--em&&Text",
        "img": ".hl-lazy&&data-original",
        "desc": ".hl-full-box li:eq(1)--em&&Text;.hl-full-box li:eq(2)--em&&Text;.hl-full-box li:eq(5)--em&&Text;.hl-full-box li:eq(6)--em&&Text;.hl-full-box li:eq(3)--em&&Text",
        "content": ".hl-col-xs-12.blurb--em&&Text",
        "tabs": ".hl-tabs&&a",
        "lists": ".hl-plays-list:eq(#id)&&li"
    },
}