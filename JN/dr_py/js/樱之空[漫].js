var rule = {
  title: '樱之空',
  host: 'https://www.skr2.cc/',
  url: '/vodshow/fyclass--------fypage---.html',
  searchUrl: '/vodsearch/**----------fypage---.html',
  searchable: 2,
  quickSearch: 0,
  filterable: 0,
  headers: {
    'User-Agent': 'MOBILE_UA',
  },
   class_name: '全部&国漫&日漫&美漫&桜歌&桜剧',
   class_url: '1&47&46&85&3&32',
  play_parse: true,
/*  lazy:`js:
		var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
		var url = html.url;
		if (html.encrypt == '1') {
			url = unescape(url)
		} else if (html.encrypt == '2') {
			url = unescape(base64Decode(url))
		}
		if (/\\.m3u8|\\.mp4/.test(url)) {
			input = {
				jx: 0,
				url: url,
				parse: 0
			}
		} else {
			input
		}
	`,*/
  limit: 6,
  double: true,
  一级: 'body&&.ranklist_thumb;a&&title;a&&data-original;.text_right&&Text;a&&href',
  二级: {
    title: 'h1&&Text;.star_tips&&Text',
    img: '.lazyload&&data-original',
    desc: '.data:eq(1)&&Text;.data:eq(2)&&Text;.data:eq(3)&&Text',
    content: '.desc&&Text',
    tabs: '.play_source_tab&&a',
    lists:'#playlistbox:eq(#id) li',
    tab_text: "a&&alt",
    list_text: "body&&Text",
    list_url: "a&&href"
    
  },
  搜索: 'body&&.searchlist_item;h4&&Text;a&&data-original;.text_right&&Text;a&&href',
}