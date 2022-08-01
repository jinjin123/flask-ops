# -*- coding: UTF-8 -*-
import MySQLdb as mysql
import sys,os,time,threading,ConfigParser,json,re
from flask import Flask, g, flash, request, render_template, url_for, redirect, session, jsonify, make_response
from flask.ext.login import LoginManager,login_user, logout_user, current_user, login_required
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from uploader import Uploader
import Model,modifystr,usermodify,ywjob,jobmodify,serveract,zabbix,ywnote,jmjob,statistics
reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
path = os.getcwd()
config = ConfigParser.ConfigParser()
if (os.path.exists(path + "/ywsetting.ini")):
	config.read(path + "/ywsetting.ini")
else:
	print "ywsetting.ini not found!"
ywdb = config.get("db","database")
ywdbhost = config.get("db","host")
ywdbuser = config.get("db","user")
ywdbpwd = config.get("db","password")
ywsk = config.get("main","SECRET_KEY")
ywhost = config.get("main","host")
ywport = config.get("main","port")
ywdebug = config.get("main","debug")
jmusername = config.get("jm","username")
jmpassword = config.get("jm","password")
ywemail = config.get("jobemail","enable")
mail_host = config.get("jobemail","mail_host")
mail_user = config.get("jobemail","mail_user")
mail_pass = config.get("jobemail","mail_pass")
mail_postfix = config.get("jobemail","mail_postfix")
ywemailfrom = {'host':mail_host,'user':mail_user,'pwd':mail_pass,'postfix':mail_postfix}
ywemaillist = config.get("jobemail","mailto_list")
ywemaillist = ywemaillist.split(",")
ywzestr = config.get("zabbix","connectstr")
usertable = "Users"
jobtable = "Job"
jobdtable = "Jobdetail"
jmtable = "jmjob"
svrtable = "Server"
svracttable = "Serveraction"
notetable = "Note"
zabbixtable = "zabbix"
zabbixjobtable = "zabbixjob"
lm = LoginManager()
app.config["SECRET_KEY"] = ywsk
dbsqlstr = 'mysql://%s:%s@%s/%s?charset=utf8'%(ywdbuser,ywdbpwd,ywdbhost,ywdb)
engine = create_engine(dbsqlstr,pool_recycle=60)
DBSession = sessionmaker(bind=engine)
mdbsession = DBSession()
lm.init_app(app)
lm.login_view = 'login'

@lm.user_loader
def load_user(userid):
	user = mdbsession.query(Model.User).get(int(userid))
	mdbsession.close()
	return user

@app.before_request
def before_request():
	g.user = current_user

@app.route("/login/", methods=["GET", "POST"])
def login():
	nexturl = ''
	if request.method == 'GET':
		nexturl = request.args.get("next")
	if ( (g.user is not None) and (g.user.is_authenticated != False) ):
		return redirect(url_for('index'))
	if request.method == 'POST':
		username = request.form['Username']
		password = request.form['Password']
		url = request.form['nexturl']
		rember = request.form.get('rememberme')
		if rember is None:
			rember = False
		else:
			rember = True
		user = mdbsession.query(Model.User).filter_by(nickname = username).first()
		if user is None:
			flash("用户名有误！",'error')
		else:
			password = modifystr.md5(password)
			if password != user.password:
				flash("密码有误！",'error')
			else:
				curtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
				user.lastlogin = curtime
				mdbsession.commit()
				login_user(user,remember = rember)
				mdbsession.close()
				if url == "None":
					url = None
				return redirect(url or url_for("index"))
	return render_template('login.html',nexturl=nexturl)
	
@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/favicon.ico')
def favicon():
	return redirect(url_for('static', filename='favicon.ico'), code=301)	
	
@app.route("/", methods=["GET", "POST"])
@app.route("/index/", methods=["GET", "POST"])
@login_required
def index():
	if ( g.user.nickname == jmusername ):
		logout_user()
		return redirect(url_for('login'))
	return render_template('index.html')

@app.route("/welcome/", methods=["GET", "POST"])
@login_required
def welcome():
	return render_template('welcome.html')

