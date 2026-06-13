/*
@header({
  searchable: 2,
  filterable: 1,
  quickSearch: 0,
  title: '瓜子',
  author: 'EylinSir',
  '类型': '影视',
  logo: 'https://guaziyingshi.xxsnav.com/files/guaziyingshi.png',
  lang: 'ds'
})
*/

// 内置补全依赖 - 适配本地包无全局依赖问题
const CryptoJS = require('crypto-js');
const forge = require('node-forge');

var rule = {
    类型: '影视',
    author: 'EylinSir',
    title: '瓜子',
    host: 'https://api.w32z7vtd.com',
    url: '/App/IndexList/indexList',
    searchUrl: '/App/Index/findMoreVod',
    logo: 'https://guaziyingshi.xxsnav.com/files/guaziyingshi.png',
    searchable: 2,
    quickSearch: 0,
    filterable: 1,
    play_parse: true, 
    class_name: '电影&电视剧&动漫&综艺&短剧',
    class_url: '1&2&4&3&64',
    headers: {
        'User-Agent': 'okhttp/3.12.0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
        'Version': '2406025',
        'PackageName': 'com.uf076bf0c246.qe439f0d5e.m8aaf56b725a.ifeb647346f',
        'Ver': '1.9.2',
        'Referer': 'https://api.w32z7vtd.com'
    },
    token: '1be86e8e18a9fa18b2b8d5432699dad0.ac008ed650fd087bfbecf2fda9d82e9835253ef24843e6b18fcd128b10763497bcf9d53e959f5377cde038c20ccf9d17f604c9b8bb6e61041def86729b2fc7408bd241e23c213ac57f0226ee656e2bb0a583ae0e4f3bf6c6ab6c490c9a6f0d8cdfd366aacf5d83193671a8f77cd1af1ff2e9145de92ec43ec87cf4bdc563f6e919fe32861b0e93b118ec37d8035fbb3c.59dd05c5d9a8ae726528783128218f15fe6f2c0c8145eddab112b374fcfe3d79',
    rsaPrivateKey: `-----BEGIN PRIVATE KEY-----
MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGAe6hKrWLi1zQmjTT1
ozbE4QdFeJGNxubxld6GrFGximxfMsMB6BpJhpcTouAqywAFppiKetUBBbXwYsYU
1wNr648XVmPmCMCy4rY8vdliFnbMUj086DU6Z+/oXBdWU3/b1G0DN3E9wULRSwcK
ZT3wj/cCI1vsCm3gj2R5SqkA9Y0CAwEAAQKBgAJH+4CxV0/zBVcLiBCHvSANm0l7
HetybTh/j2p0Y1sTXro4ALwAaCTUeqdBjWiLSo9lNwDHFyq8zX90+gNxa7c5EqcW
V9FmlVXr8VhfBzcZo1nXeNdXFT7tQ2yah/odtdcx+vRMSGJd1t/5k5bDd9wAvYdI
DblMAg+wiKKZ5KcdAkEA1cCakEN4NexkF5tHPRrR6XOY/XHfkqXxEhMqmNbB9U34
saTJnLWIHC8IXys6Qmzz30TtzCjuOqKRRy+FMM4TdwJBAJQZFPjsGC+RqcG5UvVM
iMPhnwe/bXEehShK86yJK/g/UiKrO87h3aEu5gcJqBygTq3BBBoH2md3pr/W+hUM
WBsCQQChfhTIrdDinKi6lRxrdBnn0Ohjg2cwuqK5zzU9p/N+S9x7Ck8wUI53DKm8
jUJE8WAG7WLj/oCOWEh+ic6NIwTdAkEAj0X8nhx6AXsgCYRql1klbqtVmL8+95KZ
K7PnLWG/IfjQUy3pPGoSaZ7fdquG8bq8oyf5+dzjE/oTXcByS+6XRQJAP/5ciy1b
L3NhUhsaOVy55MHXnPjdcTX0FaLi+ybXZIfIQ2P4rb19mVq1feMbCXhz+L1rG8oa
t5lYKfpe8k83ZA==
-----END PRIVATE KEY-----`,

    CryptoUtils: {
        aesEncrypt: (t, k, i) => CryptoJS.AES.encrypt(t, CryptoJS.enc.Utf8.parse(k), { iv: CryptoJS.enc.Utf8.parse(i), mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7 }).ciphertext.toString().toUpperCase(),
        aesDecrypt: (t, k, i) => CryptoJS.AES.decrypt({ ciphertext: CryptoJS.enc.Hex.parse(t) }, CryptoJS.enc.Utf8.parse(k), { iv: CryptoJS.enc.Utf8.parse(i), mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7 }).toString(CryptoJS.enc.Utf8),
        rsaDecrypt: (t, k) => { try { return forge.pki.privateKeyFromPem(k).decrypt(forge.util.decode64(t)); } catch (e) { return ""; } }
    },

    makePythonJson: function(dataMap, order) {
        let parts = [], keys = order || Object.keys(dataMap);
        let esc = (s) => s.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/[\u0000-\u001f\u007f-\uffff]/g, c => '\\u' + ('0000' + c.charCodeAt(0).toString(16)).slice(-4));
        for (let k of keys) parts.push(`"${k}": ${typeof dataMap[k] === 'string' ? `"${esc(dataMap[k])}"` : String(dataMap[k])}`);
        return `{${parts.join(', ')}}`;
    },

    // 适配本地包内置请求 替换原生req
    postData: async function(apiPath, dataMap, keyOrder) {
        let t = Math.floor(Date.now() / 1000).toString();
        let requestJson = this.makePythonJson(dataMap, keyOrder);
        let request_key = this.CryptoUtils.aesEncrypt(requestJson, 'mvXBSW7ekreItNsT', '2U3IrJL8szAKp0Fj');
        let keys_raw = "Qmxi5ciWXbQzkr7o+SUNiUuQxQEf8/AVyUWY4T/BGhcXBIUz4nOyHBGf9A4KbM0iKF3yp9M7WAY0rrs5PzdTAOB45plcS2zZ0wUibcXuGJ29VVGRWKGwE9zu2vLwhfgjTaaDpXo4rby+7GxXTktzJmxvneOUdYeHi+PZsThlvPI=";
        let signature = md5(`token_id=,token=${this.token},phone_type=1,request_key=${request_key},app_id=1,time=${t},keys=${keys_raw}*&zvdvdvddbfikkkumtmdwqppp?|4Y!s!2br`);
        let postDataStr = [`token=${this.token}`, `token_id=`, `phone_type=1`, `time=${t}`, `phone_model=xiaomi-22021211rc`, `keys=${encodeURIComponent(keys_raw)}`, `request_key=${request_key}`, `signature=${signature}`, `app_id=1`, `ad_version=1`].join('&');
        
        // 本地包标准fetch请求适配
        let resp = await fetch(this.host + apiPath, {
            method: 'POST',
            headers: this.headers,
            body: postDataStr
        });
        if (!resp) return null;
        let content = await resp.text();
        try {
            let json = JSON.parse(content);
            if (!json.data) return null;
            let bodyki = JSON.parse(this.CryptoUtils.rsaDecrypt(json.data.keys, this.rsaPrivateKey));
            let decrypted = this.CryptoUtils.aesDecrypt(json.data.response_key, bodyki.key, bodyki.iv);
            return (decrypted && decrypted !== '{}') ? JSON.parse(decrypted) : null;
        } catch (e) { return null; }
    },

    预处理: async function() {
        let area = [{"n": "全部", "v": "0"}, {"n": "大陆", "v": "大陆"}, {"n": "香港", "v": "香港"}, {"n": "台湾", "v": "台湾"}, {"n": "美国", "v": "美国"}, {"n": "韩国", "v": "韩国"}, {"n": "日本", "v": "日本"}, {"n": "其他", "v": "其他"}];
        let year = [{"n": "全部", "v": "0"}];
        for (let i = 2025; i >= 2005; i--) year.push({"n": String(i), "v": String(i)});
        let sort = [{"n": "最新", "v": "d_id"}, {"n": "最热", "v": "d_hits"}, {"n": "推荐", "v": "d_score"}];
        let filters = {};
        this.class_url.split('&').forEach(tid => {
            filters[tid] = [{"key": "area", "name": "地区", "value": area}, {"key": "year", "name": "年份", "value": year}, {"key": "sort", "name": "排序", "value": sort}];
        });
        rule.filter = filters;
    },

    推荐: async function() { return []; },
    
    一级: async function(tid, pg, filter, extend) {
        let body = { "area": String(extend.area || '0'), "year": String(extend.year || '0'), "pageSize": "30", "sort": String(extend.sort || 'd_id'), "page": String(pg), "tid": String(tid) };
        let data = await this.postData('/App/IndexList/indexList', body, ['area', 'year', 'pageSize', 'sort', 'page', 'tid']);
        return (data && data.list) ? data.list.map(item => ({
            vod_id: item.vod_id + '/' + (item.vod_continu || 0),
            vod_name: item.vod_name,
            vod_pic: item.vod_pic,
            vod_remarks: item.vod_continu === 0 ? '电影' : `更新至${item.vod_continu}集`
        })) : [];
    },

    二级: async function(ids) {
        let vod_id = ids[0].split('/')[0], t = Math.floor(Date.now() / 1000).toString();
        let qdata = await this.postData('/App/IndexPlay/playInfo', { "token_id": "1649412", "vod_id": String(vod_id), "mobile_time": t, "token": this.token }, ['token_id', 'vod_id', 'mobile_time', 'token']);
        let jdata = await this.postData('/App/Resource/Vurl/show', { "vurl_cloud_id": "2", "vod_d_id": String(vod_id) }, ['vurl_cloud_id', 'vod_d_id']);
        if (!qdata || !qdata.vodInfo) return {};
        let vod = qdata.vodInfo;
        let playList = (jdata && jdata.list) ? jdata.list.filter(i => i.play).map((item, idx) => {
            let n = [], p = [];
            for (let k in item.play) { if (item.play[k]?.param) { n.push(k); p.push(item.play[k].param); } }
            return p.length > 0 ? `${jdata.list.length === 1 ? vod.vod_name : idx + 1}$${p[p.length-1]}||${n.join('@')}` : null;
        }).filter(Boolean) : [];

        return {
            vod_id: vod_id, 
            vod_name: vod.vod_name, 
            vod_pic: vod.vod_pic, 
            type_name: vod.vod_class || '',
            vod_year: vod.vod_year, 
            vod_area: vod.vod_area, 
            vod_actor: vod.vod_actor, 
            vod_director: vod.vod_director,
            vod_content: (vod.vod_use_content || '').trim(), 
            vod_play_from: '嗑瓜子', 
            vod_play_url: playList.join('#')
        };
    },

    搜索: async function(key, quick, pg) {
        let data = await this.postData('/App/Index/findMoreVod', { "keywords": key, "order_val": "1", "page": String(pg || 1) }, ['keywords', 'order_val', 'page']);
        return (data && data.list) ? data.list.map(item => ({
            vod_id: item.vod_id + '/' + (item.vod_continu || 0),
            vod_name: item.vod_name,
            vod_pic: item.vod_pic,
            vod_remarks: item.vod_continu === 0 ? '电影' : `更新至${item.vod_continu}集`
        })) : [];
    },

    lazy: async function(flag, id, flags) {
        try {
            let parts = id.split('||');
            if (parts.length < 2) return { parse: 0, url: '' };
            let params = {}, keys = [];
            parts[0].split('&').forEach(pair => {
                let [k, v] = pair.split('=');
                if (k) { params[k] = v; if (!keys.includes(k)) keys.push(k); }
            });
            let res = (parts[1] || '').split('@').sort((a, b) => (parseInt(b.replace(/\D/g, '')) || 0) - (parseInt(a.replace(/\D/g, '')) || 0));
            if (res.length > 0) {
                params['resolution'] = res[0];
                if (!keys.includes('resolution')) keys.push('resolution');
                let data = await this.postData('/App/Resource/VurlDetail/showOne', params, keys);
                if (data && (data.url || data.m3u8 || data.vurl)) return { parse: 0, url: data.url || data.m3u8 || data.vurl, header: this.headers };
            }
        } catch (e) {}
        return { parse: 0, url: '' };
    }
};
