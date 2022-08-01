jswdurl = '/noteform/';
nfurl = '';
nmurl = '';

function loadnote(url){
	$('#note').datagrid({
		url: url,
		singleSelect: true,
		fitColumns: true,
		toolbar: '#ntb',
		method: 'post',
		width: 700,
		height: 'auto',
		onDblClickRow: onDblClickRow,
		queryParams: {
		sort: '',
		order: '',
		sname:'',
		smode:'',
		stext:''},
		pagination:true,
		idField:'id',
		checkOnSelect:false,
		selectOnCheck:false,
		loadMsg: '正在努力加载数据,请稍后...',
		onLoadSuccess: function(data){
			role = postdata(nmurl,{type:'getrole'});
			for(var i=0;i<data.rows.length;i++){
				iscreateman = postdata(nmurl,{type:'iscreator',id:data.rows[i].id});
				if ((role != '0') && (iscreateman != 'True'))
				{
					$("input[type='checkbox'][name='cb']")[i].disabled = true;
				}
			}
		},
		onCheckAll: function(data){
			role = postdata(nmurl,{type:'getrole'});
			for(var i=0;i<data.length;i++){
				iscreateman = postdata(nmurl,{type:'iscreator',id:data[i].id});
				if ((role != '0') && (iscreateman != 'True'))
				{
					$("#note").datagrid("uncheckRow", i);
				}
			}
		},
		columns:[[
			{field:'cb',checkbox:true},
			{field:'id',title:'id',width:60,sortable:'true'},
			{field:'title',title:'标题',width:500,multiline:true,formatter:autonewline},
			{field:'creator',title:'创建者',width:140,sortable:'true'},
			{field:'content',title:'内容',width:140,hidden:'true'}
		]]
	});
}

//删除文档
function delnote(url){
	var selectitem = $('#note').datagrid('getSelected')
	var selectindex = $('#note').datagrid('getRowIndex',selectitem)
	var checkedRows = $('#note').datagrid('getChecked');
	var delrows = new Array();
	var crlen = checkedRows.length;
	if ( crlen == 0 )
	{
		$.messager.alert('提示','请先勾选要删除的文档!','info');
		return;
	}
	for (i=0;i<crlen;i++)
	{
		delrows[i] = checkedRows[i].id;
	}
	delrows = delrows.join(",");
	var tips = "是否删除 " + crlen + " 篇文档!"
	$.messager.confirm('提示',tips,function(r){
    if (r)
	{
        result = postdata(url,{type:'delnote',id:delrows});
		if (result == 'True')
		{
			parent.flashtabpage('#ct','技术文档',nfurl);
		} else {
			$.messager.alert('出错','文档删除失败!','error');
		}
    }    
	});
}

//修改文档
function mdfnote(url){
	$.messager.progress();	// 显示进度条
	$('#mn').form('submit', {
		url: url,
		onSubmit: function(param){
			param.type = 'mdfnote'; 
			param.id = parent.mdfnoteid;
			var isValid = $(this).form('validate');
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			$('#mmdfnote').window('close');
			parent.$("#ct").tabs('select',"技术文档");
			var tab = parent.$("#ct").tabs('getSelected');
			parent.$("#ct").tabs('update', {
				tab: tab,
				options: {
					content: '<iframe style="width:100%;height:100%;" scrolling="auto" frameborder="0" src=' + jswdurl + '></iframe>'
				}
			});
			parent.$('#ct').tabs('close','修改文档');
		}
	});
}

//新建文档
function addnote(url){
	$.messager.progress();	// 显示进度条
	$('#an').form('submit', {
		url: url,
		onSubmit: function(param){
			param.type = 'addnote'; 
			var isValid = $(this).form('validate');
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			$('#maddnote').window('close');
			parent.$("#ct").tabs('select',"技术文档");
			var tab = parent.$("#ct").tabs('getSelected');
			parent.$("#ct").tabs('update', {
				tab: tab,
				options: {
					content: '<iframe style="width:100%;height:100%;" scrolling="auto" frameborder="0" src=' + jswdurl + '></iframe>'
				}
			});
			parent.$('#ct').tabs('close','新建文档');
		}
	});
}

//打开文档窗口
function onDblClickRow(){
	var selectitem = $('#note').datagrid('getSelected')
	title = selectitem.title
	if (title.length <= 8){
		title = '文档 - ' + title
	} else {
		title = '文档 - ' + title.substr(0,8) + '~'
	}
	parent.$('#ct').tabs('add',{
		title: title,
		content: '<h1 style="text-align:center">' + selectitem.title + '</h1>' + selectitem.content,
		closable:true
	});
}

//开开新建文档窗口
function openaddnote(url){
	if (!parent.$('#ct').tabs('exists','新建文档'))
	{
		parent.$('#ct').tabs('add',{
			title: '新建文档',
			content: '<iframe style="width:100%;height:100%;" scrolling="auto" frameborder="0" src=' + url + '></iframe>',
			closable:true
		});
	} else {
		parent.$('#ct').tabs('select','新建文档');
	}
}

//打开修改文档窗口
function openmdfnote(chkurl,formurl){
	var selectitem = $('#note').datagrid('getSelected')
	role = postdata(chkurl,{type:'getrole'});
	iscreator = postdata(chkurl,{type:'iscreator',id:selectitem.id});
	if ((role != '0') && (iscreator != 'True'))
	{
		$.messager.alert('提示','你不能修改该文档！');
		return;	
	}
	if (!parent.$('#ct').tabs('exists','修改文档'))
	{
		var selectIndex = $('#note').datagrid('getRowIndex',selectitem)
		var rows = $("#note").datagrid("getRows");
		parent.mdfnoteid = rows[selectIndex].id;
		parent.mdfnotetitle = rows[selectIndex].title;
		parent.mdfnotecontent = rows[selectIndex].content;
		parent.$('#ct').tabs('add',{
			title: '修改文档',
			content: '<iframe style="width:100%;height:100%;" scrolling="auto" frameborder="0" src=' + formurl + '></iframe>',
			closable:true
		});
	}
}

function notereload(){
	$('#note').datagrid('reload');
}

//数据查找
function notesearch(){
	var queryParams = $('#note').datagrid('options').queryParams;
	queryParams.sname = $('#searchname').combobox('getValue');
	queryParams.smode = $('#searchmode').combobox('getValue');
	queryParams.stext = $('#searchtext').val();
	$('#note').datagrid('options').queryParams=queryParams;
	notereload();
}
	
//数据自动换行
function autonewline(value, rowData, rowIndex) {
	return '<span style="word-break:normal;width:auto;display:block;white-space:pre-wrap;word-wrap:break-word;overflow:hidden;">'+value+'</span>';
}