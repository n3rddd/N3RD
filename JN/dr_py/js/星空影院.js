var rule = {
    title: '星空影院',
    host: 'http://www.591sky.com',
    url: '/vod/list/fypage/fyclass/0/0/0/0/0/0',
    searchUrl: '/public/auto/search1.html?keyword=**&page=fypage',
    searchable: 1,
    quickSearch: 1,
    filterable: 0,
    filter: '',
    filter_url: '',
    filter_def: {},
    headers: {
        'User-Agent': 'PC_UA',
    },
    timeout: 5000,
    class_parse: '.swiper-wrapper&&li;a&&Text;a&&href;/vod/1/(.*?)/0/0/0/0/0/0',
    cate_exclude: '',
    play_parse: true,
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
    double: true,
    推荐: '*',
    一级: '.public-list-box; img&&alt; img&&data-src; .public-list-prb&&Text; a&&href',
    二级: {
        title: 'h3&&Text; .span&&Text',
        img: 'img&&data-src',
        desc: '主要信息; .this-desc-info span:eq(1)&&Text; .this-desc-info span:eq(2)&&Text; .this-info:eq(1)&&Text; .this-info&&Text',
        content: '.cor3&&Text',
        tabs: '.anthology-tab a',
        lists: '.anthology-list-play:eq(#id) li',
        tab_text: 'body&&Text',
        list_text: 'body&&Text',
        list_url: 'a&&href'
    },
    搜索: '.public-list-box; img&&alt; img&&data-original; .public-list-prb&&Text; a&&href',
}
