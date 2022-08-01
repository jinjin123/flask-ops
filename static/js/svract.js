selectIndex = undefined;
saselectIndex = undefined;
serverid = undefined;
editserverid = undefined;
caneditsu = undefined;
jmlurl = '';
saurl = '';
sfurl = '';
msort = '';
morder = '';
msname = '';
mstype = '';
mscontent = '';

function loadsa(url){
	$('#svrrecord').datagrid({
		url: url,
		singleSelect: true,
		fitColumns: true,
		toolbar: '#svrrecordtb',
		method: 'post',
		queryParams: {
		sort: '',
		order: '',
		stf: '',
		stt: '',
		sname: '',
		stype: '',
		scontent: ''},
		pagination: true,
		idField:'id',
		checkOnSelect:false,
		selectOnCheck:false,
		width: 800,
		height: 'auto',
		loadMsg: '正在努力加载数据,请稍后...',
		onClickRow: onClickRow,
		onLoadSuccess: function(data){
			$('#svrrecord').datagrid('unselectAll');
			selectIndex = undefined;
		},
		onSortColumn: function (sort, order){
			msort = sort;
			morder = order;
        },
		columns:[[
			{field:'cb',checkbox:true},
			{field:'id',title:'id',width:50,sortable:'true'},
			{field:'name',title:'名称',width:120,editor:'textbox'},
			{field:'remarks',title:'备注',width:210,editor:'textbox',formatter:autonewline},
			{field:'latime',title:'最后操作时间',width:130,sortable:'true'},
			{field:'canedit',title:'允许操作的用户',width:200,formatter:formatactuser},
			{field:'actions',title:'查看操作记录',width:100,align:'center',formatter:formatseeactions}
		]]
	});
}

function svrdatareload(){
	$('#svrrecord').datagrid('reload');
}
function svractreload(){
	$('#svractdatagrid').datagrid('reload');
}
//服务器筛选
function svrsearch(){
	var queryParams = $('#svrrecord').datagrid('options').queryParams;
	//操作时间
	if ($("#acttime").is(":checked"))
	{
		queryParams.stf = $('#stacttimefrom').datetimebox('getValue');
		queryParams.stt = $('#stacttimeto').datetimebox('getValue');
	}
	else
	{
		queryParams.stf = '';
		queryParams.stt = '';
	}
	//查找方式
	if ($("#searchtype").is(":checked"))
	{
		queryParams.sname = $('#searchname').combobox('getValue');
		queryParams.stype = $('#searchmode').combobox('getValue');
		queryParams.scontent = $('#searchtext').val();
	}
	else
	{
		queryParams.sname = '';
		queryParams.stype = '';
		queryParams.scontent = '';
	}
	$('#svrrecord').datagrid('options').queryParams=queryParams;
	msname = queryParams.sname;
	mstype = queryParams.stype;
	mscontent = queryParams.scontent;
	svrdatareload();
}