@app.route('/upload/', methods=['GET', 'POST', 'OPTIONS'])
@login_required
def upload():
	if (g.user.role >= 2):
		return "ERROR！"
	"""UEditor文件上传接口
	config 配置文件
	result 返回结果
	"""
	mimetype = 'application/json'
	result = {}
	action = request.args.get('action')
	# 解析JSON格式的配置文件
	with open(os.path.join(app.static_folder, 'ueditor','config.json')) as fp:
		try:
			# 删除 `/**/` 之间的注释
			CONFIG = json.loads(re.sub(r'\/\*.*\*\/', '', fp.read()))
		except:
			CONFIG = {}
	if action == 'config':
		# 初始化时，返回配置文件给客户端
		result = CONFIG
	elif action in ('uploadimage', 'uploadfile', 'uploadvideo'):
		# 图片、文件、视频上传
		if action == 'uploadimage':
			fieldName = CONFIG.get('imageFieldName')
			config = {
				"pathFormat": CONFIG['imagePathFormat'],
				"maxSize": CONFIG['imageMaxSize'],
				"allowFiles": CONFIG['imageAllowFiles']
			}
		elif action == 'uploadvideo':
			fieldName = CONFIG.get('videoFieldName')
			config = {
				"pathFormat": CONFIG['videoPathFormat'],
				"maxSize": CONFIG['videoMaxSize'],
				"allowFiles": CONFIG['videoAllowFiles']
			}
		else:
			fieldName = CONFIG.get('fileFieldName')
			config = {
				"pathFormat": CONFIG['filePathFormat'],
				"maxSize": CONFIG['fileMaxSize'],
				"allowFiles": CONFIG['fileAllowFiles']
			}
		if fieldName in request.files:
			field = request.files[fieldName]
			uploader = Uploader(field, config, app.static_folder)
			result = uploader.getFileInfo()
		else:
			result['state'] = '上传接口出错'
	elif action in ('uploadscrawl'):
		# 涂鸦上传
		fieldName = CONFIG.get('scrawlFieldName')
		config = {
			"pathFormat": CONFIG.get('scrawlPathFormat'),
			"maxSize": CONFIG.get('scrawlMaxSize'),
			"allowFiles": CONFIG.get('scrawlAllowFiles'),
			"oriName": "scrawl.png"
		}
		if fieldName in request.form:
			field = request.form[fieldName]
			uploader = Uploader(field, config, app.static_folder, 'base64')
			result = uploader.getFileInfo()
		else:
			result['state'] = '上传接口出错'
	elif action in ('catchimage'):
		config = {
			"pathFormat": CONFIG['catcherPathFormat'],
			"maxSize": CONFIG['catcherMaxSize'],
			"allowFiles": CONFIG['catcherAllowFiles'],
			"oriName": "remote.png"
		}
		fieldName = CONFIG['catcherFieldName']
		if fieldName in request.form:
			source = []
		elif '%s[]' % fieldName in request.form:
			source = request.form.getlist('%s[]' % fieldName)
		_list = []
		for imgurl in source:
			uploader = Uploader(imgurl, config, app.static_folder, 'remote')
			info = uploader.getFileInfo()
			_list.append({
				'state': info['state'],
				'url': info['url'],
				'original': info['original'],
				'source': imgurl,
			})
		result['state'] = 'SUCCESS' if len(_list) > 0 else 'ERROR'
		result['list'] = _list
	else:
		result['state'] = '请求地址出错'
	result = json.dumps(result)
	if 'callback' in request.args:
		callback = request.args.get('callback')
		if re.match(r'^[\w_]+$', callback):
			result = '%s(%s)' % (callback, result)
			mimetype = 'application/javascript'
		else:
			result = json.dumps({'state': 'callback参数不合法'})
	res = make_response(result)
	res.mimetype = mimetype
	res.headers['Access-Control-Allow-Origin'] = '*'
	res.headers['Access-Control-Allow-Headers'] = 'X-Requested-With,X_Requested_With'
	return res
	
@app.route("/user/", methods=["GET", "POST"])
@login_required
def user():
	if (g.user.role != 0):
		return "你没有权限查看该页面！"
	return render_template('user.html')

@app.route("/perset/", methods=["GET", "POST"])
@login_required
def perset():
	if ( g.user.nickname == jmusername ):
		logout_user()
		return redirect(url_for('login'))
	return render_template('perset.html')	
	
