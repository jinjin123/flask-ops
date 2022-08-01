//判断邮箱是否合法
function ismail(str){
	var reg = /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+/;
	return reg.test(str);
}
//post方法
function postdata(httpurl,postdata){
	var res = '';
	$.ajax({
	type: "post",
	url: httpurl,
	cache: false,
	data: postdata,
	async: false,
	datatype: "html",
	success:function(result){
	res = result;
	}
	});
	return res;
}

//get方法
function getdata(httpurl){
	var res = '';
	$.ajax({
	type: "get",
	url: httpurl,
	cache: false,
	async: false,
	datatype: "html",
	success:function(result){
	res = result;
	}
	});
	return res;
}

//刷新Tab页面
function flashtabpage(vid,tabtitle,url){
	$(vid).tabs('select',tabtitle);
	var tab = $(vid).tabs('getSelected');
	$(vid).tabs('update', {
		tab: tab,
		options: {
			content: '<iframe style="width:100%;height:100%;" scrolling="auto" frameborder="0" src=' + url + '></iframe>'
		}
	});
}