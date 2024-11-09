function geturl(a) {
    let yjstr=req(a).content;
    let yjurl1=jsp.pdfh(yjstr,'body&&a&&href');
    yjurl1=yjurl1.match(/.*target=(.*)\//)[1];
    let yjstr2=fetch(yjurl1);
    let yjlist=jsp.pdfa(yjstr2,'body&&a.xv');
    let yjurls=[];
    yjlist.forEach(it=>yjurls.push(jsp.pdfh(it,'a&&href')));


    let url=yjurls[Math.floor(Math.random()*yjurls.length)];
    return url
    
}

globalThis.geturl = geturl;
globalThis.mc ='';
globalThis.tk =''
var rule = {
    title:'xvideos涩涩[密]',
    host:'https://发布地址.com/',
    hostJs:$js.toString(() => {
        HOST=geturl(HOST);

    }),
    //url从http://hsck.net中禁止重定向取
    //let html=req(url,{redirect:0}).headers.location; 另外一种写法 
    homeUrl:'/channels-index/',
    //detailUrl:'/api/front/models/username/fyid/cam?triggerRequest=loadCam',
    searchUrl:'',
    url:'/fyclass/分隔fypage',    
    //headers:{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"},
    timeout:5000,
    //class_parse: 'json:.pingtai;.title;.address;(.*)',//从homeUrl取源码
    class_name:'频道&明星',
    class_url:'channels-index分-隔&pornstars-index分-隔',
    limit:5,
    multi:1,
    searchable:1,
    play_parse:true,
    lazy:$js.toString(() => {
        
    }),
    推荐:$js.toString(() => {

        let html=fetch(HOST+'/profiles/chicken1806/feed/straight', {headers:{'content-type':'application/x-www-form-urlencoded; charset=UTF-8','Cookie':"urlss=https%3A%2F%2Fwww.xvideos.com; HstCfa4797825=1730059354267; HstCmu4797825=1730059354267; __dtsu=4C301730059354E85C3585389B918CCD; HstCnv4797825=2; cit=c5e325341421fbf3-mTL7wCsC3ie9MEJiF8BBw%3D%3D; html5_networkspeed=16590; HstCns4797825=3; HstCla4797825=1730074800063; HstPn4797825=6; HstPt4797825=9;session_token=a3b907e235874ed8g5KbllMn7YDhAc7sILrUQhXQ3YBng0l2QnCVp_SCorYt6krd8CG97DyWEkQVcZMfCo_zxRr4LbwPBg942kwk0jLhsvb4LAEu6poCybp94FYc0-1q362OQgp4hvKcnEUdq_nkNE45c5MZwmY3EjgNhFs8leBOXm4lH-_aUG8Hpsu0ZzHN2im260Sr1Cn4ZwHGt780YJ4kRXbey4T5jSA4Y37HXwDHMzyzkq_9Xd4ndhA%3D"},body:'feedSettings%5BcontentType%5D=7&feedSettings%5BshowFreePremium%5D=1&mainCats%5B%5D=straight',method:'POST'});
        let json=JSON.parse(html);
        let list=json.data.content;

        let d = [];
        list.forEach(it => {
            d.push({
                url:HOST+it.v[0].u,
                title: it.v[0].t,
                img:it.v[0].if
               
            })
        
       });
        setResult(d);
    }),
    一级:$js.toString(() => {
        
        let url=input.match(/(http.*?\/\/.*?)\//)[1];
        let turl,str;
         mc=MY_CATE.replace('分-隔','');
        let ww=MY_CATE;
        let pg=MY_PAGE-1;
        let d = [];

        if(ww.indexOf('分-隔')>-1){
            if(MY_PAGE===1){
                turl=url+`/${mc}`
            }else{
                turl=url+`/${mc}/${pg}`
            }
        }else{
            turl=url+`/profiles/${mc}/feed/straight`
        }
        if(turl.indexOf('feed/straight')===-1){
            str=fetch(turl,{headers:{'Cookie':"urlss=https%3A%2F%2Fwww.xvideos.com; HstCfa4797825=1730059354267; HstCmu4797825=1730059354267; __dtsu=4C301730059354E85C3585389B918CCD; HstCnv4797825=2; cit=c5e325341421fbf3-mTL7wCsC3ie9MEJiF8BBw%3D%3D; html5_networkspeed=16590; HstCns4797825=3; HstCla4797825=1730074800063; HstPn4797825=6; HstPt4797825=9;session_token=a3b907e235874ed8g5KbllMn7YDhAc7sILrUQhXQ3YBng0l2QnCVp_SCorYt6krd8CG97DyWEkQVcZMfCo_zxRr4LbwPBg942kwk0jLhsvb4LAEu6poCybp94FYc0-1q362OQgp4hvKcnEUdq_nkNE45c5MZwmY3EjgNhFs8leBOXm4lH-_aUG8Hpsu0ZzHN2im260Sr1Cn4ZwHGt780YJ4kRXbey4T5jSA4Y37HXwDHMzyzkq_9Xd4ndhA%3D",'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0'}});
        }else{
            if(MY_PAGE===1){
                str=fetch(turl, {headers:{'content-type':'application/x-www-form-urlencoded; charset=UTF-8','Cookie':"urlss=https%3A%2F%2Fwww.xvideos.com; HstCfa4797825=1730059354267; HstCmu4797825=1730059354267; __dtsu=4C301730059354E85C3585389B918CCD; HstCnv4797825=2; cit=c5e325341421fbf3-mTL7wCsC3ie9MEJiF8BBw%3D%3D; html5_networkspeed=16590; HstCns4797825=3; HstCla4797825=1730074800063; HstPn4797825=6; HstPt4797825=9;session_token=a3b907e235874ed8g5KbllMn7YDhAc7sILrUQhXQ3YBng0l2QnCVp_SCorYt6krd8CG97DyWEkQVcZMfCo_zxRr4LbwPBg942kwk0jLhsvb4LAEu6poCybp94FYc0-1q362OQgp4hvKcnEUdq_nkNE45c5MZwmY3EjgNhFs8leBOXm4lH-_aUG8Hpsu0ZzHN2im260Sr1Cn4ZwHGt780YJ4kRXbey4T5jSA4Y37HXwDHMzyzkq_9Xd4ndhA%3D",'Referer':turl},body:'feedSettings%5BcontentType%5D=7&feedSettings%5BshowFreePremium%5D=1&mainCats%5B%5D=straight',method:'POST'});
                let json=JSON.parse(str);
                tk=json.metadata.lastEventTime;
            }else{
                str=fetch(turl+'/'+tk, {headers:{'content-type':'application/x-www-form-urlencoded; charset=UTF-8','Cookie':"urlss=https%3A%2F%2Fwww.xvideos.com; HstCfa4797825=1730059354267; HstCmu4797825=1730059354267; __dtsu=4C301730059354E85C3585389B918CCD; HstCnv4797825=2; cit=c5e325341421fbf3-mTL7wCsC3ie9MEJiF8BBw%3D%3D; html5_networkspeed=16590; HstCns4797825=3; HstCla4797825=1730074800063; HstPn4797825=6; HstPt4797825=9;session_token=a3b907e235874ed8g5KbllMn7YDhAc7sILrUQhXQ3YBng0l2QnCVp_SCorYt6krd8CG97DyWEkQVcZMfCo_zxRr4LbwPBg942kwk0jLhsvb4LAEu6poCybp94FYc0-1q362OQgp4hvKcnEUdq_nkNE45c5MZwmY3EjgNhFs8leBOXm4lH-_aUG8Hpsu0ZzHN2im260Sr1Cn4ZwHGt780YJ4kRXbey4T5jSA4Y37HXwDHMzyzkq_9Xd4ndhA%3D",'Referer':turl},body:'feedSettings%5BcontentType%5D=7&feedSettings%5BshowFreePremium%5D=1&mainCats%5B%5D=straight',method:'POST'});
                let json=JSON.parse(str);
                tk=json.metadata.lastEventTime;
           }

        }
        if(str.indexOf('<title>')>-1){
            let list=jsp.pdfa(str,'body&&.mozaique&&.thumb-block');        
            list.forEach(it => {
            d.push({
                //vod_id:url+'/profiles/'+it.match(/profile_(.*?)"/)[1]+'/feed/straight',
                vod_id:it.match(/profile_(.*?)"/)[1],
                vod_name: pdfh(it,'.profile-name&&Text'),
                vod_pic:it.match(/img src="(.*?)"/)[1],
                vod_tag: 'folder'
                //.match(/(http.*?)'/)[1]
            })
        
       });
        }else{
            let json=JSON.parse(str);
           
            let list=json.data.content;   
            let urls=[];
            list.forEach(it=>{
           
            d.push({
                vod_id:url+it.v[0].u,
                vod_name: it.v[0].t,
                vod_pic:it.v[0].if,
                
            })

        })
        }
        
       VODS =d;
    }),
    二级:$js.toString(() => {
            let html=fetch(input,{headers:{'Cookie':"urlss=https%3A%2F%2Fwww.xvideos.com; HstCfa4797825=1730059354267; HstCmu4797825=1730059354267; __dtsu=4C301730059354E85C3585389B918CCD; HstCnv4797825=2; cit=c5e325341421fbf3-mTL7wCsC3ie9MEJiF8BBw%3D%3D; html5_networkspeed=16590; HstCns4797825=3; HstCla4797825=1730074800063; HstPn4797825=6; HstPt4797825=9;session_token=a3b907e235874ed8g5KbllMn7YDhAc7sILrUQhXQ3YBng0l2QnCVp_SCorYt6krd8CG97DyWEkQVcZMfCo_zxRr4LbwPBg942kwk0jLhsvb4LAEu6poCybp94FYc0-1q362OQgp4hvKcnEUdq_nkNE45c5MZwmY3EjgNhFs8leBOXm4lH-_aUG8Hpsu0ZzHN2im260Sr1Cn4ZwHGt780YJ4kRXbey4T5jSA4Y37HXwDHMzyzkq_9Xd4ndhA%3D"}});
            let list=html.match(/html5player\.setVideo.*?;/ig).slice(1,4);
            let urls=[];
            let furl=html.match(/setVideoHLS\('(.*?)'/)[1];
            list.map(a=>urls.push(a.match(/setVideo(.*?)\(/)[1]+'$'+a.match(/(http.*?)'/)[1]));
            let pul=[];

            let str=fetch(furl);
            let flist=[];
            if(str!=''){
            flist=str.match(/EXT-X-STREAM-INF.*?\n.*/g);
            flist.forEach(it=>{
                pul.push(it.match(/NAME="(.*?)"/)[1]+'$'+furl.replace("hls.m3u8","")+it.match(/(hls.*)/)[1] )
            })
            }


            let vod={
            vod_id:'',
            vod_name:html.match(/setVideoTitle\('(.*?)'/)[1],
            vod_pic:html.match(/setThumbSlideBig\('(.*?)'/)[1],
            type_name:'来自海阔',
            vod_content:"暂无"
        };
        vod.vod_play_from ='不分线路';
        vod.vod_play_url =pul.join('#')+'#'+urls.join('#');;
        VOD=vod
    }),
    搜索:'',
}