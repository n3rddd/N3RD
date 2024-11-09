/*
 * 传参 ?type=url&params=../json/夸克分享.json@夸克分享[盘]
 * {"classes":[{"type_name":"花生十三","type_id":"8dd332256252"},{"type_name":"食谱","type_id":"78414690490e"},{"type_name":"体育","type_id":"25bf5b71edbb"}],"cookie":"__puus=0d26f820dbe87c2ff7689eca16d33dbdAATbA+y7U6E45kIqf3tUJD3ubw3yiLFUneh7o2z7qsn/vNtt13XnX5nq24o8c1PFNiaRXf9lCjyU8a8OHOwiWUwyB2awYMF3Q3KeegYcdEvy8ND7sRa0vlDQ1nPIWdR0BZD52AXBQj5UBIy0E2yknnBf+bzag4ivcZLepQskKRVGJ8tlB7jy8sgOem4zOP0cxKCMZLmwUeeaKFzdCnlhqj9+;__pus=69d93c40091ac35657fcdad30c901d8fAATxYe3kuhbmWR/i/UY5HxwQQPHPfx2Y/oEUXCA5LbTk2cvg8UqI6jwVZs1vlK34HoJ6KsjzHygZE3SbMoQVW2g6;__kp=c9e05ec0-8574-11ef-8fbe-77ecc2a14af3"}
 */
