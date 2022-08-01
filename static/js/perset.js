function changeppassword(posturl,furl){
	if ( postdata(posturl,{type:'chkpwd',pwd:$("#poldpasswd").val()}) == 'False' ){
		$.messager.alert('提示','密码不正确！');
		return;
	}
	if ( $("#pnewpasswd").val() == '' )
	{
		$.messager.alert('提示','请输入密码！');
		return;
	}
	if ( $("#pnewpasswd").val() != $("#pnewpasswdtwo").val() )
	{
		$.messager.alert('提示','两次输入的密码不一致！');
		return;
	}
	$.messager.progress();	// 显示进度条
	$('#cp').form('submit', {
		url: posturl,
		onSubmit: function(param){
			param.type = 'changeppassword'; 
			var isValid = $(this).form('validate');
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			parent.flashtabpage('#ct','个人设置',furl);
		}
	});
}
function changepemail(posturl,furl){
	$.messager.progress();	// 显示进度条
	$('#cm').form('submit', {
		url: posturl,
		onSubmit: function(param){
			param.type = 'changepemail'; 
			var isValid = $(this).form('validate');
			if ( !(ismail($('#pemail').val())) ){
				isValid = false;
				$.messager.alert('提示','邮箱格式不正确！');
			}
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			parent.flashtabpage('#ct','个人设置',furl);
		}
	});
}