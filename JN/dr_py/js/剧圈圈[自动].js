var rule = {
    模板: '自动',
    模板修改: $js.toString(() => {
        Object.assign(muban.自动.二级, {
            tab_text: 'div--small&&Text',
        });
    }),
    title: '剧圈圈[自动]',
    host: 'https://www.jqqzx.cc/',
    url: '/vodshow/id/fyclass/page/fypage.html',
    searchUrl: '/vodsearch**/page/fypage.html',
    class_parse: '.navbar-items li:gt(1):lt(8);a&&Text;a&&href;.*/(.*?)\.html',
    cate_exclude: '今日更新|热榜',
}