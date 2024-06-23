var rule = {
    类型: '听歌',//影视|听书|漫画|小说
    title: 'KTV歌厅[听]',
    host: 'https://vpsdn.leuse.top',
    mktvUrl: 'http://txysong.mysoto.cc/songs/',
    url: '/searchmv?table=fyclass&pg=fypage#fyfilter',
    searchUrl: '/searchmv?keywords=**&pg=fypage',
    pic: 'https://api.paugram.com/wallpaper/?source=sina&category=us',
    searchable: 2,
    quickSearch: 0,
    filterable: 1,
    filter: 'H4sIAAAAAAAAA52STU/CMBjHv0vPHATfuerFkwePhgOHSRZhmIEmhJBgBLIIBEgI0/BqAgFEwgYRDbjwZWzpvoUr2tGlXOTW/p+n7a+/Ng4iohQQZOC9jINrIQa8QBYCYlgCLiD5Q4I1hzUN5mbWXJTEqDW3Rnf+4K2wWiKRhnTPfOiRmFQTrvhq4CY7kGq7az5n7NjzF6PPESxodrxLu6sGbFdAwkcKvzxXYTm0plnqc6gMtqZZlj84FNiZcBzLeQoWFcLhc4FIWAowgoJ+xg4eDXEvuebx/BMIqwVrC56parAxxTKbfTbeozLVDhvv027VgHmVrRzQU7M6Gx/SW4/bbHxEYdLT73nFjo/p9v03VHcc7N6hQBPNkdufIa9B7ctRojfG00cKyzx+NHYjOB+/kd368dH7PX7J8a6LCizrnGuUTCK1y7mGqQUa5njX9T4sGZxopJXYbioaKw1UHfOiKzU4y3Ci8eLVHDxtsKy2UL55enZxcr5BtaHjbmb1gxM/8si9TOYDAAA=',
    filter_url: '{{fl}}',
    headers: {
        'User-Agent': 'MOBILE_UA',
    },
    timeout: 5000,
    class_name: '歌手&曲库',
    class_url: 'singer&song',
    一级: $js.toString(() => {
        let d = [];
        let _url = input.split('#')[0];
        if (MY_CATE === 'singer') {
            if (MY_FL.region) {
                _url += '&where=region_id&keywords=' + MY_FL.region + '&size=21';
            } else if (MY_FL.form) {
                _url += '&where=form_id&keywords=' + MY_FL.form + '&size=21';
            }
            let html = request(_url);
            let json = JSON.parse(html);
            d = json.map(item => {
                let pic = rule.mktvUrl + item.id + '.jpg';
                return {
                    vod_id: item.name + '@@' + item.name + '@@' + pic,
                    vod_name: item.name,
                    vod_pic: pic,
                    vod_remarks: '',
                }
            });
        } else if (MY_CATE === 'song') {
            if (MY_FL.lan) {
                _url += '&where=language_id&keywords=' + MY_FL.lan + '&size=21';
            } else if (MY_FL.type) {
                _url += '&where=type_id&keywords=' + MY_FL.type + '&size=21';
            }
            let html = request(_url);
            let json = JSON.parse(html);
            d = json.map(item => {
                return {
                    vod_id: rule.mktvUrl + item.number + '.mkv' + '@@' + item.name + '@@' + '',
                    vod_name: item.name,
                    vod_pic: rule.pic,
                    vod_remarks: '',
                }
            });
        }
        VODS = d;
    }),
    二级: $js.toString(() => {
        let id = orId.split('@@')[0];
        let name = orId.split('@@')[1];
        if (id.endsWith('.mkv')) {
            VOD = {
                vod_name: name,
                vod_play_from: '道长在线',
                vod_content: '道长在线',
            }
        } else {
            VOD = {
                vod_name: id,
                vod_play_from: '道长在线',
                vod_content: '道长在线',
            }
        }
        if (id.endsWith('.mkv')) {
            VOD.vod_play_url = '嗅探播放$' + id;
        } else {
            let data = [];
            for (let i = 0; i < 2; i++) {
                let pg = Number(i) + 1;
                let url = `${rule.host}/searchmv?table=song&where=singer_names&keywords=${id}&size=500&pg=${pg}`;
                let res = request(url);
                let json = JSON.parse(res);
                data = data.concat(json);
            }
            VOD.vod_play_url = (data.map(item => {
                return item.name + '$' + rule.mktvUrl + item.number + '.mkv';
            })).join('#');
        }
    }),
    搜索: $js.toString(() => {
        let d = [];
        let html = request(input);
        let json = JSON.parse(html);
        d = json.map(item => {
            return {
                vod_id: rule.mktvUrl + item.number + '.mkv' + '@@' + item.name + '@@' + '',
                vod_name: item.name,
                vod_pic: rule.pic,
                vod_remarks: item.singer_names,
            }
        });
        VODS = d;
    }),
    play_parse: true,
    lazy: $js.toString(() => {
        input = {parse: 0, url: input};
    }),
}