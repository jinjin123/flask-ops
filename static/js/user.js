editIndex = undefined;
selectIndex = undefined;
ufurl = '';
roletext = [{ "value": "0", "text": "管理员" }, { "value": "1", "text": "运维人员" }, { "value": "2", "text": "普通用户" }];

function loadud(url){
	$('#ywuserinfo').datagrid({
		url: url,
		title: '用户信息编辑',
		singleSelect: true,
		fitColumns: true,
		toolbar: '#usrlitb',
		method: 'post',
		queryParams: {
		sort: '',
		order: '',
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
			editIndex = undefined;
			selectIndex = undefined;
		},
		columns:[[
			{field:'cb',checkbox:true},
			{field:'id',title:'id',width:30,sortable:'true'},
			{field:'nickname',title:'用户名',width:80},
			{field:'password',title:'密码',width:250,editor:'textbox'},
			{field:'role',title:'权限',width:80,sortable:'true',editor:{type:'combobox',options:{data:roletext,valueField:"value",textField:"text",editable:false}},formatter:formatrole},
			{field:'email',title:'邮箱',width:150,editor:'textbox'},
			{field:'lastlogin',title:'最后登陆时间',width:200,sortable:'true',formatter:formatlogin}
		]]
	});
}
function userreload(){
	$('#ywuserinfo').datagrid('reload');
}
function namesearch(){
	var queryParams = $('#ywuserinfo').datagrid('options').queryParams;
	queryParams.sname = $('#searchname').combobox('getValue');
	queryParams.stype = $('#searchmode').combobox('getValue');
	queryParams.scontent = $('#searchtext').val();
	$('#ywuserinfo').datagrid('options').queryParams=queryParams;
	userreload();
}
function endEditing(){
	if (editIndex == undefined){return true}
	if ($('#ywuserinfo').datagrid('validateRow', editIndex)){
		$('#ywuserinfo').datagrid('endEdit', editIndex);
		editIndex = undefined;
		return true;
	} else {
		return false;
	}
}
function onClickRow(index){
	if ( selectIndex == undefined || selectIndex != index)
	{
		$('#ywuserinfo').datagrid('selectRow', index);
		selectIndex = index;
	} else if (selectIndex == index) {
		$('#ywuserinfo').datagrid('unselectRow', index);
		selectIndex = undefined;
	}
}
function editusr(){
	if (editIndex == undefined && selectIndex != undefined){
		$('#ywuserinfo').datagrid('beginEdit', selectIndex);
		editIndex = selectIndex;
	}
}
function canceleditusr(){
	if (editIndex != undefined){
		$('#ywuserinfo').datagrid('endEdit', editIndex);
		editIndex = undefined;
	}
}
function editusrok(url){
	if (editIndex != undefined){
		$('#ywuserinfo').datagrid('selectRow', editIndex);
		var selectitem = $('#ywuserinfo').datagrid('getSelected')
		var pwdbefore = selectitem.password
		var rolebefore = selectitem.role
		var emailbefore = selectitem.email
		$('#ywuserinfo').datagrid('endEdit', editIndex);
		editIndex = undefined;
		if ( !ismail(selectitem.email) )
		{
			return
		}
		if ( !( pwdbefore != selectitem.password || rolebefore != selectitem.role || emailbefore != selectitem.email ) )
		{
			return
		}
		if ( pwdbefore == selectitem.password )
		{
			result = postdata(url,{type:'updateusernp',id:selectitem.id,role:selectitem.role,email:selectitem.email});
		}
		else
		{
			result = postdata(url,{type:'updateuser',id:selectitem.id,pwd:selectitem.password,role:selectitem.role,email:selectitem.email});
		}
		if ( result == 'True' )
		{
			return
		}
	}
}
function delusr(url){
	var selectitem = $('#ywuserinfo').datagrid('getSelected')
	var selectindex = $('#ywuserinfo').datagrid('getRowIndex',selectitem)
	var checkedRows = $('#ywuserinfo').datagrid('getChecked');
	var delrows = new Array();
	var crlen = checkedRows.length;
	if ( crlen == 0 )
	{
		$.messager.alert('提示','请先勾选要删除的用户!','info');
		return;
	}
	for (i=0;i<crlen;i++)
	{
		delrows[i] = checkedRows[i].id;
	}
	delrows = delrows.join(",");
	var tips = "是否删除 " + crlen + " 个用户!"
	$.messager.confirm('提示',tips,function(r){    
    if (r)
	{
        result = postdata(url,{type:'deluser',id:delrows});
		if (result == 'True')
		{
			editIndex = undefined;
			selectIndex = undefined;
			parent.flashtabpage('#ct','用户',ufurl);
		}
    }    
	});
}
function ceu(){
	canceleditusr();
	userreload();
	editIndex = undefined;
	selectIndex = undefined;
}
function euok(posturl){
	editusrok(posturl);
	userreload();
	editIndex = undefined;
	selectIndex = undefined;
}
function openadduser(){
	$('#madduser').window('open');
	$("#busername").textbox('setValue','');
	$("#bpassword").val('');
	$("#bpasswordtwo").val('');
	$("#bemail").val('');
	$("#brole").combobox('setValue','2');
	$('#busername').textbox().next('span').find('input').focus();
}
$.extend($.fn.validatebox.defaults.rules, {    
	equals: {    
		validator: function(value,param){    
			return value == $(param[0]).val();    
		},    
		message: '两次输入的密码不一致！'   
	},
	username: {    
		validator: function(value,param){    
			return /^[a-zA-Z0-9\u4E00-\u9FA5]*$/.test(value)
		},
		message: '用户名只能包含数字,字母,中文！'
	}
});
function adduser(posturl){
	$.messager.progress();	// 显示进度条
	$('#au').form('submit', {
		url: posturl,
		onSubmit: function(param){
			param.type = 'adduser'; 
			var isValid = $(this).form('validate');
			var existuser = postdata(posturl,{type:'chkuser',name:$("#busername").val()});
			if (existuser == 'True'){
				isValid = false;
				$.messager.alert('提示','已存在该用户名！');
			}
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			userreload();
			$('#madduser').window('close');
			editIndex = undefined;
			selectIndex = undefined;
		}
	});
}
function formatlogin(val,row){
	if (val == 'NEVERLOGIN'){
		return '<span style="color:red;">'+val+'</span>';
	} else {
		return '<span style="color:green;">'+val+'</span>';
	}
}

function formatrole(value, rowData, rowIndex) {
	for (var i = 0; i < roletext.length; i++) {
		if (roletext[i].value == value) {
			return roletext[i].text;
		}
	}
}