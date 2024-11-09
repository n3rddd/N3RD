var rule = {
    模板: '首图2',
    title:'泥巴影院',
    host: 'https://nbys.app',
	    headers:{
        'User-Agent':'PC_UA'
    },
    url:'/genre/fyclass---fypage/by/time.html',
    searchUrl:'/search/**----------fypage---.html',
                二级: {
                title: '.stui-content__detail .title&&Text;p.data a&&Text',
                img: '.stui-content__thumb .lazyload&&data-original',
                desc: '.stui-content__detail p&&Text;.stui-content__detail&&p:eq(-2)&&a:eq(2)&&Text;.stui-content__detail&&p:eq(-2)&&a:eq(1)&&Text;.stui-content__detail p:eq(2)&&Text;.stui-content__detail p:eq(1)&&Text',
                //desc1: '.stui-content__detail p:eq(4)&&Text;;;.stui-content__detail p:eq(1)&&Text',
                content: '.detail&&Text',
                tabs: '.stui-pannel__head h4',
                lists: '.stui-content__playlist:eq(#id) li',
            },
}