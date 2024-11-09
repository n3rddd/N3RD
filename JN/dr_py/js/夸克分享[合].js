/*
 * 传参 ?type=url&params=../json/夸克分享.json@夸克分享[盘]
 * {"classes":[{"type_name":"花生十三","type_id":"8dd332256252"},{"type_name":"食谱","type_id":"78414690490e"},{"type_name":"体育","type_id":"25bf5b71edbb"}],"cookie":"__puus=0d26f820dbe87c2ff7689eca16d33dbdAATbA+y7U6E45kIqf3tUJD3ubw3yiLFUneh7o2z7qsn/vNtt13XnX5nq24o8c1PFNiaRXf9lCjyU8a8OHOwiWUwyB2awYMF3Q3KeegYcdEvy8ND7sRa0vlDQ1nPIWdR0BZD52AXBQj5UBIy0E2yknnBf+bzag4ivcZLepQskKRVGJ8tlB7jy8sgOem4zOP0cxKCMZLmwUeeaKFzdCnlhqj9+;__pus=69d93c40091ac35657fcdad30c901d8fAATxYe3kuhbmWR/i/UY5HxwQQPHPfx2Y/oEUXCA5LbTk2cvg8UqI6jwVZs1vlK34HoJ6KsjzHygZE3SbMoQVW2g6;__kp=c9e05ec0-8574-11ef-8fbe-77ecc2a14af3"}
 */

