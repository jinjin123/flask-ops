function loadnavmenu(navmenu){
	$('#tt').tree({
		onClick: function(node){
			for (var i = 0; i < navmenu.length; i++) {
				if ( node.text == navmenu[i][0] )
				{
					if (!$('#ct').tabs('exists',navmenu[i][0]))
					{
						$('#ct').tabs('add',{
							title: navmenu[i][0],
							content: '<iframe style="width:100%;height:100%;" scrolling="auto" frameborder="0" src=' + navmenu[i][1] + '></iframe>',
							closable:true,
							tools:[{    
								iconCls:'icon-mini-refresh',
								handler:function(){
									for (var i = 0; i < navmenu.length; i++)
									{
										if(navmenu[i][0] == node.text)
										{
											url = navmenu[i][1];
											break;
										}
									}
									flashtabpage('#ct',node.text,url)
								}
							}]
						});
					}
					else
					{
						flashtabpage('#ct',navmenu[i][0],navmenu[i][1])
					}
				}
			}
		}
	});
	$('#ct').tabs({
		border:false,
		fit:true
	});
}
function tabresize(){
	$('#ct').tabs('resize',{
		width:$(window).width()
	});
}
$(window).resize(function(){
	setTimeout("tabresize()",100)
});
function perset(name,url){
	if (!$('#ct').tabs('exists',name))
	{
		$('#ct').tabs('add',{
			title: name,    
			content: '<iframe style="width:100%;height:100%;" scrolling="auto" frameborder="0" src=' + url + '></iframe>',
			closable:true,
			tools:[{    
				iconCls:'icon-mini-refresh',    
				handler:function(){
					flashtabpage('#ct',name,url)
				}    
			}]
		});
	}
	else
	{
		flashtabpage('#ct',name,url)
	}
}