//数据导出excel
function exportexcel(url){
	var tips = "是否导出当前所有页的服务器信息到Excel表格?";
	$.messager.confirm('提示',tips,function(r){
    if (r)
	{
		window.location.href=url+'?sort='+msort+'&order='+morder+'&sname='+msname+'&stype='+mstype+'&scontent='+mscontent;
    }
	});
}
function onClickRow(index){
	if ( selectIndex == undefined || selectIndex != index)
	{
		$('#svrrecord').datagrid('selectRow', index);
		selectIndex = index;
	} else if (selectIndex == index) {
		$('#svrrecord').datagrid('unselectRow', index);
		selectIndex = undefined;
	}
}
//打开添加服务器窗口
function openaddsvrwin(){
	$('#maddserver').window('open');
	$("#bsvrname").textbox('setValue','');
	$("#bremarks").textbox('setValue','');
	document.getElementById("canedituser").checked = false;
	$('#bactuser').datalist('clearChecked');
	$("#actuser").css("display","none");
	$('#bsvrname').textbox('textbox').focus();
}
function loadactuser(url){
	$('#bactuser').datalist({ 
		url: url, 
		checkbox: true, 
		lines: true,
		method: 'post',
		valueField: 'value',
		textField: 'text',
		selectOnCheck: false
	});
}
function loadcactuser(url){
	$('#cbactuser').datalist({
		url: url, 
		checkbox: true, 
		lines: true,
		method: 'post',
		valueField: 'value',
		textField: 'text',
		selectOnCheck: false,
		onLoadSuccess: setaucheckbox
	});
}
function setaucheckbox(data) {
	var rowData = data.rows;
	$.each(rowData, function (idx, val) {
		if( caneditsu.indexOf( "[" + val.value + "]" ) != -1 )
		{
			$('#cbactuser').datalist("checkRow", idx);
		}
	});
}
//添加服务器
function addsvr(posturl){
	ausn = []
	if ($("#canedituser").is(":checked"))
	{
		actusersd = $('#bactuser').datalist('getChecked');
		for (i=0;i<actusersd.length;i++)
		{
			ausn[i] = '[' + actusersd[i].text + ']';
		}
		if ( ausn.length == 0)
		{
			$.messager.alert('提示','你没有选择用户！');
			return
		}
	}
	$.messager.progress();	// 显示进度条
	$('#as').form('submit', {
		url: posturl,
		onSubmit: function(param){
			param.type = 'addserver'; 
			param.onlyusers = ausn; 
			var isValid = $(this).form('validate');
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			svrdatareload();
			$('#maddserver').window('close');
		}
	});
}
function cedituser(){
	if ($("#canedituser").is(":checked"))
	{
		$("#actuser").css("display","block");
	} else {
		$("#actuser").css("display","none");
	}
}
function ccedituser(){
	if ($("#ccanedituser").is(":checked"))
	{
		$("#cactuser").css("display","block");
	} else {
		$("#cactuser").css("display","none");
	}
}
function formatactuser(val,row){
	if (val == ''){
		return '<span style="color:red;">所有人</span>';
	} else {
		return '<span style="word-break:normal;width:auto;display:block;white-space:pre-wrap;word-wrap:break-word;overflow:hidden;color:green;">'+val+'</span>';
	}
}
//数据自动换行
function autonewline(value, rowData, rowIndex) {
	return '<span style="word-break:normal;width:auto;display:block;white-space:pre-wrap;word-wrap:break-word;overflow:hidden;">'+value+'</span>';
}
//查看操作记录
function formatseeactions(val,row){
	return '<a style="text-decoration:none" href="#" onclick=getsvracts(' + row.id + ',"' + row.name + '")>点击查看</a>'
}
//打开服务器操作记录窗口
function getsvracts(id,title){
	wintitle = '服务器操作记录 - ' + title + '(' + id + ')';
	$('#mserveractions').panel('setTitle',wintitle);
	$('#mserveractions').window('open');
	$('#cacttime').attr("checked", false);
	$('#csearchtype').attr("checked", false);
	$("#tacttimefrom").datetimebox('setValue','');
	$("#tacttimeto").datetimebox('setValue','');
	$("#sasearchname").combobox('setValue','id');
	$("#sasearchmode").combobox('setValue','0');
	$("#sasearchtext").textbox('setValue','');
	serverid = id;
	loadsvracts(saurl,id);
	sadgreset();
}

function sadgreset(){
    var pager = $('#svractdatagrid').datagrid('getPager');
    pager.pagination('refresh',{
		pageNumber:1
    });
	$('#svractdatagrid').datagrid('sort', {
		sortName: '',
		sortOrder: 'asc'
	});
}

