var rule = {
    title: '172MV',
    host: 'https://m.172mixdj.com',
    url: '/categories/fyclass/new?page=fypage',
    searchUrl: '/searches?s=**',
    searchable: 2,
    quickSearch: 0,
    filterable: 0,
    filter: '',
    filter_url: '',
    filter_def: {},
    headers: {
        'User-Agent': 'MOBILE_UA',
    },
    timeout: 5000,
    class_name: '中文MV舞曲&英文MV舞曲&中文MV串烧',
    class_url: 'zwmv&ywmv&zwcs',
    cate_exclude: '',
    play_parse: true,
    lazy: `js:
  let html = request(input);
  let hconf = html.match(/r player_.*?=(.*?)</)[1];
  let json = JSON5.parse(hconf);
  let url = json.url;
  if (json.encrypt == '1') {
    url = unescape(url);
  } else if (json.encrypt == '2') {
    url = unescape(base64Decode(url));
  }
  if (/\\.(m3u8|mp4|m4a|mp3)/.test(url)) {
    input = {
      parse: 0,
      jx: 0,
      url: url,
    };
  } else {
    input;
  }`,
    double: true,
    推荐: '',
    一级: 'body&&.infinite-item;a&&title;img&&data-src;.video-length&&Text;a&&href',
    二级: '*',
    tab_rename: {
        '道长在线': '在线播放',
    },
    搜索: '*',
}