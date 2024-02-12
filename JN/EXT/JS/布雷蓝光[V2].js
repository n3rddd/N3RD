var rule = {
	title: '布雷蓝光[V2]', // csp_AppYsV2
	host: 'http://117.175.212.198:8088',
	//host: 'https://appto-v3-1251970844.cos.ap-chongqing.myqcloud.com/accredits/68.json',
	//hostJs:'print(HOST);let html=request(HOST,{headers:{"User-Agent":"Dart/3.0 (dart:io)"}});let src = JSON.parse(html).domain;print(src);HOST=src',
	homeUrl:'/api.php/app/index_video',
	url: '/api.php/app/video?tid=fyclassfyfilter&limit=18&pg=fypage',
	filter_url:'&class={{fl.class}}&area={{fl.area}}&lang={{fl.lang}}&year={{fl.year}}',
	filter: {
		"1":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""}]}],
		"2":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""}]}],
		"3":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""}]}],
		"4":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""}]}],
		"24":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""}]}]
	},
	detailUrl:'/api.php/app/video_detail?id=fyid',
	searchUrl: '/api.php/app/search?text=**&pg=fypage',
	searchable: 2,
	quickSearch: 0,
	filterable: 0,
	headers:{'User-Agent':'Dart/3.0 (dart:io)'},
	timeout:5000,
	class_name:'飞云4K&电影&电视剧&综艺&动漫', // 分类筛选 /api.php/app/nav
	class_url:'24&1&2&3&4',
	play_parse:true,
		lazy:`js:input = /Feiyun/.test(input) ? {
		    jx:0, 
		    parse: 1,
		    url:'https://fy.wuye3d.com/fy27.php?url=' + input, 
	        header:{
	    	    'User-Agent':'Mozilla/5.0 (iPad)', 
	    	    'Referer':'http://www.tvyb03.com/'}
	    } : input
	`,
	limit:5,
	推荐:'json:list[1].vlist;*;*;*;*',
	一级:'json:list;vod_name;vod_pic;vod_remarks;vod_id',
	二级:'js:try{let html=request(input);print(html);html=JSON.parse(html);let node=html.data;VOD={vod_id:node["vod_id"],vod_name:node["vod_name"],vod_pic:node["vod_pic"],type_name:node["vod_class"],vod_year:node["vod_year"],vod_area:node["vod_area"],vod_remarks:node["vod_remarks"],vod_actor:node["vod_actor"],vod_director:node["vod_director"],vod_content:node["vod_content"].strip()};let episodes=node.vod_url_with_player;let playMap={};if(typeof play_url==="undefined"){var play_url=""}episodes.forEach(function(ep){let source=ep["name"];if(!playMap.hasOwnProperty(source)){playMap[source]=[]}playMap[source].append(ep["url"])});let playFrom=[];let playList=[];Object.keys(playMap).forEach(function(key){playFrom.append(key);playList.append(playMap[key])});let vod_play_from=playFrom.join("$$$");let vod_play_url=playList.join("$$$");VOD["vod_play_from"]=vod_play_from;VOD["vod_play_url"]=vod_play_url}catch(e){log("获取二级详情页发生错误:"+e.message)}',
	搜索:'*',
}
