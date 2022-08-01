editIndex = undefined;
selectIndex = undefined;
fjid = undefined;
jeid = undefined;
ajcid = undefined;
cjmid = undefined;
jdurl = '';
jmurl = '';
jfurl = '';
iID = '';
jstatus = [{ "value": "0", "text": "未接手" },{ "value": "1", "text": "处理中" }, { "value": "2", "text": "已处理" }];
jtype = [{ "value": "0", "text": "故障" }, { "value": "1", "text": "维护" },{ "value": "2", "text": "部署" }];

function changeflashtime(){
	$('#flashdelay').combobox({  
		onChange:function(n,m){
			clearInterval(iID);
			if ( n != '0' )
			{
				iID = setInterval("$('#ywjobinfo').datagrid('reload')",n);
			}
		}
	});
}

function endEditing(){
	if (editIndex == undefined){return true}
	if ($('#ywjobinfo').datagrid('validateRow', editIndex)){
		$('#ywjobinfo').datagrid('endEdit', editIndex);
		editIndex = undefined;
		return true;
	} else {
		return false;
	}
}
function jobreload(){
	$('#ywjobinfo').datagrid('reload');
}
function jobdetailreload(){
	$('#jobdetaildatagrid').datagrid('reload');
}
function onClickRow(index){
	if ( selectIndex == undefined || selectIndex != index)
	{
		$('#ywjobinfo').datagrid('selectRow', index);
		selectIndex = index;
	} else if (selectIndex == index) {
		$('#ywjobinfo').datagrid('unselectRow', index);
		selectIndex = undefined;
	}
}

//格式化状态
function formatstatus(value, rowData, rowIndex) {
	for (var i = 0; i < jstatus.length; i++) {
		if (jstatus[i].value == value) {
			if (value == '0'){
				return '<span style="color:gray;">'+jstatus[i].text+'</span>';
			} else if (value == '1'){
				return '<span style="color:red;">'+jstatus[i].text+'</span>';
			}
			else {
				return '<span style="color:green;">'+jstatus[i].text+'</span>';
			}
		}
	}
}

//格式化类型
function formattype(value, rowData, rowIndex) {
	for (var i = 0; i < jtype.length; i++) {
		if (jtype[i].value == value) {
			if (value == '0'){
				return '<span style="color:red;">'+jtype[i].text+'</span>';
			} else if (value == '1'){
				return '<span style="color:green;">'+jtype[i].text+'</span>';
			} else {
				return '<span style="color:blue;">'+jtype[i].text+'</span>';
			}
		}
	}
}

//数据自动换行
function autonewline(value, rowData, rowIndex) {
	return '<span style="word-break:normal;width:auto;display:block;white-space:pre-wrap;word-wrap:break-word;overflow:hidden;">'+value+'</span>';
}

//score格式化
function formatscore(value, rowData, rowIndex) {
	switch(value)
	{
		case '1':
			value = '☆';
			break;
		case '2':
			value = '☆☆';
			break;
		case '3':
			value = '☆☆☆';
			break;
		case '4':
			value = '☆☆☆☆';
			break;
		case '5':
			value = '☆☆☆☆☆';
			break;
	}
	return '<span style="display:block;overflow:hidden;">'+value+'</span>';
}

//添加事务窗口初始化
function openaddjob(){
	$('#maddjob').window('open')
	$("#bjobname").textbox('setValue','');
	$("#bjobcontent").textbox('setValue','');
	$("#bjobtype").combobox('setValue','0');
	$('#bjobname').textbox('textbox').focus();
}