@app.route("/job/", methods=["GET", "POST"])
@login_required
def job():
	if ( g.user.nickname == jmusername ):
		logout_user()
		return redirect(url_for('login'))
	return render_template('job.html')	

@app.route("/jobform/", methods=["GET", "POST"])
@login_required
def jobform():
	if ( g.user.nickname == jmusername ):
		logout_user()
		return redirect(url_for('login'))
	return render_template('jobform.html')

@app.route("/jobmodify", methods=["POST"])
@login_required
def jobmdf():
	if g.user.is_authenticated == False:
		return "error"
	result = 'False'
	fromjm = ''
	type = request.form['type']
	if type == 'addjob':
		name = request.form['jobname']
		content = request.form['jobcontent']
		jobtype = request.form['jobtype']
		if (g.user.nickname == jmusername):
			fromjm = 'YES'
		jobcreateman = g.user.nickname
		if request.headers.getlist("X-Forwarded-For"):
		   ip = request.headers.getlist("X-Forwarded-For")[0]
		else:
		   ip = request.remote_addr
		maillist = ywemaillist[:]
		result = jobmodify.addjob(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobdtable,jmtable,fromjm,name,content,jobtype,jobcreateman,ip,ywemail,ywemailfrom,maillist)
	if type == 'deljob':
		jobids = request.form['jobid']
		jobids = jobids.split(',')
		username = g.user.nickname
		userrole = str(g.user.role)
		for jobid in jobids:
			jobcname = jobmodify.getjobcreateman(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid)
			jobstatus = str(jobmodify.getjobstatus(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid))
			if ((userrole != '0') and ((username != jobcname) or (not(username == jobcname and jobstatus == '0')))):
				return 'False'
		jobmodify.deljob(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobdtable,jmtable,jobids)
		result = 'True'
	if type == 'getjob':
		jobid = request.form['jobid']
		jobman = g.user.nickname
		jobmanname = jobmodify.getjobman(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid)
		jobstatus = str(jobmodify.getjobstatus(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid))
		if ((int(g.user.role) >= 2) or (jobstatus == '2') or (jobmanname != '')):
			return "ERROR！"
		maillist = ywemaillist[:]
		jobmodify.getjob(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobdtable,jobid,jobman,ywemail,ywemailfrom,maillist)
		result = 'True'
	if type == 'getjobman':
		jobid = request.form['jobid']
		result = jobmodify.getjobman(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid)
	if type == 'changejobman':
		jobid = request.form['jobid']
		tojobman = str(request.form['tojobman'])
		jobmanname = jobmodify.getjobman(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid)
		jobstatus = str(jobmodify.getjobstatus(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid))
		userrole = int(jobmodify.getuserrole(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable,tojobman))
		if ((g.user.nickname != jobmanname) or (jobstatus == '2') or (userrole >= 2) or (jobmanname == tojobman)):
			return "ERROR！"
		jobmodify.changejobman(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable,jobtable,jobdtable,jobid,tojobman,ywemail,ywemailfrom)
		result = 'True'
	if type == 'addjobcourse':
		jobid = request.form['jobid']
		jobcourse = request.form['jobcourse']
		jobmanname = jobmodify.getjobman(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid)
		jobstatus = str(jobmodify.getjobstatus(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid))
		if ((g.user.nickname != jobmanname) or (jobstatus == '2')):
			return "ERROR！"
		jobmodify.addjobcourse(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable,jobtable,jobdtable,jobid,jobcourse,ywemail,ywemailfrom)
		result = 'True'
	if type == 'finishjob':
		jobid = request.form['jobid']
		jobtec = request.form['jobtec']
		jobmanname = jobmodify.getjobman(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid)
		jobstatus = str(jobmodify.getjobstatus(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid))
		if ((g.user.nickname != jobmanname) or (jobstatus == '2')):
			return "ERROR！"
		jobmodify.finishjob(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable,jobtable,jobdtable,jobid,jobtec,ywemail,ywemailfrom)
		result = 'True'
	if type == 'jobevaluate':
		jobid = request.form['jobid']
		jobscore = request.form['jobscore']
		jobcomment = request.form['jobcomment']
		if (g.user.nickname == jmusername):
			fromjm = 'YES'
		jobcname = jobmodify.getjobcreateman(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid)
		jobstatus = str(jobmodify.getjobstatus(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid))
		ftover1day = jobmodify.ftover1day(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid)
		if ((g.user.nickname != jobcname) or (jobstatus != '2') or ( (jobstatus == '2') and (ftover1day == 'True') )):
			return "ERROR！"
		jobmodify.jobevaluate(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobdtable,jmtable,jobid,jobscore,jobcomment,fromjm)
		result = 'True'		
	if type == 'jobrework':
		jobid = request.form['jobid']
		jobcname = jobmodify.getjobcreateman(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid)
		jobstatus = str(jobmodify.getjobstatus(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid))
		ftover1day = jobmodify.ftover1day(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid)
		if ((g.user.nickname != jobcname) or (jobstatus != '2') or ( (jobstatus == '2') and (ftover1day == 'True') )):
			return "ERROR！"
		jobmodify.jobrework(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable,jobtable,jobdtable,jobid,ywemail,ywemailfrom)
		result = 'True'
	if type == 'chkjobman':
		jobid = request.form['jobid']
		jobman = g.user.nickname
		jobmanname = jobmodify.getjobman(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid)
		if (jobman == jobmanname):
			result = 'True'
	if type == 'getrole':
		result = str(g.user.role)
	if type == 'getjobstatus':
		jobid = request.form['jobid']
		result = str(jobmodify.getjobstatus(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid))
	if type == 'isjobcreateman':
		jobid = request.form['jobid']
		name = g.user.nickname
		jobcname = jobmodify.getjobcreateman(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid)
		if (name == jobcname):
			result = 'True'
	if type == 'ftover1day':
		jobid = request.form['jobid']
		result = jobmodify.ftover1day(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobid)
	return result

