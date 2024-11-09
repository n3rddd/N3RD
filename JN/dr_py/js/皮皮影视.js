var rule = {
   "title": "皮皮影视",
    模板: 'mxpro',
    tab_exclude: '排序',
    "host": "https://www.ppys01.com",
     "url": "/vodshow/fyclassfyfilter.html",
    "searchUrl": "/vodsearch/**----------fypage---.html",
    "searchable": 2,
    "quickSearch": 0,
    "filterable": 1,
    "headers": {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36"
    },
    "class_parse": ".navbar-items li:gt(0):lt(8);a&&Text;a&&href;/(\\d+).html",
    "play_parse": true,
    lazy: $js.toString(() => {
        let html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        let url = html.url;
        if (html.encrypt == '1') {
            url = unescape(url);
        } else if (html.encrypt == '2') {
            url = unescape(base64Decode(url));
        }
        if (/m3u8/.test(url)) {
            input = {
                jx: 0,
                url: url,
                parse: 0
            }
        } else {
            let config = {};
            eval(request(HOST + '/static/js/playerconfig.js') + '\nconfig=MacPlayerConfig;');
            let jx = HOST + config.player_list[html.from].parse;
            if (jx == '') {
                jx = HOST + config.parse;
            }
            log(jx);
            eval(request(jx + url, {
                headers: {
                    'Referer': input
                }
            }).match(/let config = {[\s\S]*?}/)[0]);
            log(config.url);
            eval(getCryptoJS());

            function rc4(data, key, t) {
                let pwd = key || 'ffsirllq';
                let cipher = '';
                key = [];
                let box = [];
                let pwd_length = pwd.length;
                if (t == 1) {
                    data = atob(data);
                } else {
                    data = encodeURIComponent(data);
                }
                let data_length = data.length;
                for (let i = 0; i < 256; i++) {
                    key[i] = pwd[i % pwd_length].charCodeAt();
                    box[i] = i;
                }
                for (let j = 0, i = 0; i < 256; i++) {
                    j = (j + box[i] + key[i]) % 256;
                    let tmp = box[i];
                    box[i] = box[j];
                    box[j] = tmp;
                }
                for (let a = 0, j = 0, i = 0; i < data_length; i++) {
                    a = (a + 1) % 256;
                    j = (j + box[a]) % 256;
                    let tmp = box[a];
                    box[a] = box[j];
                    box[j] = tmp;
                    let k = box[((box[a] + box[j]) % 256)];
                    cipher += String.fromCharCode(data[i].charCodeAt() ^ k);
                }
                if (t == 1) {
                    return decodeURIComponent(cipher);
                } else {
                    return btoa(cipher);
                }
            }

            let play = rc4(config.url, "202205051426239465", 1);
            input = {
                jx: 0,
                url: play,
                parse: 0
            }

        }
    }),
    "limit": 6,
    "double": true,
    "二级": {
        "title": "h1&&Text;.module-info-tag-link:eq(-1)&&Text",
        "img": ".lazyload&&data-original||data-src||src",
        "desc": ".module-info-item:eq(-1)&&Text;.module-info-tag-link&&Text;.module-info-tag-link:eq(1)&&Text;.module-info-item:eq(2)&&Text;.module-info-item:eq(1)&&Text",
        "content": ".module-info-introduction&&Text",
        "tabs": ".module-tab-item",
        "lists": ".module-play-list:eq(#id) a",
        "tab_text": "div--small&&Text"
    },
    "搜索": "body .module-item;.module-card-item-title&&Text;.lazyload&&data-original;.module-item-note&&Text;a&&href;.module-card-item-info&&Text",
     "filter": "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",
  "filter_url": "-{{fl.地区}}-{{fl.排序}}-{{fl.剧情}}-{{fl.语言}}-{{fl.字母}}---fypage---{{fl.年份}}",
}