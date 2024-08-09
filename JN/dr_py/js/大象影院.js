var rule = {
    title: "大象影院",
    host: "https://www.appopen.com.cn",
    url: "/channel_filter/fyfilter.html",
    searchUrl: "https://www.appopen.com.cn/search.html#wd=**;post",
    searchable: 2,
    quickSearch: 0,
    filterable: 1,
    filter: 'H4sIAAAAAAAAA+2WwW7aQBCG38VnJO55lSqHJXXBJNiF4CoQRUqbQHCgpalaKApqewgBWiqM2iSNCeRlWBveomN7veux1UOVSqhSjp759p+dnZ1Z70tPFaKWFDUtbTzZl7blkrQhOZMp/VSXEpJKcjJ808pgdTSA7xdkR5c9UEVm+OAyBwnmPR0sZl3HOAkATU2Xde05cIJpdanRF8yektUR4NQm9lFFAETJQwyM9M/o7VQg23JGJypC7Jdv7cNWCIGtpHAg2AYKlNVjgezax4VlCKScIWo5I0epVyOndRZKSXfPRcSpvlt1hsKdI9oe2kfvBGWTV9xsRLKnY2f2VbifwRZ0UN90Ab94tGvShvV3xRPhL/qrTpVZk6QgkyQzBcTqsmP/GiOCmbhG07Rv51jDN/Es5m/o+QwRzMRP8ceHKMFMAbGsT6IEM3GNds/ujrCGb+K5fB5GNZiJ5zK/iRLMJHZqxndqIo3XJrUusYZv4hrHTThlWhtiGW7lOffuneZ3x+jgtLlVtN4Xu34Pi3FQbuVc5XoxbWHIN4UvlN0w7Pb1qv1T3KmwCV8r5HFVU6VkUYFFPNeGsRwf01o1BOxuaQXZjbmZ8ObIbgbmwD+YR74Oz/Z8trD60OiMSOvaFrRwiIBbHHITNR1e3TSFr0jCwu6d4a6IYrsnXIXwIveS/EHPHvXdduBeTc/JyH91Qy9awp9XioSlu8bClWGowqB7WNWYCB5HzvRuaVhBXWFxhIJDhhIgqqC4wzmCQXWbJsLcGsPZR0Hv/BHolSDA1tcbsIEcvAYP7AymEnqo7btvzvsrOpsk4VbRruUYNQzHX3e/mbyluJ+i8v7MRWRBSclxzr/1Yc479RjnlRFH9ssYS8ybZYj0WiXA1lbHrLLj/32IQj6+2o+v9n/7ah/8Bly0KEZGDAAA',
    filter_url: '{{fl.类型}}{{fl.地区}}{{fl.按时间}}/page/fypage',
    "filter_def": {
        "dianying": {
            "类型": "dianying"
        },
        "dianshiju": {
            "类型": "dianshiju"
        },
        "zongyi": {
            "类型": "zongyi"
        },
        "dongman": {
            "类型": "dongman"
        },
        "jilupian": {
            "类型": "jilupian"
        }
    },
    headers: {
        "User-Agent": "MOBILE_UA"
    },
    timeout: 5000,
    class_parse: "#pop-nav li;a&&Text;a&&href;.*/(.*?).html",
    cate_exclude: "",
    play_parse: true,
    lazy: $js.toString(() => {
        input = {
            parse: 1,
            url: input,
            js: ''
        };
    }),
    double: true,
    推荐: "",
    一级: "body&&.item;a&&title;img&&data-src;.tag1&&Text;a&&href;.desc&&Text",
    二级: {
    重定向: $js.toString(() => {
            log('执行重定向:' + MY_URL);
            MY_URL = pd(html, '.btn-play&&a&&href', MY_URL);
            log('二级重定向到:' + MY_URL);
            html = request(MY_URL);
        }),
        title: "h1&&Text;.gm-bread li:eq(2)&&Text",
        img: "img&&src",
        desc: ".more .info:eq(6)&&Text;.more .info&&Text;.more .info:eq(1)&&Text;.more .info:eq(2)&&Text;.more .info:eq(3)&&Text",
        content: ".info-box&&Text",
        tabs: "body&&.hd-item",
        lists: ".list:eq(#id) a",
    },
    搜索: "*"
}