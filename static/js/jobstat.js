msort = '';
morder = '';
mftimef = '';
mftimet = '';
mftype = '';

function loadjobstat(url){
	$('#jobstat').datagrid({
		url: url,
		singleSelect: true,
		fitColumns: true,
		toolbar: '#jstb',
		method: 'post',
		width: 700,
		height: 'auto',
		queryParams: {
		sort: '',
		order: '',
		ftimef: '',
		ftimet: '',
		ftype: ''},
		pagination:true,
		loadMsg: '正在努力加载数据,请稍后...',
		onSortColumn: function (sort, order){
			msort = sort;
			morder = order;
		},
		columns:[[
			{field:'name',title:'姓名',width:100,sortable:'true'},
			{field:'finjobs',title:'完成事务数',width:50,sortable:'true'},
			{field:'totaltime',title:'总耗时',width:120,sortable:'true'},
			{field:'avgtime',title:'平均耗时',width:70,sortable:'true'},
			{field:'totalscore',title:'总评分',width:50,sortable:'true'},
			{field:'avgscore',title:'平均评分',width:50,sortable:'true'}
		]]
	});
}

function jobstatreload(){
	$('#jobstat').datagrid('reload');
}

function getjobstat(){
	var queryParams = $('#jobstat').datagrid('options').queryParams;
	//时间
	if ($("#ctime").is(":checked"))
	{
		queryParams.ftimef = $('#ttimefrom').datetimebox('getValue');
		queryParams.ftimet = $('#ttimeto').datetimebox('getValue');
	}
	else
	{
		queryParams.ftimef = '';
		queryParams.ftimet = '';
	}
	//类型
	if ($("#ctype").is(":checked"))
	{
		queryParams.ftype = $('#stype').combobox('getValue');
	}
	else
	{
		queryParams.ftype = '';
	}
	$('#jobstat').datagrid('options').queryParams=queryParams;
	mftimef = queryParams.ftimef;
	mftimet = queryParams.ftimet;
	mftype = queryParams.ftype;
	jobstatreload();
}

//数据导出excel
function exportexcel(url){
	var tips = "是否导出工作统计信息到Excel表格?";
	$.messager.confirm('提示',tips,function(r){
    if (r)
	{
		window.location.href=url+'?sort='+msort+'&order='+morder+'&ftimef='+mftimef+'&ftimet='+mftimet+'&ftype='+mftype;
    }
	});
}