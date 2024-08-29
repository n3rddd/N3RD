var rule = {
	title: '电影兔',
	host: 'https://www.dianyingtu.com',
	class_name: '电影&电视剧&综艺&动漫&微电影&短剧',
	class_url: 'dianying&dianshiju&zongyi&dongman&weidianying&dianshiju/duanju',
	searchUrl: '/search/**/page/fypage',
	searchable: 2,
	quickSearch: 0,
	headers: {
	'User-Agent': 'MOBILE_UA',
	},
	url: '/fyclass/page/fypage',
	filterable: 0,
	filter_url: '',
	filter: {},
	filter_def: {},
	detailUrl: '',
	play_parse: true,
	lazy: '',
	limit: 6,
	推荐: '*',
	一级: '.movie-item li;a&&title;.lazy-load-img&&_src;.rs-state&&Text;a&&href',
	二级: {
	title: 'h1&&Text',
	img: '.lazy-load-img&&_src',
	//主要信息;年代;地区;演员;导演,
	desc: '.movie-txt&&p:eq(2)&&em&&Text;.movie-txt&&p:eq(4)&&em&&Text;.movie-txt&&p:eq(5)&&em&&Text;.movie-txt&&p:eq(1)&&em&&Text;.movie-txt&&p:eq(0)&&em&&Text',
	content: '.content--p&&Text',
	tabs: '.tab-list li',
	//lists: '.episodes-list:eq(#id)&&a'
	lists:`js:
		let id=input.split("/").pop();
		let c=vod.vod_play_from.split('$$$').length;
		let pd='';
	let url=HOST+'/common/api_getTargetRsBoxData.php';
		for (let i=0;i<c;i++){
			pd='order=getTargetRsBoxData&ids='+id+'&type=2&index='+i;
			let jo1 = JSON.parse(post(url,{body:pd}));
			let playList = [];
		jo1.data.episodes.forEach(function(playurl) {
			playList.append(playurl["title"]+"$"+playurl["url"])
		})
		LISTS.append(playList)
		}
	`
	},
	搜索: '.collect-list.mt15 li;h5&&Text;.lazy-load-img&&_src;.rstype&&Text;*;.line-two&&Text'
}