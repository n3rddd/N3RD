Object.assign(muban.mxpro.二级, {
    tab_text: 'div--small&&Text',
});
var rule = {
    模板: 'mxpro',
    title: '嘀哩嘀哩',
    host: 'http://www.dilidili23.com',
    url: '/index.php/vod/show/id/fyclass/page/fypage.html',
    searchUrl: '/index.php/vod/search/page/fypage/wd/**.html',
    class_parse: '.navbar-items li:gt(0):lt(8);a&&Text;a&&href;/(\\d+).html',
	lazy: $js.toString(() => {
		let html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
		let url = html.url;
		if (html.encrypt == '1') {
			url = unescape(url)
		} else if (html.encrypt == '2') {
			url = unescape(base64Decode(url))
		}
if (/\.m3u8/.test(url)) {
            let body = request(url);
            let lines = body.split('\n');
            let m3u8Url = null;
            for (let line of lines) {
                line = line.trim();
                if (line.endsWith('.m3u8')) {
                    m3u8Url = urljoin(url,line);
                    console.log(m3u8Url);
                    break;
                }
            }
            input = {
                jx: 0,
                url: m3u8Url || url,
                parse: 0
            };
    } else {
			input = {
                jx: tellIsJx(url),
                url: url,
                parse: 0
            };
		}
	}),
}