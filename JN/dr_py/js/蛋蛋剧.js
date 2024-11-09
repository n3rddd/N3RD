// 地址发布页 https://www.dandanju.vip
// 搜索安全验证 > 通过drpy_ocr验证码接口过验证OK

function verifyLogin(url) {
    let cnt = 0;
    let cookie = '';
    let r = Math.random();
    let yzm_url = getHome(url) + '/index.php/verify/index.html';
    log(`验证码链接:${yzm_url}`);
    let submit_url = getHome(url) + '/index.php/ajax/verify_check';
    log(`post登录链接:${submit_url}`);
    while (cnt < OCR_RETRY) {
        try {
            let {cookie, html} = reqCookie(yzm_url + '?r=' + r, {toBase64: true});
            let code = OcrApi.classification(html);
            log(`第${cnt + 1}次验证码识别结果:${code}`);
            html = post(submit_url, {
                headers: {Cookie: cookie},
                body: 'type=show&verify=' + code,
            });
            html = JSON.parse(html);
            
            if (html.code === 1) {
                log(`第${cnt + 1}次验证码提交成功`);
                log(cookie);
                return cookie // 需要返回cookie
            } else if (html.code !== 1 && cnt + 1 >= OCR_RETRY) {
                cookie = ''; // 需要清空返回cookie
            }
        } catch (e) {
            log(`第${cnt + 1}次验证码提交失败:${e.message}`);
            if (cnt + 1 >= OCR_RETRY) {
                cookie = '';
            }
        }
        cnt += 1
    }
    return cookie
}

globalThis.verifyLogin = verifyLogin;

