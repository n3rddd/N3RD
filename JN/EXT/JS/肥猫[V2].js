var rule = {
	title: '肥猫[V2]', 
	host: 'http://i.xn--z7x900a.love:63',
	homeUrl:'/api.php/provide/vod?ac=detail&pg=1&f=',
	url: '/api.php/provide/vod/?t=fyclass&ac=detail&pg=fypage',
	detailUrl:'/api.php/provide/vod?ac=detail&ids=fyid',
	searchUrl: 'api.php/provide/vod?ac=detail&wd=**',
	searchable: 2,
	quickSearch: 0,
	filterable: 0,
	headers:{'User-Agent':'Mozilla/5.0'},
	timeout:5000,
	class_name:'电影&电视剧&动漫&综艺',
	class_url:'1&2&3&4',
	play_parse:true,
  	lazy:`js:input = {
					jx:0, 
					parse: 1,
					url:'https://fy.wuye3d.com/fy27.php?url=' + input, 
					header:{
						'User-Agent':'Mozilla/5.0 (iPad)', 
						'Referer':'http://www.tvyb03.com/'}
				}
	`,
	
	推荐:'*',
	一级:'json:list;vod_name;vod_pic;vod_remarks;vod_id',
	二级:'js:try{let html=request(input);print(html);html=JSON.parse(html);let node=html.list[0];VOD={vod_id:node["vod_id"],vod_name:node["vod_name"],vod_pic:node["vod_pic"],type_name:node["vod_class"],vod_year:node["vod_year"],vod_area:node["vod_area"],vod_remarks:node["vod_remarks"],vod_actor:node["vod_actor"],vod_director:node["vod_director"],vod_content:node["vod_content"].strip(),vod_play_url:node["vod_play_url"],vod_play_from:node["vod_play_from"]};}catch(e){log("获取二级详情页发生错误:"+e.message)}',
	搜索:'*',
}