@app.route("/jobmanlist", methods=["POST"])
@login_required
def jobmanlist():
	if (g.user.role >= 2):
		return "error"
	result = jobmodify.getjobmanlist(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable)
	return result
	
@app.route("/userform/", methods=["GET"])
@login_required
def userform():
	if (g.user.role != 0):
		return "你没有权限查看该页面！"
	return render_template('userform.html')
	
@app.route("/usermodify", methods=["POST"])
@login_required
def usermdf():
	result = 'False'
	type = request.form['type']
	if type == 'chkuser':
		name = request.form['name']
		result = usermodify.chkuser(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable,name)
	if type == 'chkpwd':
		id = g.user.id
		pwd = request.form['pwd']
		result = usermodify.chkpwd(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable,id,pwd)
	if type == 'updateuser':
		if (g.user.role != 0):
			return "error"
		id = request.form['id']
		pwd = request.form['pwd']
		role = request.form['role']
		email = request.form['email']
		userinfo = {
		'password':pwd,
		'role':role,
		'email':email
		}
		usermodify.updateuser(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable,id,userinfo)
		result = 'True'
	if type == 'updateusernp':
		if (g.user.role != 0):
			return "error"
		id = request.form['id']
		role = request.form['role']
		email = request.form['email']
		userinfo = {
		'role':role,
		'email':email
		}
		usermodify.updateusernp(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable,id,userinfo)
		result = 'True'
	if type == 'adduser':
		if (g.user.role != 0):
			return "error"
		name = request.form['name']
		password = request.form['password']
		email = request.form['email']
		role = request.form['role']
		usermodify.adduser(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable,name,password,email,role)
		result = 'True'
	if type == 'deluser':
		if (g.user.role != 0):
			return "error"
		id = request.form['id']
		id = id.split(',')
		usermodify.deluser(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable,id)
		result = 'True'
	if type == 'changepemail':
		id = g.user.id
		mail = request.form['mail']
		usermodify.changemail(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable,id,mail)
		result = 'True'
	if type == 'changeppassword':
		id = g.user.id
		pwd = request.form['pwd']
		usermodify.changepwd(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable,id,pwd)
		result = 'True'
	return result

@app.route("/userdata", methods=["POST"])
@login_required
def userdata():
	if (g.user.role != 0):
		return "error"
	result = ''
	page = request.form['page']
	rows = request.form['rows']
	sort = request.form['sort']
	order = request.form['order']
	sname = request.form['sname']
	stype = request.form['stype']
	scontent = request.form['scontent']
	result = usermodify.getuserdata(ywdbhost,ywdbuser,ywdbpwd,ywdb,usertable,page,rows,sort,order,sname,stype,scontent)
	return result
	
