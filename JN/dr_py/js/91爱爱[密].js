var rule={
            title: '91',
            host: 'https://101.91aiai110.com',
            url: '/list/fyclass-fypage.html',
            searchUrl: '/search/**----------fypage---.html',
            searchable: 2,//是否启用全局搜索,
            quickSearch: 0,//是否启用快速搜索,
            filterable: 0,//是否启用分类筛选,
 class_name:'国产精品&中文字幕&日韩精品&欧美精品&精彩动漫&情色小说',
 class_url:'3&4&5&6&7',          
            play_parse: true,
            lazy: `js:
let kcode=jsp.pdfh(request(input).match(/<iframe(.*?)</iframe>/)[1]);
let kurl=kcode.match(/url=(.*?)\"/)[1];
if (/m3u8|mp4/.test(kurl)) {
input = { jx: 0, parse: 0, url: kurl }
} else {
input = { jx: 0, parse: 1, url: rule.parse_url+kurl }
}`,
            limit: 6,
            推荐: '.detail;a&&title;img&&data-src;.module-item-text&&Text;a&&href',
            double: true, // 推荐内容是否双层定位
            一级: '.col-6;.detail&&h6&&a a&&Text;.lazyload&&data-src;.module-item-text&&Text;a&&href',
            二级: '*',
            搜索: '.video-img-box .img-box;a&&Text;.lazyload&&data-src;.label&&Text;a&&href',
        }