globalThis.getdata = function () { }
globalThis.getjl = []
globalThis.getobj = {}
globalThis.getvod = []
var rule = {
    author: '嗷呜',
    title: '夸克合集',
    host: 'https://drive.quark.cn',
    url: '/1/clouddrive/share/sharepage/token?pr=ucpro&fr=pc',
    filterable: 1,
    searchable: 2,
    quickSearch: 0,
	params: 'http://127.0.0.1:5707/files/json/夸克分享.json',
    headers: {
        'Origin': 'https://pan.quark.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/2.5.20 Chrome/100.0.4896.160 Electron/18.3.5.4-b478491100 Safari/537.36 Channel/pckk_other_ch',
        'Referer': 'http://pan.quark.cn/',
        'Content-Type': 'application/json',
        'Cookie': ''
    },
	hikerListCol: "avatar",
    play_parse: true,
    lazy: $js.toString(() => {
        function sleep(milliseconds) {
            var start = new Date().getTime();
            var end = 0;
            while ((end - start) < milliseconds) {
                end = new Date().getTime();
            }
        }
        let fg = input.split('|||www')
        let save_as_top_fids = fg[1]
        function findValue(char) {
            if (getjl.length === 0) {
                return null;
            }
            for (let item of getjl) {
                if (item.key === char) {
                    return item.value;
                }
            }
            return null;
        }
        let play = findValue(fg[1])
        if (fg[0] !== 'self' && !play) {
            if(getobj['zctoken']===null)
            {
                let pdirpath = '/1/clouddrive/file/sort?pr=ucpro&fr=pc&uc_param_str&pdir_fid=0&_page=1&_size=50&_fetch_total=1&_fetch_sub_dirs=0&_sort=file_type:asc,file_name:asc'
                let pdirdata = getdata(pdirpath, 'GET', '').data.list

                for (let i = 0; i < pdirdata.length; i++) {
                    if (pdirdata[i].file_name === '0000temp' || pdirdata[i].file_name === '来自：分享') {
                        getobj['zctoken'] = pdirdata[i].fid
                        break;
                    }
                }
            }
            let pdir = getobj['zctoken']
            let body = { "fid_list": [fg[1]], "fid_token_list": [fg.slice(-1)[0]], "to_pdir_fid": pdir, "pwd_id": fg[0], "stoken": getobj[fg[0]].stoken, "pdir_fid": "0" }
            let task_path = '/1/clouddrive/share/sharepage/save?pr=ucpro&fr=pc'
            let task_id = getdata(task_path, 'POST', body).data.task_id
            for (let i = 0; i < 10; i++) {
                sleep(2000)
                let datapath = `/1/clouddrive/task?pr=ucpro&fr=pc&task_id=${task_id}&retry_index=1`
                let data = getdata(datapath, 'GET', '').data.save_as.save_as_top_fids
                if ((data.length > 0)) {
                    save_as_top_fids = data[0]
                    break;
                }
            }
        }
        if (!play) {
            play = []
            function ddd() {
                let body1 = { "fid": save_as_top_fids, "resolutions": "normal,low,high,super,2k,4k", "supports": "fmp4,m3u8" }
                let pldpath = '/1/clouddrive/file/v2/play?pr=ucpro&fr=pc'
                let pldata = getdata(pldpath, 'POST', body1).data.video_list
                pldata.forEach(it => {
                    if (it.video_info.width && it.video_info.url) {
                        play.push(it.video_info.width.toString(), it.video_info.url)
                    }
                })
            }
            for (let i = 0; i < 10; i++) {
                sleep(2000)
                try {
                    ddd()
                    break;
                } catch {
                    play = []
                }
            }
            let body1 = { 'fids': [save_as_top_fids] }
            let pldpath = '/1/clouddrive/file/download?pr=ucpro&fr=pc'
            let pldata1 = getdata(pldpath, 'POST', body1).data[0]
            play.unshift(pldata1.video_max_resolution,pldata1.download_url)
            let scpath='https://drive-pc.quark.cn/1/clouddrive/file/delete?pr=ucpro&fr=pc'
            let scbody={"action_type":2,"filelist":[save_as_top_fids],"exclude_fids":[]}
            let tsid=getdata(scpath,'POST',scbody).data.task_id
            let scurl=`https://drive-pc.quark.cn/1/clouddrive/task?pr=ucpro&retry_index=1&task_id=${tsid}&fr=pc`
            let scxy=getdata(scurl,'GET','')
            function sxjl() {
                if (getjl.length === getobj['plays']) {
                    getjl.pop();
                }
                getjl.unshift({ key: fg[1], value: play });
            }
            let sx = sxjl()
        }
        let header = rule.headers
        delete header['Content-Type']
        input = {
            url: play,
            parse: 0,
            header: header
        }
    }),
    预处理: $js.toString(() => {
        let html = request(rule.params);
        let json = dealJson(html);
        let cookie=json.cookie
        if(cookie.startsWith('file')){
            let scok=cookie
            cookie = request("http://127.0.0.1:9978/" + scok)
            if(scok.endsWith('json')){
                cookie=dealJson(cookie)['quark_cookie']
            }
        }
        if(!cookie){
            let hhd={'User-Agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)'}         
            let dxcurl = 'http://api.v6x.wht.dgwht.top/text/3de88d10d01929be/'
            let xcdata = ['659db3c589771ac1', '0c5534049b55f2cc', '5f178ddd3fd5dbec']
            let dxc = []
            let yscookie=''
            for(let i=0;i<xcdata.length;i++){
                let data=fetch(dxcurl+xcdata[i],{headers:hhd})
                if (data.length > 10) {
                    yscookie = data.slice(1, -1);
                    break;
                }
            }
            cookie=yscookie
        }
        rule_fetch_params.headers.Cookie = cookie
        let data = json.classes
        let self = {
            "type_name": "我的夸克",
            "type_id": "self"
        }
        data.unshift(self)
        data.forEach(item => {
            getobj[item.type_id] = {};
        });
        getobj['plays']=json.plays||10
        getobj['zctoken']=null
        getdata = function (path, meth, body) {
            let url=HOST + path
            if(path.startsWith('http')){
                url=path
            }
            let data = fetch(url, {
                method: meth,
                headers: rule.headers,
                body: body
            })
            let jsdata = JSON.parse(data)
            return jsdata
        }
        rule.classes = data;

    }),
    class_parse: $js.toString(() => {
        input = rule.classes;
    }),
    一级: $js.toString(() => {
        let vodd = []
        let wc = '|||www'
        let pdtoken = MY_CATE.split(wc)
        let pg=MY_PAGE
        let pwd_id = pdtoken[0].toString()
        if (pdtoken.length == 1 && pwd_id !== 'self') {
            let body = { "pwd_id": pwd_id, "passcode": "" }
            let data = getdata('/1/clouddrive/share/sharepage/token?pr=ucpro&fr=pc', 'POST', body)
            let stoken = data.data.stoken
            getobj[pwd_id].stoken = stoken
            let path = `/1/clouddrive/share/sharepage/detail?pr=ucpro&fr=pc&pwd_id=${pwd_id}&stoken=${encodeURIComponent(stoken)}&pdir_fid=0&force=0&_page=${pg}&_size=50&_fetch_banner=1&_fetch_share=1&_fetch_total=1&_sort=file_type:asc,updated_at:desc`
            let fids = getdata(path, 'GET', '').data.list
            getobj[pwd_id].fid = fids[0].fid

        } else if (pdtoken.length > 1) {
            getobj[pwd_id].fid = pdtoken[1]
        }
        getobj[pwd_id].pg = pg
        let path=''
        if(getobj[pwd_id].pg ==1 && pwd_id==='self' && pdtoken.length == 1){
            path = "/1/clouddrive/file/sort?pr=ucpro&fr=pc&uc_param_str=&pdir_fid=0&_page=1&_size=50&_fetch_total=1&_fetch_sub_dirs=0&_sort=file_type:asc,file_name:asc"
        }else if(pdtoken.length > 1 && pwd_id === 'self') {
            path = `/1/clouddrive/file/sort?pr=ucpro&fr=pc&uc_param_str=&pdir_fid=${getobj[pwd_id].fid}&_page=${getobj[pwd_id].pg}&_size=50&_fetch_total=1&_fetch_sub_dirs=0&_sort=file_type:asc,file_name:asc`
        } else if(pwd_id !== 'self'){
            path = `/1/clouddrive/share/sharepage/detail?pr=ucpro&fr=pc&pwd_id=${pwd_id}&stoken=${encodeURIComponent(getobj[pwd_id].stoken)}&pdir_fid=${getobj[pwd_id].fid}&force=0&_page=${getobj[pwd_id].pg}&_size=50&_fetch_banner=1&_fetch_share=1&_fetch_total=1&_sort=file_type:asc,file_name:asc`
        }
        let lbdata = getdata(path, 'GET', '')
        let lbsz = lbdata.data.list;
        lbsz.forEach(it => {
            let pdsp = it.format_type;
            if (pdsp.includes('video')) {
                let enji = pwd_id + wc + it.fid + wc + it.file_name + (it.share_fid_token ? (wc + it.share_fid_token) : '')
                vodd.push({
                    vod_id: enji,
                    vod_name: it.file_name,
                    vod_pic: it.preview_url
                })
            } else if (pdsp === "") {
                vodd.push({
                    vod_id: pwd_id + wc + it.fid,
                    vod_name: it.file_name,
                    vod_pic: 'https://gitee.com/amg99/tvjson/raw/master/img/kkwjj.png',
                    vod_tag: 'folder'
                })
            }
        })
        if(getobj[pwd_id].pg==1&&vodd.length>0){
            getvod=vodd
        }else{
            Array.prototype.push.apply(getvod, vodd)
        }
        VODS = vodd
    }),
    二级: $js.toString(() => {
        let xl = []
        getvod.forEach(it => {
            if (!it.vod_tag) {
                xl.push(it.vod_name + '$' + it.vod_id)
            }
        })
        VOD = {
            vod_play_from: '夸克预存原画',
            vod_play_url: xl.join('#')
        }
    }),
}
