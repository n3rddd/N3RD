var rule = {
    title: '926tv',
    host: 'https://www.926.tv/',
    url: '/fyclass',
    searchUrl: '',
    searchable: 1,
    quickSearch: 0,
    class_name: '全部',
    class_url: '/',
    //class_url:'?live',
    headers: {
        'User-Agent': 'MOBILE_UA'
    },
    timeout: 5000,
    play_parse: true,
    lazy: '',
    limit: 6,
    double: false,
    推荐: '*',
    一级: $js.toString(() => {
        let d = [];
        pd=jsp.pd;
        pdfh=jsp.pdfh;
        pdfa=jsp.pdfa;
       
        let html = request(input);
        let tabs = pdfa(html, '.list_content&&a');
        tabs.forEach((it) => {
            let ps = pdfh(it, '.eventtime&&em&&Text');
            let pz = pdfh(it, '.zhudui&&p&&Text');
            let pk = pdfh(it, '.kedui&&Text');
            let img = pd(it, 'img&&op-zfr-a-g');
            let timer = pdfh(it, '.eventtime&&i&&Text');
            let url = pd(it, 'a.clearfix&&href');
            d.push({
                title: pz + '🆚' + pk,
                desc: timer + '🏆' + ps,
                img: img,
                url: url
            });
        });
        setResult(d);
    }),
    二级: {
        title: "h2.biaoti&&Text",
       img: "img&&src",
        desc: "",
        content: "title&&Text",
        "tabs": "js:TABS=['道长在线']",
        lists: $js.toString(() => {
            LISTS = [];
        pd=jsp.pd;
        pdfh=jsp.pdfh;
        pdfa=jsp.pdfa;
            let lists1=[];
            let src=pdfh(html,'#myiframe&&src');
            lists1.push('在线播放' + '$' + src);
            LISTS.push(lists1);
        }),
    },
    搜索: '',
}
