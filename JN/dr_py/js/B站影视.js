// 搜索验证
var rule = {
    title: 'B站影视',
    // host:'https://bzhanys.com',
    host: 'https://bzhanyy.com',
    // url:'/index.php/vod/show/id/fyclass/page/fypage.html',
    url: '/index.php/vod/show/id/fyfilter.html',
    // url:'/api.php/xiao/vod?type=fyclass&page=fypage&limit=24',
    filterable: 1,//是否启用分类筛选,
    filter_url: '{{fl.cateId}}{{fl.area}}{{fl.by or "/by/time"}}{{fl.class}}/page/fypage{{fl.year}}',
    filter: 'H4sIAAAAAAAAA+2Y7W7aSBSG78W/IzEmbT56B3sNq/6gXaRW7XalJLtSVFVKN4HFJAUatUlZaD62TSBVSEyDuolp4GY8Y7iLHZjxmTOHVYvUaKWt/NPPObwzfm2f1+ap4zp3fnzqPMquOnec+5mV7A8/OTPOk8zPWXkctbt8b1Me/5Z5/Gt23PhEYp5rDtebIywPXOfZjMY7de41NJ4DHBXaYj2n8Txg8bwi1nY0XjDdjZf8qqvxotH2GkbEZUal8CYMvJibvUTF8+j6Q8zTpr91HPYONE+j/uADv34dc6MfVfKDsyDy/ohL8rzujorKsMxSNmPs4nWfbwVftsuc0fvGsJrXNDUSSmkUdwyPq+Ly3OrQCDTKvrjq2RoKwf57JV67tjo0AkcuXtMOjeKOwWabdmgEGrtHon5qaygE57J/QjU0gnPp/U07NDI79Sd36lsaL3weHNsaCoHGRlm6zAsntgxQOOejflRuRV7VPm2gsGLxQGz25Y/tRYFCX+5T2N2xmxTCt9NqNrOEbqerTth9N+XtlGbpW7H8SCY1Bqg6S6uzuJqm1TSuurTq4iqjVYaq7iKpuou4ukCrC7g6T6vzuDpHq3O4eptWb+Mq9crFXrnUKxd75VKvXOyVS71ysVcu9crFXjHqFcNeMeoVw14x6hXDXjHqFcNeMeoVw14x6hXDXjHqFcNeMeoVw14x6hXDXjHqlQT4Ybm3ah4VUdrmQXniURFbntj9NNztxEr3VlMrD+UvYBxseWEQCP8VanjwcGUZNwzON3ghjxqW7/+ylB1t5e6Mk/7G9DR2yDkWBg0ToOiekyNfjnVUMhdAjtnRHDUlc+XEaWM06k3p5qIrn5P99jBTaPpxfxPh9vXYmSb+vhYqU8Tfji8nPn97aMsATUIgCYEkBL7fEJjFIfA4s7yMHl/4bpni8R2ueVFjLV5krJTSDLaynhMb+3aLZjCvzvoDv2C3aAYq2y1RPCIqipnZmhOXl6RFMTPkL8KrCtmuYmj+Dt+R7WqGv7zO9kiLYrCX2seBF5C9KAYqr/ZFp0tUFDMpeikK5TDY5sUm0cIVsLHzV9QtExsVA8X274PnW0RLsf8sadW7gR08CtmvCDQlR8h+U7A7FEpyKcmlJJf+r7l064ZyaYrQsf62i+evYtCy3hocknTTDBYqNaNKniykGLRU9qLTl6RFMTM0t4fVE7tFMxjulbeDkme3aAYLHRzyWosspBgsVGyG13WykGKgUg9E4Q1RUQz20q9MJJJmoIL/5YxVFIO9+NLsDtmLYrjl6GKyRTK4Ru974ec/yTVSDFRK+7xQIyqKxS1h8JG3yIuBZrBQrSiqJNI1M+62eX+Xujtm//5BpVsmv6i+JYDHX+V2ACs0/UfoF+I1+TBMAjgJ4O80gJ/9A8iZ+RtdGwAA',
    filter_def: {
        1: {cateId: '1'},
        2: {cateId: '2'},
        3: {cateId: '3'},
        4: {cateId: '4'}
    },
    searchable: 2,//是否启用全局搜索,
    quickSearch: 0,//是否启用快速搜索,
    headers: {
        'User-Agent': 'MOBILE_UA'
    },
    class_parse: '.fixed-nav&&.flex:lt(4);li&&Text;li&&data-id',
    play_parse: true,
    lazy: `js:
        var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        var url = html.url;
        if (html.encrypt == '1') {
            url = unescape(url)
        } else if (html.encrypt == '2') {
            url = unescape(base64Decode(url))
        }
        if (/\\.m3u8|\\.mp4/.test(url)) {
            input = {
                jx: 0,
                url: url,
                parse: 0
            }
        } else {
            input
        }
    `,
    limit: 6,
    推荐: '*',
    // 推荐:'.movie-list-body&&.movie-list-item;.movie-title&&Text;.Lazy&&data-original;.movie-rating&&Text;a&&href',
    一级: '.movie-list-body&&.movie-list-item;.movie-title&&Text;.Lazy&&data-original;.movie-rating&&Text;a&&href',
    // 一级:'json:list;vod_name;vod_pic;vod_score;vod_id',
    二级访问前: 'log(MY_URL);MY_URL=MY_URL.replace("/play/","/detail/").replace("/sid/1/nid/1","");log(MY_URL)',
    二级: {
        "title": "h1&&title;.scroll-content&&Text",
        "img": ".poster&&img&&src",
        "desc": ";;;.starLink&&Text;.cr3:eq(0)&&Text",
        "content": ".detailsTxt--div&&Text",
        "tabs": ".swiper-wrapper&&a",
        "lists": ".content_playlist:eq(#id)&&li"
    },

    // searchUrl:'/index.php/vod/search/page/fypage/wd/**.html',
    searchUrl: '/index.php/ajax/suggest?mid=1&wd=**&limit=50',
    detailUrl: '/index.php/vod/detail/id/fyid.html',
    // 搜索:'.movie-list-body&&.vod-search-list;*;*;.getop&&Text;*',
    搜索: 'json:list;name;pic;;id',
}