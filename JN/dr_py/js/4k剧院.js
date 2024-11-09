muban.mxpro.二级.title = 'h1&&Text;.module-info-tag&&Text';
muban.mxpro.二级.desc = '.module-info-item:eq(4)&&Text;;;.module-info-item-content:eq(1)&&Text;.module-info-item-content:eq(0)&&Text';
muban.mxpro.二级.tab_text = 'body--small&&Text';
var rule = {
	title:'4K剧院', //原91free
	模板:'mxpro',
	host:'https://www.4k4k.live',
	    headers:{
        'User-Agent':'PC_UA'
    },
	url:'/vodshow/fyfilter.html',
	filterable:1,//是否启用分类筛选,
	filter_url:'{{fl.cateId}}-{{fl.area}}-{{fl.by or "time"}}-{{fl.class}}-{{fl.lang}}-{{fl.letter}}---fypage---{{fl.year}}',
	filter: 'H4sIAAAAAAAAA+2ZWU8bVxTHv8s88zBjwpa37CH7vlV5cFKrjZpSidBKKEIiBac2BOygBMexA6GF2EkxmEUpjDF8Gd9r+1tk7Hu2SRvLKqhqpHnj//v7zMw59945B/ux5ViHv3ls/RAZtg5b98NDkf5vrQ5rIPxjxNPVtZKam/T0L+GHP0eaHxzwsIrm62P5BvaEY410GFx1P6jyy2r8N3BCNllqIl8pZ9nqZmc2q+I5dnr4crnnarvETi85+klSj86y08cxsTU9FmXHEY8Qz/ktfnAde1Vx48IKWSN3G6apSngwEuaaqGxRPXNb14Rvupirp58CBYFe/V1ab62CB4LiEkW9vYtxRlCOu9MqUwYPBGWy8ZI9EOjVJtfYA0FxqSWdXcY4I+g5599zHAh6zt2/2APBz1KUz1L0xU0VlfsO44yguPGEVykVe4+hpCmTpb1qolCNpzEZ0rzf3urJPS8Mb0GaPhH9WCnNom2EXPSH4YHveNFrq4VafrTdRc+Uvc/jpY0Qi8AeCFrY9UX2QNAipMpqKsU2a7FMwjZCLC97IMSWEZ4RYnlFJkaIAqqVMS5gQ8gCDkfCg+LUbG9WSuU2CxiyQ4foHeL9KXgn807JQ8xDkjvMHclt5rbgTh9xp0/yXua9kvcw75G8m3m35F3MuyTnfB2Zr8P5OjJfh/N1ZL4O5+vIfB3Ot/FKlPs8MjQUkQtVSOnVqTYX6giAI0SOAjlK5BiQY0SOAzlO5ASQE0ROAjlJ5BSQU0ROAzlNpB9IP5EzQM4QOQvkLJFzQM4ROQ/kPJELQC4QuQjkIpFLQC4RuQzkMpErQK4QuQrkKpFrQK4RuQ7kOpEbQG4QuQnkJpFbQG4RuQ3kNpE7QO74NsW9Yd4QenpGuYm/bQid+lhPbUL00APvo3jJiuvq4gtwvn8w9IhffqvjKobd8NH9nwYjjbve7bBC+5xB+AiYPuP1enT4FHi84ubYEgdKL+cajZQtPoNeV/b6r7D42Hov0kY7ZKv7wMaGp1Hv8/huNaKddvxvR4pW7b/1uPHlFt9y3Jgteh1ZvVnAUNJBe/6sPQdtNmizQZsN2uxBtNnOfbZZPhrmX9lqaacWd3HLiybcbKd+VzTbZtv0u5/3W7/b5aua+UdeHCXU7Ryl+mi8mhvF17ARdOuxqB6fx9ewEVTTlb1aMYaNwQiKmynoiSWMM4KTjeqtLXq1NwW3hI3KdpJaQlOIrlv/A58FBHnuB7Uyh54RdL/MOhcOBMW9mNebJYwzgsu+pWOJijujJrBmPkR12Py9WkpgHYyga6z9WnvyDKON+A8GIrNj6KGbwr/XuLM2hH+XomdEMGIEI8ZXNWIQtzlfW+Zrc762zNfmfG2Zr8352jJfm/O1Zb425+v9GYw8VjDy/J9GnkP7HHn4CMPXBxN5vfMnbnk+IPANgs/lYwXfFPhc8XOG+YrB5/Yd3MjTaqwxv7FgwzGCvLFCbQFHJRB0zel8NYn1BkFecq66/Bw9I7iPz9TT2I9B0Bom39Sm49gYjaBrvl1QGWpfRtA1m78t4TWNoLisq2OvMM4Iut9ekocdEBTX/EUI44yg+xW9MuH+BCG9pQ3heYLqubhb2XmN9TSC4qbnVSyDcUbwrl9XBRwTQdA1MxM6jeMeCK7LmtpLUV2aQrT8ll+v7GdUa54Tnn0aQpyDL37P9I/jWJuPG4xqwagWjGrBqBaMal/tqDbyCe9BSq2KIgAA',
	filter_def:{
		1:{cateId:'1'},
		2:{cateId:'2'},
		3:{cateId:'3'},
		4:{cateId:'4'}
	},
	//class_parse: 'ul.nav-menu-items li:gt(0):lt(5);a&&title;a&&href;/.*/(\\d+)',
	lazy:muban.mxpro.lazy,
	推荐: '*',
	double: false, // 推荐内容是否双层定位

	// searchUrl:'/vodsearch/**----------fypage---.html',
	searchUrl:'/index.php/ajax/suggest?mid=1&wd=**&limit=50',
	detailUrl:'/voddetail/fyid.html', //非必填,二级详情拼接链接
	搜索:'json:list;name;pic;;id',

}