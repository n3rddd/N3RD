var rule = {
    模板: '自动',
    title: 'FreeOKLOL',
    host: 'https://www.freeok.lol',
    url: '/vodshow/id/fyclass/page/fypage.html',
    searchUrl: '/vodsearch**/page/fypage.html',
    class_parse: '.navbar-items li:gt(0):lt(8);a&&Text;a&&href;/.*/(.*?).html',
    二级: {
        title: 'h1&&Text;.module-info-tag-link:eq(2)&&Text',
        img: '.lazyload&&data-original',
        desc: '.module-info-item-content:eq(3)&&Text;.module-info-tag-link:eq(0)&&Text;.module-info-tag-link:eq(1)&&Text;.module-info-item:eq(2)--span&&Text;.module-info-item:eq(1)--span&&Text',
        content: '.module-info-introduction&&Text',
        tabs: '.module-tab-item',
        lists: '.module-play-list:eq(#id) a',
    },
    搜索: 'body .module-item;.module-card-item-title&&Text;.lazyload&&data-original;.module-item-note&&Text;a&&href;.module-info-item-content&&Text',
}