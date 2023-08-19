var rule = {
	title:'4KHDR[磁]',
	host:'https://www.4khdr.cn',
        homeUrl: "/forum.php?mod=forumdisplay&fid=2&page=1",
	url: '/forum.php?mod=forumdisplay&fid=2&filter=typeid&typeid=fyclass&page=fypage',
	filter_url:'{{fl.class}}',
	filter:{
	},
	searchUrl: '/search.php#searchsubmit=yes&srchtxt=**;post',
	searchable:2,
	quickSearch:1,
	filterable:0,
	headers:{
		'User-Agent': 'PC_UA',
         	'Cookie':'hvLw_2132_saltkey=D42d76fc; hvLw_2132_lastvisit=1691932615; hvLw_2132_visitedfid=2; hvLw_2132_sendmail=1; _clck=154oxs7|2|fe4|0|1320; hvLw_2132_seccodecSAN65=6123.7f784d2302a06fc851; hvLw_2132_ulastactivity=1691936275%7C0; hvLw_2132_auth=f414is8LjLPKidkdraDXILeOYO7FTXkLD2kGZXnMpbd%2F%2FFBbttQIi4Uz3B4UY04siUlqGhn2aTWfMVM9XtsXb3H%2FqQ; hvLw_2132_lastcheckfeed=59035%7C1691936275; hvLw_2132_checkfollow=1; hvLw_2132_lip=120.84.12.18%2C1691936275; hvLw_2132_sid=0; hvLw_2132_st_t=59035%7C1691936277%7C72adae43ccf943acc9f44889da89c8c2; hvLw_2132_forum_lastvisit=D_2_1691936277; hvLw_2132_checkpm=1; hvLw_2132_noticeTitle=1; hvLw_2132_lastact=1691936278%09misc.php%09patch',
	},
	timeout:5000,
	class_name: "4K电影&4K美剧&4K华语&4K动画&4K纪录片&4K日韩印&蓝光电影&蓝光美剧&蓝光华语&蓝光动画&蓝光日韩印",
	class_url:"3&8&15&6&11&4&29&31&33&32&34",
	play_parse:false,
	lazy:'',
	limit:6,
	推荐:'ul#waterfall li;a&&title;img&&src;div.auth.cl&&Text;a&&href',
	一级:'ul#waterfall li;a&&title;img&&src;div.auth.cl&&Text;a&&href',
	二级:{
		title:"#thead_subject&&Text",
		img:"img.zoom&&src",
		desc:'td[id^="postmessage_"] font&&Text',
		content:'td[id^="postmessage_"] font&&Text',
		tabs:`js:
			pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
			TABS=[]
			var d = pdfa(html, 'table.t_table');
			let magnetIndex=0;
			let aliIndex=0;
			d.forEach(function(it) {
				let burl = pdfh(it, 'a&&href');
				log("burl >>>>>>" + burl);
				if (burl.startsWith("https://www.aliyundrive.com/s/")){
					let result = 'aliyun' + aliIndex;
					aliIndex = aliIndex + 1;
					TABS.push(result);
				}
			});
			d.forEach(function(it) {
				let burl = pdfh(it, 'a&&href');
				log("burl >>>>>>" + burl);
				if (burl.startsWith("magnet")){
					let result = 'magnet' + magnetIndex;
					magnetIndex = magnetIndex + 1;
					TABS.push(result);
				}
			});
			log('TABS >>>>>>>>>>>>>>>>>>' + TABS);
		`,
		lists:`js:
			log(TABS);
			pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
			LISTS = [];
			var d = pdfa(html, 'table.t_table');
			TABS.forEach(function(tab) {
				log('tab >>>>>>>>' + tab);
				if (/^aliyun/.test(tab)) {
					let targetindex = parseInt(tab.substring(6));
					let index = 0;
					d.forEach(function(it){
						let burl = pdfh(it, 'a&&href');
						if (burl.startsWith("https://www.aliyundrive.com/s/")){
							if (index == targetindex){
								let title = pdfh(it, 'a&&Text');
								log('title >>>>>>>>>>>>>>>>>>>>>>>>>>' + title);
								burl = "http://127.0.0.1:9978/proxy?do=js&type=push&from=ali&url=" + encodeURIComponent(burl);
								log('burl >>>>>>>>>>>>>>>>>>>>>>>>>>' + burl);
								let loopresult = title + '$' + burl;
								LISTS.push([loopresult]);
							}
							index = index + 1;
						}
					});
				}
			});
			TABS.forEach(function(tab) {
				log('tab >>>>>>>>' + tab);
				if (/^magnet/.test(tab)) {
					let targetindex = parseInt(tab.substring(6));
					let index = 0;
					d.forEach(function(it){
						let burl = pdfh(it, 'a&&href');
						if (burl.startsWith("magnet")){
							if (index == targetindex){
								let title = pdfh(it, 'a&&Text');
								log('title >>>>>>>>>>>>>>>>>>>>>>>>>>' + title);
								log('burl >>>>>>>>>>>>>>>>>>>>>>>>>>' + burl);
								let loopresult = title + '$' + burl;
								LISTS.push([loopresult]);
							}
							index = index + 1;
						}
					});
				}
			});
			`,

	},
	一级:'ul#waterfall li;a&&title;img&&src;div.auth.cl&&Text;a&&href',
	搜索:'div#threadlist ul li;h3&&Text;;p:eq(3)&&Text;a&&href;p:eq(2)&&Text',
	预处理:`
    		if (rule_fetch_params.headers.Cookie.startsWith("http")){
			rule_fetch_params.headers.Cookie=fetch(rule_fetch_params.headers.Cookie);
			setItem(RULE_CK,cookie);
		};
		log('4khdr cookie>>>>>>>>>>>>>>>' + rule_fetch_params.headers.Cookie);
		let new_host='https://www.4khdr.cn/search.php';
		let new_html=request(new_host);
		pdfh=jsp.pdfh;pdfa=jsp.pdfa;pd=jsp.pd;
		let formhash = pdfh(new_html, 'input[name="formhash"]&&value');
		log("formhash>>>>>>>>>>>>>>>" + formhash);
		rule_fetch_params.formhash = formhash;
	`,
}
