var rule = {
author: '小可乐/2408/第一版',
title: '木偶哥哥[盘]',
类型: '影视',
host: 'http://mogg.top',
hostJs: '',
headers: {'User-Agent': 'MOBILE_UA'},
编码: 'utf-8',
timeout: 5000,

homeUrl: '/',
url: '/index.php/vod/show/id/fyfilter.html',
filter_url: '{{fl.cateId}}{{fl.area}}{{fl.by}}{{fl.class}}{{fl.lang}}{{fl.letter}}/page/fypage{{fl.year}}',
detailUrl: '',
searchUrl: '/index.php/vod/search/page/fypage/wd/**.html',
searchable: 1, 
quickSearch: 1, 
filterable: 1, 

class_name: '木偶电影&木偶剧集&木偶动漫&木偶纪录',
class_url: '1&2&3&4',
filter_def: {
1: {cateId: '1'},
2: {cateId: '2'},
3: {cateId: '3'},
4: {cateId: '4'}
},

play_parse: true,
lazy: `js:
let type = '';
if (/quark/.test(input)) {
    type = 'quark'
} else if (/uc/.test(input)) {
    type = 'uc'
} else if (/aliyundrive|alipan/.test(input)) {
    type = 'ali'
};
let confirm= '';
input = getProxyUrl().replace('js',type)+'&type=push'+confirm+'&url='+encodeURIComponent(input)
`,

limit: 9,
double: false,
推荐: '*',
一级: '.module-item;img&&alt;img&&data-src;.module-item-text&&Text;a:eq(0)&&href',
二级: {
title: 'h1&&Text;.tag-link:eq(1)&&Text',
img: '.video-cover&&img&&data-src',
desc: '.video-info-items:eq(-2)&&Text;.tag-link:eq(-2)&&Text;.tag-link:eq(-1)&&Text;.video-info-actor:eq(1)&&Text;.video-info-actor:eq(0)&&Text',
content: '.sqjj_a--span&&Text',
tabs: '.downtab-item',
tab_text: 'body--small&&Text',
lists: '.module-row-one:eq(#id)&&a.btn-down',
list_text: 'a&&title',
list_url: 'a&&href'
},
搜索: '.module-search-item;*;*;.video-serial&&Text;.video-serial&&href',

filter: 'H4sIAAAAAAAAA+2XW08TQRTH3/sx9hlTtihe3lREwRsXrxgfqjZqREygmhBCApZWLkKFYGu1eIlAASktXlC2KXyZzm77LZxlZs/MnCWyBBN92Mf+f/+emTkzO3POQEDTtRO3AgPao0i/dkK72x3u69PqtJ7w4wj9ScZyZixOfz8Ldz+lwq0BrceW40u12JIt0x/aYB1XU1nq52pwJ1KQa47FGl3n8YSFa47FHH5lDqVUC9dgoPGlSjmLBmIaDJSbJpslNBDTIAqsTYrCNJjL6JuKMYbmwjTHUs0vkpcrqoVrMJfxglVGFq5JK7JmS64V2RpYFl64VsQ1mG5+sbL1EU2XaRAlMVPLLKMoTIMo71foGlEUpoHl+aqVmkYWpoElNm4+f4ssTIO8lJIk/gvlhWmOpTY3Y75ZUC1cg4FSL6pjBhqIabDorTVr9gcpr6N1gwzG5Hz1Mz4STAPLVIIkvyIL0+BIbL+ie4eOBNPENmTNuWm8DTsaWEa2rS9o6VyDBJanrVJ2t6UpZPD2YB184OHeSFj6vrNF8tLw+n3P52qZhDOQHSjIJdiuxYz5q6A4uCQyXDQ3t9QYTIJFbU2Rd2XFwSXY8W+vsYNLsAMT69jBJYiRXjCzq2oMJsFaPizjGFwSx+ondnBJzLTonmlRiTFZJMaiGoNJEGMkSbNMRpfVMKDCmhe2rWTeGsuoywZVXDUfzYlt+md1UFDBF9+olFKqiUnKeeoO99wX56layFeXhryep3dl6ndGsAMFuSTtI3ZwCU7L13ns4BLsY7pMJtPYJFRpv10mJklnBju4JJ1Ml4NJ0plxrZlJUt7JWkx1MEnJe38k3CvybqY3aunvHvMeqg8dduLbYYI7gkQbMG2QaQjTkEx1THWZ1mNaL1H9OKJUkOgxTI/J9CimR2XaiGmjTI9gekSmOFe6nCsd50qXc6XjXOlyrnScK13OlY5zRQX1y4tEoxHpDJB82ixMejwDJ+GA7UQJngRyCpFTQE4jchpIEyJNQM4gcgZIMyLNQM4ichbIOUTOAWlBpAVIKyKtQM4jch7IBUQuALmIyEUglxC5BOQyIpeBtCHSBqQdkXYgHYh0AOlEpBPIFUSuALmKyFUg1xC5BuQ6IteB3EDkBpCbiNwE0oVIF5D6Q8cRsxXlG7jTL92BUzPESLrOv7ga7UB3+oPRh9TujFExDLM4K9EHD6N94v0pjJDRhET77j7pjdhTCNyuC2ghpXMKRyMt98R0rPUSeT/x589R3Ab04asYOdE+SdeIuZqzCyCBxP1Dnx+7JhFIXFy06KKFlYQa1cwdqNHbu0z20DmxOp4Mb5BYcrcKn5N9dJdkbYMYeWRh2v56sb26Sw+9mIfu0kMr4aFFqmx+crUSXBO9WNzMFNBmMA3m8jrhavq4JnUbrg3g2u41I4+yS9F4kCYkEad+tSxlkvfC/W+0KXs3EF4amb3aAw+NTKpIa3cy90kNA6pfzgvTfst5vxT3S3G/FPdLcb8U/+9L8YaDluLirmCluFOhi1uRFduOLu4HVp87esh/G/y3wX8b/LfBfxv+l7fhsPw2+BeyfyH7F7J/IfsX8j+6kAODvwEbh23DdCQAAA=='
}