@app.route("/jobdata", methods=["POST"])
@login_required
def jobdata():
	if g.user.is_authenticated == False:
		return "error"
	result = ''
	ipaddr = ''
	fromjm = ''
	page = request.form['page']
	rows = request.form['rows']
	sort = request.form['sort']
	order = request.form['order']
	btf = request.form['fbegintimef']
	btt = request.form['fbegintimet']
	etf = request.form['fendtimef']
	ett = request.form['fendtimet']
	status = request.form['fstatus']
	type = request.form['ftype']
	othername = request.form['fotname']
	othertype = request.form['fotstype']
	othercontent = request.form['fotscontent']
	if (g.user.nickname == jmusername):
		fromjm = 'YES'
	if fromjm == 'YES':
		if request.headers.getlist("X-Forwarded-For"):
		   ipaddr = request.headers.getlist("X-Forwarded-For")[0]
		else:
		   ipaddr = request.remote_addr
	result = ywjob.getjobdata(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jmtable,page,rows,sort,order,btf,btt,etf,ett,status,type,othername,othertype,othercontent,ipaddr)
	return result

@app.route("/jobdatadetail", methods=["POST"])
@login_required
def jobdatadetail():
	if g.user.is_authenticated == False:
		return "error"
	result = ''
	id = request.args.get("id")
	if id is not None:
		result = ywjob.getjobdatadetail(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobdtable,id)
	return result

@app.route("/svract/", methods=["GET", "POST"])
@login_required
def svract():
	if (g.user.role >= 2):
		return "你没有权限查看该页面！"
	return render_template('svract.html')

@app.route("/svractform/", methods=["GET"])
@login_required
def svractform():
	if (g.user.role >= 2):
		return "你没有权限查看该页面！"
	return render_template('svractform.html')

@app.route("/svractdata", methods=["POST"])
@login_required
def svractdata():
	if (g.user.role >= 2):
		return "error"
	result = ''
	name = g.user.nickname
	role = g.user.role
	page = request.form['page']
	rows = request.form['rows']
	sort = request.form['sort']
	order = request.form['order']
	stf = request.form['stf']
	stt = request.form['stt']
	sname = request.form['sname']
	stype = request.form['stype']
	scontent = request.form['scontent']
	loadtype = ''
	result = serveract.getsvrdata(loadtype,ywdbhost,ywdbuser,ywdbpwd,ywdb,svrtable,page,rows,sort,order,stf,stt,sname,stype,scontent,name,role)
	return result

@app.route("/serveraction", methods=["POST"])
@login_required
def serveraction():
	if (g.user.role >= 2):
		return "error"
	result = ''
	page = request.form['page']
	rows = request.form['rows']
	id = request.form['said']
	sort = request.form['sort']
	order = request.form['order']
	atf = request.form['atf']
	att = request.form['att']
	sname = request.form['sname']
	stype = request.form['stype']
	scontent = request.form['scontent']
	if id is not None:
		result = serveract.getserveraction(ywdbhost,ywdbuser,ywdbpwd,ywdb,svracttable,id,page,rows,sort,order,atf,att,sname,stype,scontent)
	return result
	
@app.route("/saexceldownload", methods=["GET"])
@login_required
def saexceldownload():
	if (g.user.role >= 2):
		return "error"
	result = ''
	name = g.user.nickname
	role = g.user.role
	sort = request.args.get("sort")
	order = request.args.get("order")
	sname = request.args.get("sname")
	stype = request.args.get("stype")
	scontent = request.args.get("scontent")
	if sort is None:
		sort = ''
	if order is None:
		order = ''
	if sname is None:
		sname = ''
	if stype is None:
		stype = ''
	if scontent is None:
		scontent = ''
	loadtype = 'excel'
	page = ''
	rows = ''
	stf = ''
	stt = ''
	result = serveract.getsvrdata(loadtype,ywdbhost,ywdbuser,ywdbpwd,ywdb,svrtable,page,rows,sort,order,stf,stt,sname,stype,scontent,name,role)
	response = make_response(result)
	response.headers['Content-Type'] = 'application/vnd.ms-excel' 
	response.headers['Content-Disposition'] = 'attachment; filename=data.xls'
	result = response
	return result
	
