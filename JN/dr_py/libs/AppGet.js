// 用法
//{
// "key": "drpy2_AppGet模板",
// "name": "AppGet模板|drpy2",
// "type": 3,
// "api": "./lib/drpy2.min.js",
// "ext": "./lib/drpy2_AppGet模板.js?type=url&params=域名$key$iv"
// },

//例子 {
	// "key": "drpy2_AppGet模板",
	// "name": "AppGet模板|drpy2",
	// "type": 3,
	// "api": "xxx/drpy2.min.js",
	// "ext": "xxx/drpy2_AppGet模板.js?type=url&params=http://154.37.220.65$uI1TkPJC8B46AyN3$uI1TkPJC8B46AyN3"
// },
var rule = {
	//定义AES加密函数
	encryptAes: function(data) {
		const key = CryptoJS.enc.Utf8.parse(rule.key);
		const iv = CryptoJS.enc.Utf8.parse(rule.iv);
		const encrypted = CryptoJS.AES.encrypt(data, key, {
			iv: iv,
			mode: CryptoJS.mode.CBC,
			padding: CryptoJS.pad.Pkcs7
		});
		return encrypted.toString()
	},
	//定义AES解密函数
	decryptAes: function(data, key, iv) {
		data = data.replace(/^\uFEFF/, '');
		key = key || rule.key;
		iv = iv || rule.iv;
		key = CryptoJS.enc.Utf8.parse(key);
		iv = CryptoJS.enc.Utf8.parse(iv);
		const decrypted = CryptoJS.AES.decrypt(data, key, {
			iv: iv,
			mode: CryptoJS.mode.CBC,
			padding: CryptoJS.pad.Pkcs7
		});
		return decrypted.toString(CryptoJS.enc.Utf8)
	},
	//定义获取目标代码json函数
	getkjson: function(url, body) {
		let khtml = fetch(url, {
			headers: rule.headers,
			body: body,
			method: 'POST'
		});
		let kdata = JSON.parse(khtml).data;
		let kjson = JSON.parse(rule.decryptAes(kdata))
		return kjson
	},

	author: '小可乐/2505/第一版',
	title: 'AppGet模板',
	类型: '影视',
	host: '',
	hostJs: `HOST = rule.params.split('$')[0]`,
	headers: {
		'User-Agent': 'okhttp/3.14.9'
	},
	编码: 'utf-8',
	timeout: 5000,

	homeUrl: '/api.php/getappapi.index/initV119',
	url: '/api.php/getappapi.index/typeFilterVodList',
	filter_url: '',
	searchUrl: '/api.php/getappapi.index/searchList',
	detailUrl: '/api.php/getappapi.index/vodDetail?vod_id=fyid',

	limit: 9,
	double: false,
	class_parse: $js.toString(() => {
		input = rule.classes
	}),
	filter_def: {},

	预处理: $js.toString(() => {
		let khost = rule.params.split('$')[0];
		rule.key = rule.params.split('$')[1] || '';
		rule.iv = rule.params.split('$')[2] || '';

		let kjson = rule.getkjson(`${khost}/api.php/getappapi.index/initV119`, {});
		let kclasses = kjson.type_list.map((item) => {
			return {
				type_name: item.type_name,
				type_id: item.type_id
			}
		});
		let nameObj = JSON.parse(JSON.stringify({
			'class': '剧情',
			'area': '地区',
			'lang': '语言',
			'year': '年份',
			'sort': '排序'
		}));
		let kfilter = kjson.type_list.reduce((acc, kit) => {
			if (kit.filter_type_list) {
				acc[kit.type_id] = kit.filter_type_list.map((kfl) => {
					return {
						key: kfl.name,
						name: nameObj[kfl.name],
						value: kfl.list.map((item) => {
							return {
								n: item,
								v: item
							}
						})
					}
				});
			} else {
				acc[kit.type_id] = []
			};
			return acc
		}, {});
		rule.classes = kclasses;
		rule.filter = kfilter
	}),

	推荐: $js.toString(() => {
		let kjson = rule.getkjson(input, {});
		VODS = kjson.recommend_list;
		kjson.type_list.forEach((item) => {
			if (Array.isArray(item.recommend_list) && item.recommend_list.length !== 0) {
				VODS = VODS.concat(item.recommend_list)
			}
		})
	}),
	一级: $js.toString(() => {
		let kbody = {
			"type_id": (MY_FL.cateId || MY_CATE).toString(),
			"class": (MY_FL.class || "全部").toString(),
			"area": (MY_FL.area || "全部").toString(),
			"lang": (MY_FL.lang || "全部").toString(),
			"year": (MY_FL.year || "全部").toString(),
			"sort": (MY_FL.sort || "最新").toString(),
			"page": MY_PAGE
		};
		let kjson = rule.getkjson(input, kbody);
		VODS = kjson.recommend_list
	}),
	搜索: $js.toString(() => {
		let kbody = {
			"keywords": KEY,
			"type_id": 0,
			"page": MY_PAGE
		};
		let kjson = rule.getkjson(input, kbody);
		VODS = kjson.search_list
	}),
	二级: $js.toString(() => {
		let durl = input.split('?')[0];
		let dbody = input.split('?')[1];
		let kjson = rule.getkjson(durl, dbody);
		let kvod = kjson.vod;
		let ktabs = kjson.vod_play_list.map((it) => {
			return `雷蒙影视 | ${it.player_info.show}`
		});
		let kurls = kjson.vod_play_list.map((item) => {
			let kurl = item.urls.map((it) => {
				return `${it.name}$${it.from}@${it.url}@${it.token}@${item.player_info.parse}`
			});
			return kurl.join('#')
		});
		VOD = {
			vod_id: kvod.vod_id,
			vod_name: kvod.vod_name,
			vod_pic: kvod.vod_pic,
			type_name: kvod.vod_class,
			vod_remarks: kvod.vod_remarks,
			vod_year: kvod.vod_year,
			vod_area: kvod.vod_area,
			vod_lang: kvod.vod_lang,
			vod_director: kvod.vod_director,
			vod_actor: kvod.vod_actor,
			vod_content: kvod.vod_content,
			vod_play_from: ktabs.join('$$$'),
			vod_play_url: kurls.join('$$$')
		}
	}),

	play_parse: true,
	lazy: $js.toString(() => {
		function getpurl(furl, fparse, ftoken) {
			furl = encodeURIComponent(rule.encryptAes(furl));
			furl = `${HOST}/api.php/getappapi.index/vodParse?parse_api=${fparse}&url=${furl}&token=${ftoken}`;
			let kdata = JSON.parse(fetch(furl)).data;
			kdata = JSON.parse(rule.decryptAes(kdata)).json;
			return JSON.parse(kdata.replace(/\\/g, '')).url
		};
		let [kfrom, kurl, ktoken, kparse] = input.split('@');
		let pheaders = {
			'User-Agent': MOBILE_UA,
			'Referer': HOST
		};
		if (/\.(m3u8|mp4|mkv)/.test(kurl)) {
			input = {
				jx: 0,
				parse: 0,
				url: kurl,
				header: pheaders
			}
			// } else if (/qq|youku|iqiyi|mgtv|bilibili/.test(kurl)) {
			// kurl = '填自己官解' + kurl;
			// kurl = JSON.parse(fetch(kurl)).url;
			// input = { jx: 0, parse: 0, url: kurl, header: pheaders }
		} else {
			kurl = getpurl(kurl, kparse, ktoken);
			input = {
				jx: 0,
				parse: 0,
				url: kurl,
				header: pheaders
			}
		}
	}),

	filter: {}
}
