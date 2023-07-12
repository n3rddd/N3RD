muban.mxpro.二级.tabs = '#y-playList .module-tab-item';
muban.mxpro.二级.desc = '.module-info-item-content:eq(3)&&Text;;;.module-info-item-content:eq(2)&&Text;.module-info-item-content:eq(0)&&Text';
var rule={     
    title:'布雷蓝光',
    模板:'mxpro',
    host:'https://fabu.bulei.cc',
    hostJs:'let html=request(HOST,{headers:{"User-Agent":PC_UA}});let src=jsp.pdfh(html,"li:eq(0)&&a&&href");HOST=src',
    homeUrl:'/index.php/label/new.html',
    //url:'/index.php/vod/type/id/fyclass.html',
    url:'/index.php/vod/type/id/fyclass/page/fypage.html',

    headers: {//网站的请求头,完整支持所有的,常带ua和cookies
                "Cookie": "PHPSESSID=rikmngsg39hgn1dc3urfbo8cu0", 
                //"Cookie": "PHPSESSID=l0g5372u1khuo2g7fhldl7a1j6",
                "User-Agent": "PC_UA"
            },
    
    searchUrl:'/index.php/vod/search/page/fypage/wd/**.html',
    class_parse: '.navbar-items li:gt(1):lt(10);a&&Text;a&&href;/(\\d+).html',
    lazy:`js: var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
    var url = html.url;
    fetch_params.headers["User-Agent"]=MOBILE_UA;
    if (html.encrypt == '1') {
        url = unescape(url)
    } else if (html.encrypt == '2') {
        url = unescape(base64Decode(url))
    }
    if (/m3u8|mp4/.test(url)) {
        input = url
    } else {
        input
    }`
    ,
    pagecount:{"1":1,"2":1,"3":1,"4":1,"5":1,"21":1,"22":1},
    搜索: 'body .module-item;.module-card-item-title&&Text;.lazyload&&data-original;.module-item-note&&Text;a&&href;.module-info-item-content&&Text',
}