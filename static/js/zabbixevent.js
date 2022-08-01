jobmdfurl = '';
zabbixmdfurl = '';
zjmdfurl = '';
iID = '';

function loadze(url){
	$('#zabbixevent').datagrid({
		url: url,
		singleSelect: true,
		fitColumns: true,
		toolbar: '#zetb',
		method: 'post',
		queryParams: {
		sort: '',
		order: '',
		fhappentimef: '',
		fhappentimet: '',
		fotname: '',
		fottype: '',
		fotcontent: '',
		showfinish: 'false'},
		pagination:true,
		width: 800,
		height: 'auto',
		onDblClickRow: onDblClickRow,
		loadMsg: '正在努力加载数据,请稍后...',
		columns:[[
			{field:'did',title:'事件id',width:60,sortable:'true'},
			{field:'hostname',title:'主机名称',width:100,sortable:'true'},
			{field:'description',title:'事件描述',width:170,sortable:'true'},
			{field:'time',title:'发生时间',width:80,sortable:'true'},
			{field:'status',title:'状态',width:50,align:'center',sortable:'true',formatter:formatstatus},
			{field:'ignore',title:'忽略事件',width:50,align:'center',formatter:formatignore}
		]]
	});
}

//切换显示模式
function displaymode(){
	var queryParams = $('#zabbixevent').datagrid('options').queryParams;
	if ($("#showmode").is(":checked"))
	{
		queryParams.showfinish = 'true';
	} else {
		queryParams.showfinish = 'false';
	}
	$('#zabbixevent').datagrid('options').queryParams=queryParams;
	$('#zabbixevent').datagrid('reload');
}

//忽略按钮
function formatignore(val,row){
	if ( row.status != '0' )
	{
		return '';
	} else {
		return '<a style="text-decoration:none" href="#" onclick=ignoreevent(' + row.did + ')>忽略</a>';
	}
}

//忽略事件
function ignoreevent(id){
	var tips = "是否忽略zabbix事件 id:" + id
	$.messager.confirm('忽略事件',tips,function(r){
	if (r)
	{
		postdata(zabbixmdfurl,{type:'ignoreevent',id:id});
		$('#zabbixevent').datagrid('reload');
	}
	});
}

//状态格式化
function formatstatus(val,row){
	if ( val == '0' )
	{
		return '<span style="color:gray;">未处理</span>';
	} else if ( val == '1' ) {
		return '<span style="color:red;">处理中</span>';
	} else {
		return '<span style="color:green;">已结束</span>';
	}
}

//打开清除已结束事件窗口
function opendelzfe(){
	$('#mdelzfe').window('open');
	$("#rng").combobox('setValue','0');
	$("#zfetime").datetimebox('setValue','');
}

//清除已结束事件
function delzfe(url){
	role = postdata(url,{type:'getrole'});
	if (role != '0')
	{
		$.messager.alert('提示','只有管理员才能执行该操作！');
		return;
	}
	rng = $('#rng').combobox('getValue');
	zfetime = $('#zfetime').datetimebox('getValue');
	if (rng == '1' && zfetime == '')
	{
		$.messager.alert('提示','你没有选择时间！');
		return;
	}
	$.messager.progress();	// 显示进度条
	$('#delzfe').form('submit', {
		url: url,
		onSubmit: function(param){
			param.type = 'delzfe';
			var isValid = $(this).form('validate');
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			$('#zabbixevent').datagrid('reload');
			$('#mdelzfe').window('close');
		}
	});
}

//数据筛选
function zfefilter(){
	var queryParams = $('#zabbixevent').datagrid('options').queryParams;
	//发生时间
	if ($("#chappentime").is(":checked"))
	{
		queryParams.fhappentimef = $('#thappentimefrom').datetimebox('getValue');
		queryParams.fhappentimet = $('#thappentimeto').datetimebox('getValue');
	}
	else
	{
		queryParams.fhappentimef = '';
		queryParams.fhappentimet = '';
	}
	//其它
	if ($("#cother").is(":checked"))
	{
		queryParams.fotname = $('#sother').combobox('getValue');
		queryParams.fottype = $('#ssearchmode').combobox('getValue');
		queryParams.fotcontent = $('#tsearchtext').val();
	}
	else
	{
		queryParams.fotname = '';
		queryParams.fottype = '';
		queryParams.fotcontent = '';
	}
	$('#zabbixevent').datagrid('options').queryParams=queryParams;
	$('#zabbixevent').datagrid('reload');
}

function changeflashtime(){
	$('#flashdelay').combobox({  
		onChange:function(n,m){
			clearInterval(iID);
			if ( n != '0' )
			{
				iID = setInterval("$('#zabbixevent').datagrid('reload')",n);
			}
		}
	});
}

function onDblClickRow(index){
	var selectitem = $('#zabbixevent').datagrid('getSelected')
	if ( selectitem.status != '0' )
	{
		return;
	}
	var tips = "ID:" + selectitem.did + " " + selectitem.hostname + ':' + selectitem.description + " 发生于:" + selectitem.time
	$.messager.confirm('添加事务',tips,function(r){
    if (r)
	{
		jobid = postdata(jobmdfurl,{type:'addjob',jobname:'zabbix报警事件',jobcontent:tips,jobtype:'0'});
		postdata(jobmdfurl,{type:'getjob',jobid:jobid});
		postdata(zabbixmdfurl,{type:'setstatusdoing',id:selectitem.did});
		postdata(zjmdfurl,{type:'add',jid:jobid,zeid:selectitem.did});
		$('#zabbixevent').datagrid('reload');
    }    
	});
}