@app.route("/svractmodify", methods=["POST"])
@login_required
def svractmdf():
	if (g.user.role >= 2):
		return "ERROR"
	result = 'False'
	type = request.form['type']
	name = g.user.nickname
	role = g.user.role
	if type == 'addserver':
		svrname = request.form['svrname']
		remarks = request.form['remarks']
		onlyusers = request.form['onlyusers']
		serveract.addserver(ywdbhost,ywdbuser,ywdbpwd,ywdb,svrtable,svrname,remarks,onlyusers)
		result = 'True'
	if type == 'changesvr':
		id = request.form['id']
		svrname = request.form['csvrname']
		remarks = request.form['cremarks']
		onlyusers = request.form['onlyusers']
		ce = serveract.cesvr(ywdbhost,ywdbuser,ywdbpwd,ywdb,svrtable,name,id)
		if ((role != 0) and (ce != 'True')):
			return 'False'
		serveract.changesvr(ywdbhost,ywdbuser,ywdbpwd,ywdb,svrtable,id,svrname,remarks,onlyusers)
		result = 'True'	
	if type == 'delsvr':
		ids = request.form['id']
		ids = ids.split(',')
		for id in ids:
			ce = serveract.cesvr(ywdbhost,ywdbuser,ywdbpwd,ywdb,svrtable,name,id)
			if ((role != 0) and (ce != 'True')):
				return 'False'
		serveract.delsvr(ywdbhost,ywdbuser,ywdbpwd,ywdb,svrtable,svracttable,ids)
		result = 'True'
	if type == 'addsvract':
		serverid = request.form['serverid']
		svraction = request.form['svraction']
		ce = serveract.cesvr(ywdbhost,ywdbuser,ywdbpwd,ywdb,svrtable,name,serverid)
		if ((role != 0) and (ce != 'True')):
			return 'False'
		serveract.addsvract(ywdbhost,ywdbuser,ywdbpwd,ywdb,svrtable,svracttable,serverid,name,svraction)
		result = 'True'
	if type == 'delsvract':
		id = request.form['id']
		ce = serveract.cesvr(ywdbhost,ywdbuser,ywdbpwd,ywdb,svrtable,name,id)
		if ((role != 0) and (ce != 'True')):
			return 'False'
		serveract.delsvract(ywdbhost,ywdbuser,ywdbpwd,ywdb,svracttable,id)
		result = 'True'
	return result

@app.route("/zabbixevent/", methods=["GET", "POST"])
@login_required
def zabbixevent():
	if (g.user.role >= 2):
		return "你没有权限查看该页面！"
	return render_template('zabbixevent.html')

@app.route("/zabbixeventform/", methods=["GET"])
@login_required
def zabbixeventform():
	if (g.user.role >= 2):
		return "你没有权限查看该页面！"
	return render_template('zabbixeventform.html')

'''
@app.route("/zabbixeventdata", methods=["POST"])
@login_required
def zabbixeventdata():
	if (g.user.role >= 2):
		return "ERROR"
	result = {"rows": [], "total": 0}
	zabbixlist = eval(ywzestr)
	for zabbixhost in zabbixlist: 
		address = zabbixhost['address']
		username = zabbixhost['username']
		password = zabbixhost['password']
		zabbixapi = zabbix.ZabbixAPI(address=address, username=username, password=password) 
		zabbixtg = eval(zabbixapi.trigger_get())
		for tg in zabbixtg['rows']:
			result['rows'].append(tg)
		result['total'] += zabbixtg['total']
	result = json.dumps(result)
	return result
'''
@app.route("/zabbixeventdata", methods=["POST"])
@login_required
def zabbixeventdata():
	if (g.user.role >= 2):
		return "error"
	result = ''
	page = request.form['page']
	rows = request.form['rows']
	sort = request.form['sort']
	order = request.form['order']
	htf = request.form['fhappentimef']
	htt = request.form['fhappentimet']
	name = request.form['fotname']
	type = request.form['fottype']
	content = request.form['fotcontent']
	showfinish = request.form['showfinish']
	result = zabbix.getevents(ywdbhost,ywdbuser,ywdbpwd,ywdb,zabbixtable,page,rows,sort,order,htf,htt,name,type,content,showfinish)
	return result

