jeid = undefined;
jmmdfurl = '';
jdurl = '';
jmurl = '';
iID = '';
jstatus = [{ "value": "0", "text": "未接手" },{ "value": "1", "text": "处理中" }, { "value": "2", "text": "已处理" }];

function init(){
	//清理过期事务
	postdata(jmmdfurl,{type:'cleanjmp'});
	chkvaluate();
	$('#flashdelay').combobox({  
		onChange:function(n,m){
			clearInterval(iID);
			if ( n != '0' )
			{
				iID = setInterval("$('#jmpinfo').datagrid('reload');chkvaluate();",n);
			}
		}
	});
	$('#sstatus').combobox({    
		onSelect: function(res){    
			var queryParams = $('#jmpinfo').datagrid('options').queryParams;
			queryParams.fstatus = res.value;
			$('#jmpinfo').datagrid('options').queryParams=queryParams;
			jmpreload();
		}
	});
}

//检查可评价事务
function chkvaluate(){
	result = postdata(jmmdfurl,{type:'canevaluate'});
	if ( result == 'True') {
		if ( parent.evalwarning != 'True' ){
			parent.evalwarning = 'True';
			parent.ewshow();
		}
	} else {
		parent.$('#ewmsg').window('close');
	}
}

function loadjmp(url){
	$('#jmpinfo').datagrid({
		url:url,
		singleSelect: true,
		fitColumns: true,
		toolbar: '#jmptb',
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
		width:930,
		height:500,
		loadMsg: '正在努力加载数据,请稍后...',
		columns:[[
			{field:'jobid',title:'事务id',width:50,sortable:'true',hidden:'true'},
			{field:'jobstatus',title:'状态',width:50,sortable:'true',formatter:formatstatus},
			{field:'jobman',title:'处理人',width:80,editor:'textbox'},
			{field:'jobut',title:'耗时',width:120,editor:'textbox'},
			{field:'jobtitle',title:'事务名称',width:150,editor:'textbox'},
			{field:'jobbt',title:'开始时间',width:130,sortable:'true',editor:'textbox'},
			{field:'jobet',title:'结束时间',width:130,sortable:'true',editor:'textbox'},
			{field:'actions',title:'查看详细',width:100,align:'center',formatter:formatshowdetail}
		]]
	});
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

//查看详细
function formatshowdetail(val,row){
	return '<a style="text-decoration:none" href="#" onclick=showdetail(' + row.jobid + ')>点击查看</a>'
}
//打开详细窗口
function showdetail(id){
	wintitle = '事务详情';
	$('#mjmpdetail').panel('setTitle',wintitle);
	$('#mjmpdetail').window('open');
	loadjmpdetail(jdurl,jmurl,id);
}
function loadjmpdetail(jdurl,posturl,id){
	 $('#jmpdetaildatagrid').datagrid({
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
			text:'事务评价',
			id:'jmpinfo-je',
			handler: function(){jobevaluatewin(id)}
		},'-',{
			text:'事务返工',
			id:'jmpinfo-jr',
			handler: function(){jobrework(posturl,id)}
		}],
		onLoadSuccess:function(){
			jobstatus = postdata(posturl,{type:'getjobstatus',jobid:id});
			if ( jobstatus != '2' )
			{
				$('#jmpinfo-je').linkbutton('disable');
				$('#jmpinfo-jr').linkbutton('disable');
			} else {
				$('#jmpinfo-je').linkbutton('enable');
				$('#jmpinfo-jr').linkbutton('enable');
			}
		}
	 });
}

function jmpreload(){
	$('#jmpinfo').datagrid('reload');
}
function jmpdetailreload(){
	$('#jmpdetaildatagrid').datagrid('reload');
}

//打开事务评价窗口
function jobevaluatewin(jobid){
	jeid = jobid;
	$('#mjmpevaluate').window('open');
	$("#sjmpscore").combobox('setValue','3');
	$('#bjmpcomment').textbox('setValue','');
	$('#bjmpcomment').textbox('textbox').focus();
}

//事务评价
function jmpevaluate(url){
	jobid = jeid;
	$.messager.progress();	// 显示进度条
	$('#jmpevaluate').form('submit', {
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
			//jmpdetailreload();
			jmpreload();
			$('#mjmpevaluate').window('close');
			$('#mjmpdetail').window('close');
			chkvaluate();
		}
	});
}

//事务返工
function jobrework(url,jobid){
	var tips = "是否要求事务返工!";
	$.messager.confirm('提示',tips,function(r){    
    if (r)
	{
        result = postdata(url,{type:'jobrework',jobid:jobid});
		if (result == 'True')
		{
			jmpreload();
			//jmpdetailreload();
			$('#mjmpdetail').window('close');
			chkvaluate();
		}
    }
	});
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