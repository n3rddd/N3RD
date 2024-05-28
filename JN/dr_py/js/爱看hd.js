Object.assign(muban.mxpro.二级, {
    tab_text: 'div--small&&Text',
});
var rule = {
    模板: 'mxpro',
    title: '爱看hd',
    host: 'https://www.aikanhd.vip/',
    headers: {'User-Agent': 'IOS_UA'},
    class_parse: '.navbar-items li:gt(0):lt(10);a&&Text;a&&href;.*/(\\d+)',
    cate_exclude: '今日更新|排序|福利区',
    url: '/vodshow/fyclass--------fypage---.html',
    searchUrl: '/vodsearch/**----------fypage---/',
    tab_exclude: '排序',
}