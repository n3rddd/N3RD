muban.mxpro.二级.desc = '.module-info-item:eq(4)&&Text;;;.module-info-item-content:eq(1)&&Text;.module-info-item-content:eq(0)&&Text';
muban.mxpro.二级.tab_text = 'body--small&&Text';
var rule = {
    title: 'voflix',
    模板: 'mxpro',
    host: 'https://voflix.fun',
    homeUrl: '/label/new.html',
    url:'/vodshow/fyclass--------fypage---.html',
    tab_remove:['夸克网盘'],
    class_parse: '.navbar-items&&li;a&&Text;a&&href;/(\\d+).html',
	    lazy: $js.toString(() => {
        input = {
            parse: 1,
            url: input,
            js: 'document.querySelector("#playleft iframe").contentWindow.document.querySelector("#player").click()',
        }
    }),

    // searchUrl:'/search/**----------fypage---.html',
    searchUrl: '/index.php/ajax/suggest?mid=1&wd=**&limit=50',
    detailUrl: '/detail/fyid.html', //非必填,二级详情拼接链接
    搜索: 'json:list;name;pic;;id',
}