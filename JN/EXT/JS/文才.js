var rule = {
    title: '文才资源网',
    host: 'https://api.zeqaht.com',
    //homeTid: '1',
    homeUrl: '/api.php/provide/vod/?ac=detail&t=33',
    detailUrl: '/api.php/provide/vod/?ac=detail&ids=fyid',
    searchUrl: '/api.php/provide/vod/?wd=**&pg=fypage',
    //url: '/api.php/provide/vod/?ac=detail&pg=fypage&t=fyclass',
    url: '/index.php/ajax/data?mid=1&tid=fyfilter&page=fypage&limit=20',//网站的分类页面链接
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    },
    filterable: 1,//是否启用筛选,
    filter_url: '{{fl.cateId}}',
    filter: {
        "1": [{ "key": "cateId", "name": "剧情", "value": [{ "n": "全部", "v": "" }, { "n": "喜剧", "v": "22" }, { "n": "动作", "v": "23" }, { "n": "科幻", "v": "30" }, { "n": "爱情", "v": "26" }, { "n": "悬疑", "v": "27" }, { "n": "奇幻", "v": "87" }, { "n": "剧情", "v": "37" }, { "n": "恐怖", "v": "36" }, { "n": "犯罪", "v": "35" }, { "n": "动画", "v": "33" }, { "n": "惊悚", "v": "34" }, { "n": "战争", "v": "25" }, { "n": "冒险", "v": "31" }, { "n": "灾难", "v": "81" }, { "n": "其他", "v": "43" }] }],
        "2": [{ "key": "cateId", "name": "剧情", "value": [{ "n": "全部", "v": "" }, { "n": "国产剧", "v": "14" }, { "n": "欧美剧", "v": "15" }, { "n": "港台剧", "v": "16" }, { "n": "日韩剧", "v": "62" }, { "n": "其他剧", "v": "68" }] }],
        "3": [{ "key": "cateId", "name": "剧情", "value": [{ "n": "全部", "v": "" }, { "n": "国产综艺", "v": "69" }, { "n": "港台综艺", "v": "70" }, { "n": "日韩综艺", "v": "72" }, { "n": "欧美综艺", "v": "73" }, { "n": "其他综艺", "v": "74" }] }],
        "4": [{ "key": "cateId", "name": "剧情", "value": [{ "n": "全部", "v": "" }, { "n": "国产动漫", "v": "75" }, { "n": "日韩动漫", "v": "76" }, { "n": "欧美动漫", "v": "77" }] }]
    },
    filter_def: {
        1: { cateId: '1' },
        2: { cateId: '2' },
        4: { cateId: '4' },
        3: { cateId: '3' }
    },
    class_name: '电影&电视剧&综艺&动漫',
    class_url: '1&2&3&4',
    //class_parse:'js:let html=request(input);input=JSON.parse(html).class;',
    //class_parse: 'json:class;',
    limit: 20,
    multi: 1,
    searchable: 2,//是否启用全局搜索,
    quickSearch: 1,//是否启用快速搜索,
    filterable: 0,//是否启用分类筛选,
    play_parse: true,
    图片替换: 'https://api.zeqaht.com=>https://obs.gduamoe.com',
    parse_url: '',
    lazy: `js:
            if(/\\.(m3u8|mp4)/.test(input)){
            input = {
            parse: 0,
            url: input,
            header: {
                "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                "Referer":"www.whbax.cn"
            }
            }
            }
            `,
    推荐: '*',
    一级: 'json:list;vod_name;vod_pic;vod_remarks;vod_id;vod_play_from',
    二级: `js:
            let html=request(input);
            html=JSON.parse(html);
            let data=html.list;
            VOD=data[0];`,
    搜索: '*',
}