globalThis.getxx = []
var rule = {
    author: '嗷呜',
    title: '夸克分享[合]',
    host: 'https://drive.quark.cn',
    url: '/1/clouddrive/share/sharepage/token?pr=ucpro&fr=pc',
    filterable: 1,
    searchable: 2,
    quickSearch: 0,
    // params:'../json/夸克分享.json',
    params: 'http://127.0.0.1:5707/files/json/夸克分享.json',
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/2.5.20 Chrome/100.0.4896.160 Electron/18.3.5.4-b478491100 Safari/537.36 Channel/pckk_other_ch',
        'Referer': 'http://pan.quark.cn/',
        'Content-Type': 'application/json',
        'Cookie': ''
    },
    hikerListCol: "avatar",
    play_parse: true,
    lazy: $js.toString(() => {
        let url = input
        input = {
            url: url,
            parse: 0,
            header: rule.headers
        }
    }),
    预处理: $js.toString(() => {
        let html = request(rule.params);
        let json = dealJson(html);
        rule_fetch_params.headers.Cookie = json.cookie
        rule.classes = json.classes;
    }),
    class_parse: $js.toString(() => {
        input = rule.classes;
    }),
    一级: $js.toString(() => {
        let vodd = []
        let pdtoken = MY_CATE
        if (!pdtoken.includes('_wjj')) {
            getxx[0] = pdtoken
            let body = { "pwd_id": MY_CATE, "passcode": "" }
            let data = JSON.parse(fetch(input, {
                method: 'POST',
                headers: rule.headers,
                body: body
            }));
            let stoken = data.data.stoken
            getxx[1] = stoken
            let url = HOST+`/1/clouddrive/share/sharepage/detail?pr=ucpro&fr=pc&pwd_id=${MY_CATE}&stoken=${encodeURIComponent(stoken)}&pdir_fid=0&force=0&_page=${MY_PAGE}&_size=50&_fetch_banner=1&_fetch_share=1&_fetch_total=1&_sort=file_type:asc,updated_at:desc`
            let fid = JSON.parse(request(url, { headers: rule.headers })).data.list
            getxx[2] = fid[0].fid

        } else {
            getxx[2] = pdtoken.replace('_wjj', '')
        }
        let url = HOST+`/1/clouddrive/share/sharepage/detail?pr=ucpro&fr=pc&pwd_id=${getxx[0]}&stoken=${encodeURIComponent(getxx[1])}&pdir_fid=${getxx[2]}&force=0&_page=${MY_PAGE}&_size=50&_fetch_banner=1&_fetch_share=1&_fetch_total=1&_sort=file_type:asc,file_name:asc`
        getxx[3] = MY_PAGE
        let data1 = JSON.parse(fetch(url, { headers: rule.headers }))
        let data2 = data1.data.list;
        data2.forEach(it => {
            let pdsp = it.format_type;
            if (pdsp.includes('video')) {
                let enji = it.fid + "$" + it.share_fid_token + "$" + it.file_name
                vodd.push({
                    vod_id: enji,
                    vod_name: it.file_name,
                    vod_pic: it.preview_url
                })
            } else if (pdsp === "") {
                vodd.push({
                    vod_id: it.fid + '_wjj',
                    vod_name: it.file_name,
                    vod_pic: 'https://gitee.com/amg99/tvjson/raw/master/img/kkwjj.png',
                    vod_tag: 'folder'
                })
            }
        });
        VODS = vodd
    }),
    二级: $js.toString(() => {
        let fg = vod_id.split('$')
        let csurl = HOST+`/1/clouddrive/share/sharepage/detail?pr=ucpro&fr=pc&pwd_id=${getxx[0]}&stoken=${encodeURIComponent(getxx[1])}&pdir_fid=${getxx[2]}&force=0&_page=${getxx[3]}&_size=50&_fetch_banner=1&_fetch_share=1&_fetch_total=1&_sort=file_type:asc,file_name:asc`
        let csdata1 = JSON.parse(fetch(csurl, { headers: rule.headers })).data.list
        for (let i = 0; i < csdata1.length; i++) {
            if (csdata1[i].file_name === fg[2] && csdata1[i].share_fid_token !== fg[1]) {
                fg[1] = csdata1[i].share_fid_token
                break;
            }
        }
        let pdirdata = fetch(HOST+'/1/clouddrive/file/sort?pr=ucpro&fr=pc&uc_param_str&pdir_fid=0&_page=1&_size=50&_fetch_total=1&_fetch_sub_dirs=0&_sort=file_type:asc,file_name:asc', { headers: rule.headers })
        pdirdata = dealJson(pdirdata).data.list
        let pdir = ''
        for (let i = 0; i < pdirdata.length; i++) {
            if (pdirdata[i].file_name === '0000temp' || pdirdata[i].file_name === '来自：分享') {
                pdir = pdirdata[i].fid
                break;
            }
        }
        let body = { "fid_list": [fg[0]], "fid_token_list": [fg[1]], "to_pdir_fid": pdir, "pwd_id": getxx[0], "stoken": getxx[1], "pdir_fid": "0" }
        let task_id = JSON.parse(fetch(HOST+'/1/clouddrive/share/sharepage/save?pr=ucpro&fr=pc', {
            method: 'POST',
            headers: rule.headers,
            body: body
        })).data.task_id
        function syncDelay(milliseconds) {
            var start = new Date().getTime();
            var end = 0;
            while ((end - start) < milliseconds) {
                end = new Date().getTime();
            }
        }
        let save_as_top_fids = ''
        for (let i = 0; i < 10; i++) {
            let data = fetch(HOST+`/1/clouddrive/task?pr=ucpro&fr=pc&task_id=${task_id}&retry_index=${i}`, { headers: rule.headers });
            let dataa = JSON.parse(data).data.save_as.save_as_top_fids
            if ((dataa.length > 0)) {
                save_as_top_fids = dataa[0]
                break;
            }
            syncDelay(2000)
        }
        let play = []; let pname = [];
        function ddd() {
            let body1 = { "fid": save_as_top_fids, "resolutions": "normal,low,high,super,2k,4k", "supports": "fmp4,m3u8" }
            let pldata = fetch(HOST+'/1/clouddrive/file/v2/play?pr=ucpro&fr=pc', {
                method: 'POST',
                headers: rule.headers,
                body: body1
            });
            let pljson = JSON.parse(pldata).data.video_list
            pljson.forEach(it => {
                pname.push(it.video_info.width)
                play.push(fg[2] + '$' + it.video_info.url)
            })
        }
        for (let i = 0; i < 10; i++) {
            syncDelay(2000)
            try {
                ddd()
                break;
            } catch {
                play = []; pname = [];
            }
        }
        let body2 = { 'fids': [save_as_top_fids] }
        let pldata1 = fetch(HOST+'/1/clouddrive/file/download?pr=ucpro&fr=pc', {
            method: 'POST',
            headers: rule.headers,
            body: body2
        })
        VOD = {
            vod_play_from: pname.join('$$$'),
            vod_play_url: play.join('$$$')
        }
    }),
}