@app.route("/zabbixmodify", methods=["POST"])
@login_required
def zabbixmdf():
	if (g.user.role >= 2):
		return "ERROR"
	result = 'False'
	type = request.form['type']
	if type == 'ignoreevent':
		id = request.form['id']
		zabbix.ignoreevent(ywdbhost,ywdbuser,ywdbpwd,ywdb,zabbixtable,id)
		result = 'True'
	if type == 'setstatusdoing':
		id = request.form['id']
		zabbix.setstatusdoing(ywdbhost,ywdbuser,ywdbpwd,ywdb,zabbixtable,id)
		result = 'True'
	if type == 'delzfe':
		if (g.user.role != 0):
			return "只有管理员有权限！"
		rng = request.form['rng']
		zfetime = request.form['zfetime']
		if (rng == '1' and zfetime == ''):
			return "error!"
		zabbix.delzfe(ywdbhost,ywdbuser,ywdbpwd,ywdb,zabbixtable,rng,zfetime)
		result = 'True'
	if type == 'getrole':
		result = str(g.user.role)
	return result
	
@app.route("/zabbixjobmodify", methods=["POST"])
@login_required
def zjmdf():
	if (g.user.role >= 2):
		return "ERROR"
	result = 'False'
	type = request.form['type']
	if type == 'add':
		jid = request.form['jid']
		zeid = request.form['zeid']
		zabbix.addzabbixjob(ywdbhost,ywdbuser,ywdbpwd,ywdb,zabbixjobtable,jid,zeid)
		result = 'True'
	return result
	
@app.route("/note/", methods=["GET", "POST"])
@login_required
def note():
	if (g.user.role >= 2):
		return "你没有权限查看该页面！"
	return render_template('note.html')

@app.route("/noteform/", methods=["GET"])
@login_required
def noteform():
	if (g.user.role >= 2):
		return "你没有权限查看该页面！"
	return render_template('noteform.html')	
	
@app.route("/addnoteform/", methods=["GET"])
@login_required
def addnoteform():
	if (g.user.role >= 2):
		return "你没有权限查看该页面！"
	return render_template('addnote.html')
	
@app.route("/mdfnoteform/", methods=["GET"])
@login_required
def mdfnoteform():
	if (g.user.role >= 2):
		return "你没有权限查看该页面！"
	return render_template('mdfnote.html')

@app.route("/notedata", methods=["POST"])
@login_required
def notedata():
	if (g.user.role >= 2):
		return "error"
	result = ''
	page = request.form['page']
	rows = request.form['rows']
	sort = request.form['sort']
	order = request.form['order']
	sname = request.form['sname']
	smode = request.form['smode']
	stext = request.form['stext']
	result = ywnote.getnote(ywdbhost,ywdbuser,ywdbpwd,ywdb,notetable,page,rows,sort,order,sname,smode,stext)
	return result

@app.route("/notemodify", methods=["POST"])
@login_required
def notemdf():
	if (g.user.role >= 2):
		return "error"
	result = 'False'
	type = request.form['type']
	name = g.user.nickname
	userrole = str(g.user.role)
	if type == 'addnote':
		title = request.form['notetitle']
		content = request.form['editorValue']
		ywnote.addnote(ywdbhost,ywdbuser,ywdbpwd,ywdb,notetable,title,content,name)
		result = 'True'
	if type == 'delnote':
		ids = request.form['id']
		ids = ids.split(',')
		for id in ids:
			notecreator = ywnote.getnotecreator(ywdbhost,ywdbuser,ywdbpwd,ywdb,notetable,id)
			if (userrole != '0') and (name != notecreator):
				return 'False'
		ywnote.delnote(ywdbhost,ywdbuser,ywdbpwd,ywdb,notetable,ids)
		result = 'True'
	if type == 'mdfnote':
		id = request.form['id']
		title = request.form['notetitle']
		content = request.form['editorValue']
		notecreator = ywnote.getnotecreator(ywdbhost,ywdbuser,ywdbpwd,ywdb,notetable,id)
		if (userrole != '0') and (name != notecreator):
			return "你没有权限！"
		ywnote.mdfnote(ywdbhost,ywdbuser,ywdbpwd,ywdb,notetable,id,title,content)
		result = 'True'
	if type == 'getrole':
		result = str(g.user.role)
	if type == 'iscreator':
		id = request.form['id']
		creator = ywnote.getnotecreator(ywdbhost,ywdbuser,ywdbpwd,ywdb,notetable,id)
		if (name == creator):
			result = 'True'
	return result	

