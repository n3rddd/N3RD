// 搜索验证
var rule = {
    title:'B站影视',
    // host:'https://bzhanys.com',
    host:'https://bzhanyy.com',
    url:'/index.php/vod/show/id/fyclass/page/fypage.html',

    searchable:2,//是否启用全局搜索,
    quickSearch:0,//是否启用快速搜索,
    headers:{
        'User-Agent':'PC_UA'
    },
    class_parse: '.fixed-nav&&.flex:lt(4);li&&Text;li&&data-id;(\\d+)',
    play_parse:true,
	    lazy: $js.toString(() => {
        input = {
            parse: 1,
            url: input,
            js: 'document.querySelector("#playleft iframe").contentWindow.document.querySelector("#player").click()',
        }
    }),

    limit:6,
    推荐:'*',
    // 推荐:'.movie-list-body&&.movie-list-item;.movie-title&&Text;.Lazy&&data-original;.movie-rating&&Text;a&&href',
    一级:'.movie-list-body&&.movie-list-item;.movie-title&&Text;.Lazy&&data-original;.movie-rating&&Text;a&&href',
    // 一级:'json:list;vod_name;vod_pic;vod_score;vod_id',
    二级访问前:'log(MY_URL);MY_URL=MY_URL.replace("/play/","/detail/").replace("/sid/1/nid/1","");log(MY_URL)',
    二级:{
        "title":"h1&&title;.scroll-content a:eq(0)&&Text",
        "img":".poster&&img&&src",
        "desc":";.scroll-content a:eq(1)&&Text;.scroll-content a:eq(2)&&Text;.starLink&&Text;.cr3:eq(0)&&Text",
        "content":".detailsTxt--div&&Text",
        "tabs":".swiper-wrapper&&a",
        "lists":".content_playlist:eq(#id)&&li"
    },

     searchUrl:'/index.php/vod/search/page/fypage/wd/**.html',
	//searchUrl:'/index.php/ajax/suggest?mid=1&wd=**&limit=50',
	detailUrl:'/index.php/vod/detail/id/fyid.html',
    搜索:'.movie-list-body&&.vod-search-list;*;*;.getop&&Text;*',
	//搜索:'json:list;name;pic;;id',
}