//服务器操作筛选
function safilter(){
	var queryParams = $('#svractdatagrid').datagrid('options').queryParams;
	//操作时间
	if ($("#cacttime").is(":checked"))
	{
		queryParams.atf = $('#tacttimefrom').datetimebox('getValue');
		queryParams.att = $('#tacttimeto').datetimebox('getValue');
	}
	else
	{
		queryParams.atf = '';
		queryParams.att = '';
	}
	//查找方式
	if ($("#csearchtype").is(":checked"))
	{
		queryParams.sname = $('#sasearchname').combobox('getValue');
		queryParams.stype = $('#sasearchmode').combobox('getValue');
		queryParams.scontent = $('#sasearchtext').val();
	}
	else
	{
		queryParams.sname = '';
		queryParams.stype = '';
		queryParams.scontent = '';
	}
	$('#svractdatagrid').datagrid('options').queryParams=queryParams;
	svractreload();
}
function saonClickRow(index){
	if ( saselectIndex == undefined || saselectIndex != index)
	{
		$('#svractdatagrid').datagrid('selectRow', index);
		saselectIndex = index;
	} else if (saselectIndex == index) {
		$('#svractdatagrid').datagrid('unselectRow', index);
		saselectIndex = undefined;
	}
}
function loadsvracts(url,id){
	$('#svractdatagrid').datagrid({
		url: url,
		singleSelect: true,
		fitColumns: true,
		toolbar: '#svracttb',
		method: 'post',
		queryParams: {
		said: id,
		sort: '',
		order: '',
		atf: '',
		att: '',
		sname: '',
		stype: '',
		scontent: ''},
		pagination: true,
		width: 550,
		pageSize: 5,
		pageList: [5,10,20,30,50],
		height: 'auto',
		loadMsg: '正在努力加载数据,请稍后...',
		onClickRow: saonClickRow,
		onLoadSuccess: svractreloadtodo,
		columns:[[
			{field:'id',title:'id',width:50,sortable:'true'},
			{field:'action',title:'操作记录',width:280,formatter:autonewline},
			{field:'actman',title:'操作人',width:80,sortable:'true'},
			{field:'acttime',title:'操作时间',width:120,sortable:'true'}
		]]
	});
}
function svractreloadtodo(){
	saselectIndex = undefined;
}
//删除服务器
function delsvr(url){
	var selectitem = $('#svrrecord').datagrid('getSelected')
	var checkedRows = $('#svrrecord').datagrid('getChecked');
	var delrows = new Array();
	var crlen = checkedRows.length;
	if ( crlen == 0 )
	{
		$.messager.alert('提示','请先勾选要删除的项目!','info');
		return;
	}
	for (i=0;i<crlen;i++)
	{
		delrows[i] = checkedRows[i].id;
	}
	delrows = delrows.join(",");
	var tips = "是否删除 " + crlen + " 条项目!"
	$.messager.confirm('提示',tips,function(r){
    if (r)
	{
        result = postdata(url,{type:'delsvr',id:delrows});
		if (result == 'True')
		{
			parent.flashtabpage('#ct','服务器操作记录',sfurl);
		} else {
			$.messager.alert('出错','项目删除失败!','error');
		}
    }
	});
}
//删除服务器操作
function delsvract(url){
	var selectitem = $('#svractdatagrid').datagrid('getSelected')
	var tips = "是否删除操作记录 id:" + selectitem.id + " !"
	$.messager.confirm('提示',tips,function(r){    
    if (r)
	{
        result = postdata(url,{type:'delsvract',id:selectitem.id});
		if (result == 'True')
		{
			svractreload();
		}
    }    
	});
}
//打开添加服务器操作记录窗口
function openaddsvractwin(){
	$('#maddserveraction').window('open');
	$("#bsvraction").textbox('setValue','');
	$('#bsvraction').textbox('textbox').focus();
}
//添加服务器操作记录
function addsvract(url){
	$.messager.progress();	// 显示进度条
	$('#asa').form('submit', {
		url: url,
		onSubmit: function(param){
			param.type = 'addsvract'; 
			param.serverid = serverid; 
			var isValid = $(this).form('validate');
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			svractreload();
			svrdatareload();
			$('#maddserveraction').window('close');
		}
	});
}
//打开修改服务器信息窗口
function openeditsvr(){
	if (selectIndex != undefined)
	{
		var rows = $("#svrrecord").datagrid("getRows");
		wintitle = '修改服务器信息 - ID:' + rows[selectIndex].id;
		$('#mchangesvrmsg').panel('setTitle',wintitle);
		editserverid = rows[selectIndex].id;
		$('#mchangesvrmsg').window('open');
		$("#cbsvrname").textbox('setValue',rows[selectIndex].name);
		$("#cbremarks").textbox('setValue',rows[selectIndex].remarks);
		if (rows[selectIndex].canedit == '')
		{
			document.getElementById("ccanedituser").checked = false;
			$('#cbactuser').datalist('clearChecked');
			$("#cactuser").css("display","none");
		} else {
			document.getElementById("ccanedituser").checked = true;
			caneditsu = rows[selectIndex].canedit;
			loadcactuser(jmlurl);
			$("#cactuser").css("display","block");
		}
		$('#cbsvrname').textbox('textbox').focus();
	}
}
//修改服务器信息
function changesvrmsg(url){
	ausn = []
	if ($("#ccanedituser").is(":checked"))
	{
		actusersd = $('#cbactuser').datalist('getChecked');
		for (i=0;i<actusersd.length;i++)
		{
			ausn[i] = '[' + actusersd[i].text + ']';
		}
		if ( ausn.length == 0)
		{
			$.messager.alert('提示','你没有选择用户！');
			return
		}
	}
	$.messager.progress();	// 显示进度条
	$('#csm').form('submit', {
		url: url,
		onSubmit: function(param){
			param.type = 'changesvr';
			param.id = editserverid;
			param.onlyusers = ausn; 
			var isValid = $(this).form('validate');
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			selectIndex = undefined;
			svrdatareload();
			$('#mchangesvrmsg').window('close');
		}
	});
}