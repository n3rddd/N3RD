Object.assign(muban.mxpro.二级, {
    tab_text: 'div--small&&Text',
});
var rule = {
    模板: 'mxpro',
    title: '剧哥哥',//https://jugege.com/
    host: 'https://www.jugege.top',
    class_parse: '.navbar-items li:gt(0):lt(8);a&&Text;a&&href;/(\\d+).html',
    url: '/vodshow/fyfilter.html',
    filter_url: '{{fl.cateId}}-{{fl.area}}-{{fl.by}}-{{fl.class}}-----fypage---{{fl.year}}',
    searchUrl: '/rss/index.xml?wd=**',
    搜索: $js.toString(() => {
        let html = request(input);
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
    filter_def: {
        1: {cateId: '1'}, 2: {cateId: '2'}, 4: {cateId: '4'}, 3: {cateId: '3'}
    },
    filter: 'H4sIAAAAAAAAA+2W308aQRDH/5d79sEDf9V/pfGBGpKaWpuAbUIMSSuCoFaEIEpFa1P5oRWB1lo5cvDP3O7Jf9GF3ZlZWnshbR/v7T7f2dmd2dnduQ3DNBafbhgvwjFj0VheDUWjxpSxFnoZFsgyNZ5ICn4TWn0dHo1bG8rJ+iBRH8oCjPiUUotlMV6pCsDmpttqIgKw8XcH/G1R2RTgnDt1xy7DnBJwzlqOdbowpwT0w8AJcL30sWNlYD0JYHtoVNnelbIpwPV2mq4NNgVanG6hS3EOAW2VbYpTAcbSqDq9c4hFAvql8oPSJfhJQL+zKxE5+EmYZD/55rVbzIFNAtoSO3zzA9gkYO7dLEveQ+4SwDY4zfPjirIpwDmL2w8ZC+aUgPn1btzCd2a3IUVkHJG9ePiMVZSAtv0Uy34FmwSsYv9A1ACqKIF2tcxPc7irI0DbVt/9ApkowB2wc263PBbwmBRfGo6UtygUCYe0S1RusT1r0kt0URuUUhCCBNzoaonfN2GjJdBWtXinh1s1Agy9t89ObAhaAhbo2yHZFOA27rbJpgD9jiq8fA1+EjDOj5fkp4CK/oNsCiiWlh5La8zvfYtZVfCTgH5bWbFTLA13hRgzqfTdbMPNlCAZZLrA53y3L9zwDgPjiOSd04VrpUAveiwcimhF79w6XXvCogemAzNKG31qepD0oK4HSA/oukm6qevTpE9ruvkEdfGp6QukL+j6POnzuj5H+pyuz5I+q+uUr6nna1K+pp6vSfmaer4m5Wvq+ZqUr/jUy/QsRkXi+3lmZX8rEj+6GxzdqgnWV8RQmNixLN4qKMvzlfUonbDmFkvDvY0uv4qEh6suTRmB/9VdPd5Cr47m1ZXZzR2zGmCTMGG3+2NX9up2Xl3Z6z336j5iDl6CR1EBlqvzid56BbjeYYo6qIJJ/lY8/zoe69h+X/D7gt8X/L7wS18Ian3BPyL+EXnkiMxoR+RfWseJ7Vj4fkmY5Lnm1zXRFMAmwX/0/BP91yc6/hNlKCPlbBIAAA=='
}