//添加事务
function addjob(posturl){
	$.messager.progress();	// 显示进度条
	$('#aj').form('submit', {
		url: posturl,
		onSubmit: function(param){
			param.type = 'addjob';
			var isValid = $(this).form('validate');
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(data){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			jobreload();
			$('#maddjob').window('close');
			return data;
		}
	});
}

//删除事务
function deljob(url){
	var checkedRows = $('#ywjobinfo').datagrid('getChecked');
	var delrows = new Array();
	var crlen = checkedRows.length;
	if ( crlen == 0 )
	{
		$.messager.alert('提示','请先勾选要删除的事务!','info');
		return;
	}
	for (i=0;i<crlen;i++)
	{
		delrows[i] = checkedRows[i].jobid;
	}
	delrows = delrows.join(",");
	var tips = "是否删除 " + crlen + " 项事务!"
	$.messager.confirm('提示',tips,function(r){    
    if (r)
	{
        result = postdata(url,{type:'deljob',jobid:delrows});
		if (result == 'True')
		{
			parent.flashtabpage('#ct','工作事项',jfurl);
		} else {
			$.messager.alert('出错','事务删除失败!','error');
		}
    }
	});
}

//接手事务
function getjob(url,jobid){
	var tips = "是否接手事务 id:" + jobid + " !"
	$.messager.confirm('提示',tips,function(r){    
    if (r)
	{
        result = postdata(url,{type:'getjob',jobid:jobid});
		if (result == 'True')
		{
			jobreload();
			jobdetailreload();
		}
    }
	});
}

//打开事务评价窗口
function jobevaluatewin(jobid){
	jeid = jobid;
	$('#mjobevaluate').window('open');
	$("#sjobscore").combobox('setValue','3');
	$('#bjobcomment').textbox('setValue','');
	$('#bjobcomment').textbox('textbox').focus();
}

//事务评价
function jobevaluate(url){
	jobid = jeid;
	$.messager.progress();	// 显示进度条
	$('#jobevaluate').form('submit', {
		url: url,
		onSubmit: function(param){
			param.type = 'jobevaluate';
			param.jobid = jobid;
			var isValid = $(this).form('validate');
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			jobdetailreload();
			$('#mjobevaluate').window('close');
		}
	});
}

//事务返工
function jobrework(url,jobid){
	var tips = "是否要求事务返工 id:" + jobid + " !"
	$.messager.confirm('提示',tips,function(r){    
    if (r)
	{
        result = postdata(url,{type:'jobrework',jobid:jobid});
		if (result == 'True')
		{
			jobreload();
			jobdetailreload();
		}
    }
	});
}

//打开完成事务窗口
function finishjobwin(jobid){
	var tips = "是否结束事务 id:" + jobid + " !"
	$.messager.confirm('提示',tips,function(r){    
    if (r)
	{
		fjid = jobid;
		$('#mfinishjob').window('open');
		$("#bjobtec").textbox('setValue','');
		$('#bjobtec').textbox('textbox').focus();
    }
	});
}

//完成事务
function finishjob(url){
	jobid = fjid;
	$.messager.progress();	// 显示进度条
	$('#ej').form('submit', {
		url: url,
		onSubmit: function(param){
			param.type = 'finishjob';
			param.jobid = jobid;
			var isValid = $(this).form('validate');
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			jobreload();
			jobdetailreload();
			$('#mfinishjob').window('close');
		}
	});
}

//打开添加事务过程窗口
function addjobcoursewin(jobid){
	ajcid = jobid;
	$('#maddjobcourse').window('open');
	$("#bjobcourse").textbox('setValue','');
	$('#bjobcourse').textbox('textbox').focus();
}

//添加事务过程
function addjobcourse(url){
	jobid = ajcid;
	$.messager.progress();	// 显示进度条
	$('#jcourse').form('submit', {
		url: url,
		onSubmit: function(param){
			param.type = 'addjobcourse';
			param.jobid = jobid;
			var isValid = $(this).form('validate');
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			jobdetailreload();
			$('#maddjobcourse').window('close');
		}
	});
}

//打开转接处理人窗口
function opencjmwin(jobid){
	cjmid = jobid;
	$('#mchangejobman').window('open');
	cjmsetvalue1();
}

//转接处理人
function changejobman(url){
	jobid = cjmid;
	$.messager.progress();	// 显示进度条
	$('#changejobman').form('submit', {
		url: url,
		onSubmit: function(param){
			param.type = 'changejobman';
			param.jobid = jobid;
			var isValid = $(this).form('validate');
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			jobreload();
			jobdetailreload();
			$('#mchangejobman').window('close');
		}
	});
}

//数据筛选
function jobfilter(){
	var queryParams = $('#ywjobinfo').datagrid('options').queryParams;
	//开始时间
	if ($("#cbegintime").is(":checked"))
	{
		queryParams.fbegintimef = $('#tbegintimefrom').datetimebox('getValue');
		queryParams.fbegintimet = $('#tbegintimeto').datetimebox('getValue');
	}
	else
	{
		queryParams.fbegintimef = '';
		queryParams.fbegintimet = '';
	}
	//结束时间
	if ($("#cendtime").is(":checked"))
	{
		queryParams.fendtimef = $('#tendtimefrom').datetimebox('getValue');
		queryParams.fendtimet = $('#tendtimeto').datetimebox('getValue');
	}
	else
	{
		queryParams.fendtimef = '';
		queryParams.fendtimet = '';
	}
	//状态
	if ($("#cstatus").is(":checked"))
	{
		queryParams.fstatus = $('#sstatus').combobox('getValue');
	}
	else
	{
		queryParams.fstatus = '';
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
	//其它
	if ($("#cother").is(":checked"))
	{
		queryParams.fotname = $('#sother').combobox('getValue');
		queryParams.fotstype = $('#ssearchmode').combobox('getValue');
		queryParams.fotscontent = $('#tsearchtext').val();
	}
	else
	{
		queryParams.fotname = '';
		queryParams.fotstype = '';
		queryParams.fotscontent = '';
	}
	$('#ywjobinfo').datagrid('options').queryParams=queryParams;
	jobreload();
}

//cjm默认选中首项
function cjmsetvalue1(){
	var data = $('#bcjm').combobox("getData");
	if (data)
	{
		 $('#bcjm').combobox('setValue',data[0].text);
	}
 }
//查看详细
function formatshowdetail(val,row){
	return '<a style="text-decoration:none" href="#" onclick=showdetail(' + row.jobid + ')>点击查看</a>'
}
//打开详细窗口
function showdetail(id){
	wintitle = '事务详情 - ' + id;
	$('#mjobdetail').panel('setTitle',wintitle);
	$('#mjobdetail').window('open');
	loadjobdetail(jdurl,jmurl,id);
}
function loadjobdetail(jdurl,posturl,id){
	 $('#jobdetaildatagrid').datagrid({
		url:jdurl+'?id='+(id),
		singleSelect: true,
		fitColumns: true,
		height:'auto', 
		method: 'post',
		loadMsg: '正在努力加载数据,请稍后...',
		columns:[[
			{field:'jobcontent',title:'事务内容',width:'250px',styler:function(value,row,index){return 'vertical-align:top;';},editor:'textbox',multiline:true,formatter:autonewline},
			{field:'jobcourse',title:'处理过程',width:'200px',styler:function(value,row,index){return 'vertical-align:top;';},editor:'textbox',multiline:true,formatter:autonewline},
			{field:'jobtec',title:'处理方法',width:'150px',styler:function(value,row,index){return 'vertical-align:top;';},editor:'textbox',multiline:true,formatter:autonewline},
			{field:'jobscore',title:'事务评分',width:'70px',styler:function(value,row,index){return 'vertical-align:top;';},editor:'textbox',multiline:true,formatter:formatscore},
			{field:'jobcomment',title:'事务评语',width:'100px',styler:function(value,row,index){return 'vertical-align:top;';},editor:'textbox',multiline:true,formatter:autonewline}
		]],
		toolbar: [{
			text:'添加事务过程',
			id:'ywjobinfo-ajc',
			handler: function(){addjobcoursewin(id)}
		},'-',{
			text:'接手事务',
			id:'ywjobinfo-gj',
			handler: function(){getjob(posturl,id)}
		},'-',{
			text:'转接事务',
			id:'ywjobinfo-cjm',
			handler: function(){opencjmwin(id)}
		},'-',{
			text:'结束事务',
			id:'ywjobinfo-ej',
			handler: function(){finishjobwin(id)}
		},'-',{
			text:'事务评价',
			id:'ywjobinfo-je',
			handler: function(){jobevaluatewin(id)}
		},'-',{
			text:'事务返工',
			id:'ywjobinfo-jr',
			handler: function(){jobrework(posturl,id)}
		}],
		onLoadSuccess:function(){
			//初始化
			jobman = postdata(posturl,{type:'getjobman',jobid:id});
			chkjobman = postdata(posturl,{type:'chkjobman',jobid:id});
			iscreateman = postdata(posturl,{type:'isjobcreateman',jobid:id});
			jobstatus = postdata(posturl,{type:'getjobstatus',jobid:id});
			ftover1day = postdata(posturl,{type:'ftover1day',jobid:id});
			role = postdata(posturl,{type:'getrole'});
			if (chkjobman == 'False' || jobstatus == '2')
			{
				$('#ywjobinfo-ajc').linkbutton('disable');
				$('#ywjobinfo-cjm').linkbutton('disable');
				$('#ywjobinfo-ej').linkbutton('disable');
			} else {
				$('#ywjobinfo-ajc').linkbutton('enable');
				$('#ywjobinfo-cjm').linkbutton('enable');
				$('#ywjobinfo-ej').linkbutton('enable');			
			}
			if (jobman != '' || parseInt(role) >= 2 || jobstatus == '2')
			{
				$('#ywjobinfo-gj').linkbutton('disable');
			} else {
				$('#ywjobinfo-gj').linkbutton('enable');
			}
			if (iscreateman == 'False' || jobstatus != '2' || (jobstatus == '2' && ftover1day == 'True'))
			{
				$('#ywjobinfo-je').linkbutton('disable');
				$('#ywjobinfo-jr').linkbutton('disable');
			} else {
				$('#ywjobinfo-je').linkbutton('enable');
				$('#ywjobinfo-jr').linkbutton('enable');
			}
		}
	 });
}
//加载数据
function loadjd(url){
	$('#ywjobinfo').datagrid({
		url:url,
		singleSelect: true,
		fitColumns: true,
		toolbar: '#jobtb',
		method: 'post',
		queryParams: {
		sort: '',
		order: '',
		fbegintimef: '',
		fbegintimet: '',
		fendtimef: '',
		fendtimet: '',
		fstatus: '',
		ftype: '',
		fotname: '',
		fotstype: '',
		fotscontent: ''},
        pagination:true,
		idField:'jobid',
		checkOnSelect:false,
		selectOnCheck:false,
		width:930,
		height:500,
		loadMsg: '正在努力加载数据,请稍后...',
		onClickRow: onClickRow,
		onLoadSuccess: function(data){
			editIndex = undefined;
			selectIndex = undefined;
			role = postdata(jmurl,{type:'getrole'});
			for(var i=0;i<data.rows.length;i++){
				iscreateman = postdata(jmurl,{type:'isjobcreateman',jobid:data.rows[i].jobid});
				if ((role != '0') && ((iscreateman != 'True') || !((iscreateman == 'True') && (data.rows[i].jobstatus == '0'))))
				{
					$("input[type='checkbox'][name='jobcb']")[i].disabled = true;
				}
			}
		},
		onCheckAll: function(data){
			role = postdata(jmurl,{type:'getrole'});
			for(var i=0;i<data.length;i++){
				iscreateman = postdata(jmurl,{type:'isjobcreateman',jobid:data[i].jobid});
				if ((role != '0') && ((iscreateman != 'True') || !((iscreateman == 'True') && (data[i].jobstatus == '0'))))
				{
					$("#ywjobinfo").datagrid("uncheckRow", i);
				}
			}
		},
		columns:[[
			{field:'jobcb',checkbox:true},
			{field:'jobid',title:'事务id',width:50,sortable:'true'},
			{field:'jobstatus',title:'状态',width:50,sortable:'true',formatter:formatstatus},
			{field:'jobcman',title:'发布人',width:80,editor:'textbox'},
			{field:'jobman',title:'处理人',width:80,editor:'textbox'},
			{field:'jobut',title:'耗时',width:120,editor:'textbox'},
			{field:'jobtype',title:'事务类型',width:70,sortable:'true',formatter:formattype},
			{field:'jobtitle',title:'事务名称',width:150,editor:'textbox'},
			{field:'jobbt',title:'开始时间',width:130,sortable:'true',editor:'textbox'},
			{field:'jobet',title:'结束时间',width:130,sortable:'true',editor:'textbox'},
			{field:'actions',title:'查看详细',width:100,align:'center',formatter:formatshowdetail}
		]]
	});
}