var rule = {
  title: 'HBOTV[优]',
  host: 'https://www.hbotv1.com/',
  url: '/fyclass/index_fypage.html[/fyclass/index.html]',
  searchUrl: '/vodsearch/**-fypage/',
  searchable: 2,
  quickSearch: 0,
  filterable: 0,
  headers: {
    'User-Agent': 'PC_UA',
  },
  class_parse: '.stui-header__menu li;a&&Text;a&&href;.*/(.*?)/',
  play_parse: true,
  lazy: "js:\n  let html = request(input);\n  let hconf = html.match(/r player_.*?=(.*?)</)[1];\n  let json = JSON5.parse(hconf);\n  let url = json.url;\n  if (json.encrypt == '1') {\n    url = unescape(url);\n  } else if (json.encrypt == '2') {\n    url = unescape(base64Decode(url));\n  }\n  if (/\\.(m3u8|mp4|m4a|mp3)/.test(url)) {\n    input = {\n      parse: 0,\n      jx: 0,\n      url: url,\n    };\n  } else {\n    input;\n  }",
  limit: 6,
  double: true,
  推荐: 'ul.stui-vodlist.clearfix;li;a&&title;.lazyload&&data-original;.pic-text&&Text;a&&href',
  一级: 'ul.stui-vodlist.clearfix li;a&&title;.lazyload&&data-original;.pic-text&&Text;a&&href',
  二级: {
    title: '.stui-content__detail .title&&Text;.stui-content__detail&&p:eq(3)&&a&&Text',
    img: '.stui-content__thumb .lazyload&&data-original',
    desc: '.pic-text&&Text;.stui-content__detail&&p:eq(3)&&a:eq(2)&&Text;.stui-content__detail&&p:eq(3)&&a:eq(1)&&Text;.stui-content__detail p--span&&Text;.stui-content__detail p:eq(1)--span&&Text',
    content: '.detail-sketch&&Text',
    tabs: '.stui-pannel__head h3',
    lists: '.stui-content__playlist:eq(#id) li',
  },
  搜索: $js.toString(() => {
        var d = [];
        var body = 'keyboard=' + KEY + '&show=title&tempid=1&tbname=news&mid=1&dopost=search'; //log(body)
        var headers = `{
            'Host': 'www.hbotv1.com',
            'content-length': '79',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'origin': 'https://www.hbotv1.com',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Linux; Android 12; 22021211RC Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/99.0.4844.88 Mobile Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'x-requested-with': 'com.example.hikerview',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.hbotv1.com/vodsearch/203070-0/',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        }`;
        var html = fetch('https://www.hbotv1.com/e/search/index.php', {
            headers: headers,
            body: body,
            method: 'POST'
        }); //log(html)
        
        var list = pdfa(html, '.stui-vodlist__media&&li');
        for (var j in list) {
            d.push({
                title: pdfh(list[j], '.lazyload&&title'),
                desc: pdfh(list[j], '.pic-text&&Text'),
                img: pd(list[j], '.lazyload&&data-original') + '@Referer=',
                url: 'https://www.hbotv1.com'+pdfh(list[j], '.lazyload&&href') + '#immersiveTheme#'
            });
        }
        setResult(d);
    }),
}