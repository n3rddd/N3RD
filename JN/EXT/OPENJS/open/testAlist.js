import { __jsEvalReturn } from './alist_open.js';

var spider = __jsEvalReturn();

async function test() {
    await spider.init({
        skey: 'siteKey',
        ext: [
            {
                name: '🙋丫仙女',
                server: 'http://v.elizen.me/',
                startPage: '/',
                showAll: false,
                search: true,
                headers: {
                    Authorization: '',
                },
                params: {
                    '/abc': {
                        password: '123',
                    },
                    '/abc/abc': {
                        password: '123',
                    },
                },
            },
            {
                name: '🐋一只鱼',
                server: 'https://alist.youte.ml',
            },
            {
                name: '🌊七米蓝',
                server: 'https://al.chirmyram.com',
            },
            {
                name: '🐉神族九帝',
                server: 'https://alist.shenzjd.com',
            },
            {
                name: '☃️姬路白雪',
                server: 'https://pan.jlbx.xyz',
            },
            {
                name: '✨星梦',
                server: 'https://pan.bashroot.top',
            },
            {
                name: '💢repl',
                server: 'https://ali.liucn.repl.co',
            },
            {
                name: '💦讯维云盘',
                server: 'https://pan.xwbeta.com',
            },
        ],
    });

    var files = JSON.parse(await spider.dir('/'));
    console.log(files);

    files = JSON.parse(await spider.dir(files.list[0].path));
    console.log(files);

    // files = JSON.parse(await spider.dir('/🙋丫仙女/电视剧/欧美/4K/00 漫威衍生美剧/L 猎鹰与冬兵4K（2021）【美剧】豆瓣评分：7.5/'));
    // console.log(files);

    var fileInfo = JSON.parse(await spider.file('/💦讯维云盘/热播短剧/傲世神尊/01.mp4'));
    console.log(fileInfo);

}

export { test };