var rule = {
    title:'蛋蛋剧',
    // host:'https://www.dandanju.cc',
    host:'https://www.dandanju.vip',
    hostJs:'print(HOST);let html=request(HOST,{headers:{"User-Agent":PC_UA}});let src=jsp.pdfh(html,"a:eq(0)&&href");print(src);HOST=src',
    // url:'/show/fyclass--------fypage---.html',
    url:'/show/fyclassfyfilter.html',
    filterable:1,//是否启用分类筛选,
    filter_url:'-{{fl.area}}-{{fl.by}}-{{fl.class}}-{{fl.lang}}-{{fl.letter}}---fypage---{{fl.year}}',
    filter:'H4sIAAAAAAAAA+2Y3W4aRxTHXyXaa1/s4nw1rxLlgkZIiZqmkp1GsiJLtjEEiAsYOTgE/NUY4zjGXmzHgaXAy+zMwlt02Dkfg1qvUGOlSuQ7fufMzJ5zhvmf2X1lOdaDh6+sXxIL1gPr8bP4/Lw1Yz2P/5pQKLINmUwpfhl/9nsiHPd8bE4djpKHY7MCa3EGrOWaGg9WAPQFmRYsxIC+W3K5KJfK4ASgRXOHfq+Gi2qgRRvrotPFRTXQPIqcAX0y8873svg8DegbNg/E2hH4AOh5udOghz4AI85go8txjoF89dccJwDF0jzw+7sYiwaaly6NKh9xngaat32kIsd5GsgXUU+5chyU19GngXzJnFx5jz4NlHu3IFJtzF0D+kZbJfmuDj4AWrP8epj1cE0NlF//JNj4LHotTJGYRhT2hx9oFzWQL58WhTP0aaBdHBTVHuAuauCq1uTWOlU1BPKtDoJPmAkAVaC3HnRrEwFPmBYfjUfqYxSfS8SNU1RzxZo37Snab4wqaQxBAxX6oCLbp1hoDVwqV3b6VKoQKPR+XlR7GLQG2qDzt+wDoDK+abEPgOZt1mXtGOdpoDh3PvI8AN70L+wD4FhcMxZ3Yt4frvAOcJ4GmrdaUJUSGTwrzJRJfRAUmkG2gskQ8wHelW8GahqdYWQakbr0u3isAMxNX0jE54xN71z43d6Umx6zY7fBFv407LNsnzXtMbbHTLvDdse022y3DbvzE9nVT8N+n+33Tfs9tt8z7XfZfte032H7HdPO+Tpmvg7n65j5OpyvY+brcL6Oma/D+aqf5jb9vMCbJPMl4RX+sUly83K0eQELvHiqhuLCvudJdwM8T56+mOd/2OmqyOC5nX/821xi/NRHM1bsutprhBZGdTQtyGL5UiQLExoNpmnatzi5FF4TfRqm7IpXdu+orhjVvaN0P6pL+Z091n0A7nwpWUFhBaDnvU1zpwUwegLXDGBaufiaHpFOqfHUwkKYRnv/a/+I0vro3nK1nkf2lrKr5Fds7dG9AflGi79/LSa7zfnaZr4252ub+dqcl23mZXNetpmXzXmpn/9nD5i9ph4wWsoGjSU8wBpMDVvdMTRMAQV2Mhi6GTxsGmheqSlzeOcF4IOfkm3UUwAWmnO/UyShCcEQhdEHjAWAfN6RONlGnwZ6XvXMeFvQQPM2duQFve1poHnttswUfK/Et/4JE9Xh4k/VFbAOGmiN1spweQ1na/gGeq00WKktBR2CobtKwVl3x0C+44YqLPo03Cjgj66AnK9t5vv9KuPta1LGKPWL+k4UJJvDPVRUAFozfxgUMWgA8hW3g2P6jqKBj/vV322Gxa1hHm/qALTm7p6o4i0bYJqbtKx5xrcgDfS8iC8hUW8NwlVlwk0GMH31c8OngOq53/f/wm9IAHxz3xGZKt3cQ+C/zploYjcBoDWrOVnBrgDAdWmJwSbVJYRvcQOv9nyPXpY0THNb/lfVvrnT3ij6j6Loi38DX/yg2lAYAAA=',
    searchUrl:'/search/**----------fypage---.html',
    searchable:2,//是否启用全局搜索,
    quickSearch:0,//是否启用快速搜索,
    headers:{
        'User-Agent':'MOBILE_UA'
    },
    timeout:5000,//网站的全局请求超时,默认是3000毫秒
    class_parse:'ul.swiper-wrapper&&li;a&&Text;a&&href;.*/(.*?).html',
    play_parse:true,
    lazy: $js.toString(() => {
        let js = 'try{function requestApix(callback){$.post(\"api.php\",{vid:getQueryString(\"vid\")},function(result){callback(result.data.url);},\"json\");}requestApix(function(data){location.href=sign(data);})}catch(e){}location.href=document.querySelector(\"#playleft iframe\").src;';
        input = {
            parse: 1,
            url: input,
            click: js,
            js: js
        };
    }),
    limit:6,
    推荐:'.tab-content&&li;.lazyload&&title;.lazyload&&data-original;.pic-text&&Text;a&&href',
    一级二:'.ewave-vodlist&&li;.lazyload&&title;.lazyload&&data-original;.pic-text&&Text;a&&href',
	一级: $js.toString(() => {
         let cookie = getItem(RULE_CK, '');
        //log('储存的cookie:' + cookie);
        
        let ret = request(MY_URL, {
            headers: {
                Referer: encodeUrl(MY_URL),
                Cookie: cookie,
            }
        });
        if (/系统安全验证/.test(ret)) {
            //log(ret);
            cookie = verifyLogin(MY_URL);
            if (cookie) {
                log(`本次成功过验证,cookie:${cookie}`);
                setItem(RULE_CK, cookie);
            } else {
                log(`本次验证失败,cookie:${cookie}`);
            }
            ret = request(MY_URL, {
                headers: {
                    Referer: encodeUrl(MY_URL),
                    Cookie: cookie,
                }
            });
        }
//log(ret);
        let d = [];
        let p = rule.一级二.split(';');
        let arr = pdfa(ret, p[0]);//列表
        arr.forEach(it => {
            d.push({
                title: pdfh(it, p[1]),//标题
                pic_url: pdfh(it, p[2]),//图片
                desc: pdfh(it, p[3]),//描述
                url: pdfh(it, p[4]),//链接
                
            });

        });
        setResult(d);
    }),
    二级:{
        "title":".picture&&title;.data--span:eq(0)&&Text",
        "img":".picture&&img&&data-original",
        "desc":".pic-text:eq(0)&&Text;;;.data--span:eq(1)&&Text;.data--span:eq(2)&&Text",
        "content":".desc--a&&Text",
        "tabs":".nav-tabs&&li",
        "lists":".tab-pane:eq(#id)&&li"
    },
    搜索: '.ewave-vodlist__media&&li;a&&title;a&&data-original;.hidden-xs--span&&Text;a&&href',
}