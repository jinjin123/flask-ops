function ewshow(){
	$.messager.show({
		id:'ewmsg',
		title:'提醒',
		width:'220px',
		height:'120px',
		msg:'<p>你有故障处理完成,你可以在处理进展里进行评价!</p>',
		timeout:0,
		showType:'slide',
		onClose:function(){
			evalwarning = 'False';
		}
	});
}

function loadjmmenu(jmmenu){
	for (var i = 0; i < jmmenu.length; i++) {
		jmaddtab(jmmenu[i][0],jmmenu[i][1]);
	}
	$('#ct-tab').tabs({
		border:false,
		fit:true
	});
}
function jmaddtab(title,url){
	$('#ct-tab').tabs('add',{
		title: title,
		content: '<iframe style="width:100%;height:100%;" scrolling="auto" frameborder="0" src=' + url + '></iframe>',
		closable:false,
		tools:[{    
			iconCls:'icon-mini-refresh',
			handler:function(){
				flashtabpage('#ct-tab',title,url)
			}
		}]
	});
}
function tabresize(){
	$('#ct-tab').tabs('resize',{
		width:$(window).width()
	});
}
$(window).resize(function(){
	setTimeout("tabresize()",100)
});