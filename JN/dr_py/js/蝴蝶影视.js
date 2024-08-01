var rule = {
    title: '蝴蝶影视',
    host: 'https://www.tqpipa.com', // homeUrl:'/',
    url: '/vodshow/fyclass--------fypage---.html',
    searchUrl: '/vodsearch/**----------fypage---.html',
    searchable: 2, //是否启用全局搜索,
    quickSearch: 0, //是否启用快速搜索,
    filterable: 0, //是否启用分类筛选,
    headers: { //网站的请求头,完整支持所有的,常带ua和cookies
        'User-Agent': 'MOBILE_UA', // "Cookie": "searchneed=ok"
    },
    class_parse: '.navbar-items li;a&&Text;a&&href;.*/(.*?)/',
    cate_exclude: '今日更新|热榜|直播',
    play_parse: true,
    lazy:`js:
    input = {
        parse: 1,
        url: input,
        js: ''
    };
    `,
            limit: 6,
            double: true, // 推荐内容是否双层定位
            推荐: '.tab-list.active;a.module-poster-item.module-item;.module-poster-item-title&&Text;.lazyload&&data-original;.module-item-note&&Text;a&&href',
            一级: 'body a.module-poster-item.module-item;a&&title;.lazyload&&data-original;.module-item-note&&Text;a&&href',
            二级: {
                title: 'h1&&Text;.module-info-tag-link:eq(-1)&&Text',
                img: '.lazyload&&data-original||data-src||src',
                desc: '.module-info-item:eq(-2)&&Text;.module-info-tag-link&&Text;.module-info-tag-link:eq(1)&&Text;.module-info-item:eq(2)&&Text;.module-info-item:eq(1)&&Text',
                content: '.module-info-introduction&&Text',
                tabs: '.module-tab-item',
                lists: '.module-play-list:eq(#id) a',
                tab_text: 'div--small&&Text',
            },
            搜索: 'body .module-item;.module-card-item-title&&Text;.lazyload&&data-original;.module-item-note&&Text;a&&href;.module-info-item-content&&Text',
        }