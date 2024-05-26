Object.assign(muban.mxpro.二级, {
    tab_text: 'div--small&&Text',
});
var rule = {
    模板: 'mxpro',
    title: '爱看影院',
    host: 'https://www.92kyy.com',
    cate_exclude: '今日更新',
    url: '/vodshow/fyclass--------fypage---.html',
    searchUrl: '/vod-s/**----------fypage---.html',
    class_parse: '.navbar-items li:gt(0):lt(8);a&&Text;a&&href;.*/(\\d+)',
    tab_exclude: '排序',
}