@app.route("/jm/", methods=["GET"])
def jm():
	username = jmusername
	password = jmpassword
	user = mdbsession.query(Model.User).filter_by(nickname = username).first()
	if user is None:
		return "ERROR"
	else:
		password = modifystr.md5(password)
		if password != user.password:
			return "ERROR"
		else:
			mdbsession.commit()
			login_user(user)
			mdbsession.close()
	return render_template('jm.html')

@app.route("/jmfd/", methods=["GET"])
def jmfd():
	if ( g.user.is_authenticated == False ):
		return "ERROR"
	return render_template('jmfd.html')

@app.route("/jmprogress/", methods=["GET"])
def jmprogress():
	if ( g.user.is_authenticated == False ):
		return "ERROR"
	return render_template('jmprogress.html')

@app.route("/jmmodify", methods=["POST"])
@login_required
def jmmdf():
	result = 'False'
	type = request.form['type']
	if request.headers.getlist("X-Forwarded-For"):
	   ip = request.headers.getlist("X-Forwarded-For")[0]
	else:
	   ip = request.remote_addr
	if type == 'cleanjmp':
		jids = jmjob.getjids(ywdbhost,ywdbuser,ywdbpwd,ywdb,jmtable,ip)
		for jid in jids:
			res = jobmodify.ftover1day(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jid)
			if res == 'True':
				jmjob.deljmp(ywdbhost,ywdbuser,ywdbpwd,ywdb,jmtable,jid)
		result = 'True'
	if type == 'canevaluate':
		result = jmjob.canevaluate(ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jmtable,ip)
	return result

@app.route("/jobstat/", methods=["GET", "POST"])
@login_required
def jobstat():
	if (g.user.role >= 2):
		return "你没有权限查看该页面！"
	return render_template('jobstat.html')

@app.route("/jobstatform/", methods=["GET"])
@login_required
def jobstatform():
	if (g.user.role >= 2):
		return "你没有权限查看该页面！"
	return render_template('jobstatform.html')
	
@app.route("/jobstatdata", methods=["POST"])
@login_required
def jobstatdata():
	if (g.user.role >= 2):
		return "ERROR"
	result = ''
	page = request.form['page']
	rows = request.form['rows']
	sort = request.form['sort']
	order = request.form['order']
	ftimef = request.form['ftimef']
	ftimet = request.form['ftimet']
	ftype = request.form['ftype']
	loadtype = ''
	result = statistics.jobstat(loadtype,ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobdtable,page,rows,sort,order,ftimef,ftimet,ftype)
	return result

@app.route("/jsexceldownload", methods=["GET"])
@login_required
def jsexceldownload():
	if (g.user.role >= 2):
		return "error"
	result = ''
	sort = request.args.get("sort")
	order = request.args.get("order")
	ftimef = request.args.get("ftimef")
	ftimet = request.args.get("ftimet")
	ftype = request.args.get("ftype")
	if sort is None:
		sort = ''
	if order is None:
		order = ''
	if ftimef is None:
		ftimef = ''
	if ftimet is None:
		ftimet = ''
	if ftype is None:
		ftype = ''
	loadtype = 'excel'
	page = ''
	rows = ''
	result = statistics.jobstat(loadtype,ywdbhost,ywdbuser,ywdbpwd,ywdb,jobtable,jobdtable,page,rows,sort,order,ftimef,ftimet,ftype)
	response = make_response(result)
	response.headers['Content-Type'] = 'application/vnd.ms-excel' 
	response.headers['Content-Disposition'] = 'attachment; filename=statistics.xls'
	result = response
	return result

if __name__ == "__main__":
	if (ywdebug == "true"):
		debugs = True
	else:
		debugs = False
	app.run(host=ywhost, port=int(ywport), debug=debugs)