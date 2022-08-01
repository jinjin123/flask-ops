function jmaddjob(url,jmpurl){
	var wts = 30;	//两次提交的间隔时间(秒)
	var dt = new Date();
	var submitdate = dt.getTime();
	if ( $.cookie('jm_lastsubmitdate') != null)
	{
		if ( (parseInt(submitdate) - parseInt($.cookie('jm_lastsubmitdate'))) <= (wts * 1000) )
		{
			$.messager.alert('提示','两次提交时间间隔不能小于' + wts + '秒!');
			return;
		}
	}
	$.cookie('jm_lastsubmitdate', submitdate, { expires: 365 });
	$.cookie('jm_name', $('#jmname').val(), { expires: 365 });
	$.cookie('jm_snum', $('#jmsnum').val(), { expires: 365 });
	jmname = $('#jmname').val();
	jmsnum = $('#jmsnum').val();
	jmtitle = $('#jmtitle').val() + '(' + jmsnum + ')';
	jmdescription = $('#jmdescription').val();
	content = '姓名:' + jmname + '    座位号:' + jmsnum + '\n故障描述:\n' + jmdescription;
	$.messager.progress();	// 显示进度条
	$('#jmaj').form('submit', {
		url: url,
		onSubmit: function(param){
			param.type = 'addjob';
			param.jobtype = '0';
			param.jobname = jmtitle;
			param.jobcontent = content;
			var isValid = $(this).form('validate');
			if (!isValid){
				$.messager.progress('close');	// 如果表单是无效的则隐藏进度条
			}
			return isValid;	// 返回false终止表单提交
		},
		success: function(data){
			$.messager.progress('close');	// 如果提交成功则隐藏进度条
			jmreset();
			parent.$("#ct-tab").tabs('select',"处理进展");
			var tab = parent.$("#ct-tab").tabs('getSelected');
			parent.$("#ct-tab").tabs('update', {
				tab: tab,
				options: {
					content: '<iframe style="width:100%;height:100%;" scrolling="auto" frameborder="0" src=' + jmpurl + '></iframe>'
				}
			});
			return data;
		}
	});
}

//重置
function jmreset(){
	$("#jmtitle").textbox('setValue','');
	$("#jmdescription").textbox('setValue','');
	$('#jmtitle').textbox('textbox').focus();
}