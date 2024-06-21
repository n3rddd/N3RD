var rule = {
    模板: '自动',
    title: '策驰影院',
    host: 'https://www.cecidy.cc',
    url: '/vodshow/fyclass--------fypage---/',
    class_parse: '.nav-list&&li;a&&Text;a&&href;/vodtype/(.*?)/',
    searchUrl: '/rss.xml?wd=**',
    搜索: $js.toString(() => {
        let html = post(input.split('?')[0], {body: input.split('?')[1]});
        let items = pdfa(html, 'rss&&item');
        // log(items);
        let d = [];
        items.forEach(it => {
            it = it.replace(/title|link|author|pubdate|description/g, 'p');
            let url = pdfh(it, 'p:eq(1)&&Text');
            d.push({
                title: pdfh(it, 'p&&Text'),
                url: url,
                desc: pdfh(it, 'p:eq(3)&&Text'),
                content: pdfh(it, 'p:eq(2)&&Text'),
                pic_url: "",
            });
        });
        setResult(d);
    }),
}