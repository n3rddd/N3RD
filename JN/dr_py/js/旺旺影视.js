var rule = {
    title: '旺旺影视',
    host: 'https://www.wwgz.cn',
    url: '/vod-type-id-fyclass-pg-fypage.html',
    searchUrl: '/vod-search-pg-fypage-wd-**.html',
    searchable: 2,
    quickSearch: 0,
    headers: {
        'User-Agent': 'PC_UA',
    },
    timeout: 5000,
    class_parse: '.nav_c a:gt(0):lt(6);a&&Text;a&&href;/vod-type-id-(\\d+)-pg-1.html',
    cate_exclude: '',
    play_parse: true,
    lazy: $js.toString(() => {
        input = {
            parse: 1,
            url: input,
            js: 'document.querySelector("#playleft iframe").contentWindow.document.querySelector("#player").click()',
        }
    }),
    double: false,
    推荐: '.list_06 li;a.b_a&&title;img&&src;a.b_a font&&Text;a&&href;.f_c&&Text',
    一级: '.list_01 li;a.b_a&&title;img&&src;.nam&&Text;a&&href',
     二级: {
        title: 'h1&&Text;.d_z_y font:eq(2)&&Text',
        img: 'img&&src',
         desc: '.content_detail:eq(1)&&li:eq(1)&&Text;.d_z_y font:eq(5)&&Text;.d_z_y font:eq(2)&&Text;.d_z_y font:eq(1)&&Text;.d_z_y font:eq(0)&&Text',
        content: '.jjie&&Text',
        tabs: 'h2 span',
        lists: '.soyurl:eq(#id) li',
            },
    搜索: '*',
}