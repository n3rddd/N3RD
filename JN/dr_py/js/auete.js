var rule = {
    title: "auete",
    host: "https://auete.pro",
    url: "/fyclassfyfilter/indexfypage.html[/fyclassfyfilter/index.html]",
    searchUrl: "/vodsearch/**----------fypage---.html",
    searchable: 2,
    quickSearch: 0,
    filterable: 1,
    filter: "H4sIAAAAAAAAAJXTwU7CQBAG4HfZM4l3zp5IvHnScFjSprTAVpRWgZCAhAiYiCSIRki8YMCYKMSYIKU+DdviW7gUaf9667F83dm/M0OZHOimKpP4cZlk5CKJkwJVSIwwmpP9B5Nmje0rTPzG+0PeGrutq42I570L7YRUYn/YnqzsIaBUCtBtzpx6A5DmAcdd/mUBZtIBOrVbp9pHTAHW287lI6B2Bth8WC1agCUIJL4jHEjbBEpWkjFyaEbpift9I2rtquhGTlb9S36eXsDSlGlGkO7+GexURfqYAhVpgaK6dhf0nDIFkHfwaPggH9irhW9MVqUgqTN/x3NmStF8W1/PMI4avnDUD6XxLvTaeFSMtFoD27WWuzqKoZd0pmAjQUUjQypGACoGsFUvxX4uUor2xO1Z/gKLMmmD4sic5Wswshxl2FwwkR9RBAQUAT308uXVAo2ScP025fYd7G0iC38kq8Mbc0TpP8KwEpIWWqrR2O19cnvmDxMqb3dnXa2FX8lSXVIp2+yE9z2VX1mJ3vdVBAAA",
    filter_url: "{{fl.tag}}",
    filter_def: {},
    headers: {
        "User-Agent": "MOBILE_UA"
    },
    timeout: 5000,
    class_parse: ".navbar-nav&&li:lt(6);a&&Text;a&&href;.*/(.*?)/index",
    cate_exclude: "发布|影讯",
    play_parse: true,
    lazy: $js.toString(() => {
        input = {parse: 1, url: input, js: ''};
    }),
    double: false,
    推荐: "a.module-poster-item.module-item;.module-poster-item-title&&Text;.lazyload&&data-original;.module-item-note&&Text;a&&href",
    一级: ".threadlist&&li;.title&&Text;.pic&&img&&src;.hdtag&&Text;a&&href",
    二级: {
        title: "meta[property]:eq(1)&&content;meta[property]:eq(4)&&content",
        img: ".cover&&img&&src",
        desc: ".media-body&&.small&&Text;.module-info-item:eq(2)&&Text;.module-info-item:eq(3)&&Text;meta[property]:eq(6)&&content;meta[property]:eq(5)&&content",
        content: "meta[property]:eq(-1)&&content",
        tabs: "#player_list&&h2",
        lists: "#player_list:eq(#id) a",
        tab_text: "*--span&&Text",
        list_text: "body&&Text",
        list_url: "a&&href"
    },
    detailUrl: "",
    搜索: "body .module-item;.module-card-item-title&&Text;.lazyload&&data-original;.module-item-note&&Text;a&&href;.module-info-item-content&&Text"
}