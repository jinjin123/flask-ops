# -*- coding: UTF-8 -*-
import sys,modifystr,time,datetime,json,sendmail,zabbix
import MySQLdb as mysql
reload(sys) 
sys.setdefaultencoding('utf8')

zabbixtable = "zabbix"
zabbixjobtable = "zabbixjob"
jobtype={'0':"故障",'1':"维护",'2':"部署"}

def getjobinfo(dbhost,username,password,dbname,jobtable,jobdtable,userid):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "select title from %s where id = '%s'"%(jobtable,userid)
	cursor.execute(sql)
	data = cursor.fetchone()
	title = str(data[0])
	sql = "select type from %s where id = '%s'"%(jobtable,userid)
	cursor.execute(sql)
	data = cursor.fetchone()
	type = str(data[0])
	sql = "select content from %s where id = '%s'"%(jobdtable,userid)
	cursor.execute(sql)
	data = cursor.fetchone()
	content = str(data[0])
	db.close()
	result = {'title':title,'type':type,'content':content}
	return result

def getmailaddress(dbhost,username,password,dbname,usertable,jobtable,userid,type):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "select %s from %s where id = '%s'"%(type,jobtable,userid)
	cursor.execute(sql)
	res = cursor.fetchone()
	name = str(res[0])
	sql = "select email from %s where nickname = '%s'"%(usertable,name)
	cursor.execute(sql)
	res = cursor.fetchone()
	result = str(res[0])
	db.close()
	return result

def getuserrole(dbhost,username,password,dbname,usertable,tojobman):
	tojobman = mysql.escape_string(tojobman)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	result = ''
	cursor = db.cursor()
	sql = "select role from %s where nickname = '%s'"%(usertable,tojobman)
	cursor.execute(sql)
	data = cursor.fetchone()
	result = data[0]
	db.close()
	return result	

def addjob(dbhost,username,password,dbname,jobtable,jobdtable,jmtable,fromjm,cname,ccontent,cjobtype,cjobcreateman,ipaddr,dosendmail,mailfrom,maillist):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	curtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	cname = mysql.escape_string(cname)
	ccontent = mysql.escape_string(ccontent)
	ipaddr = mysql.escape_string(ipaddr)
	cursor = db.cursor()
	sql = "INSERT INTO %s (type,title,begintime,endtime,usetime,jobcreateman,jobman,status) VALUES ('%s','%s','%s','','','%s','','%s')"%(jobtable,cjobtype,cname,curtime,cjobcreateman,0)
	cursor.execute(sql)
	db.commit()
	insertid = cursor.lastrowid
	sql = "INSERT INTO %s (id,content,course,technique,score,comment) VALUES ('%s','%s','','','','')"%(jobdtable,insertid,ccontent)
	cursor.execute(sql)
	jobcourse = "%s - %s发布了事务(%s)"%(curtime,cjobcreateman.encode('gbk'),ipaddr)
	jobcourse = jobcourse.decode('gbk')
	sql = "UPDATE %s SET course = '%s' WHERE id = '%s'"%(jobdtable,jobcourse,insertid)
	cursor.execute(sql)
	if fromjm == "YES":
		sql = "INSERT INTO %s (jobid,ipaddr) VALUES ('%s','%s')"%(jmtable,insertid,ipaddr)
		cursor.execute(sql)
	db.commit()
	db.close()
	result = str(insertid)
	if dosendmail == 'True':
		mailname = "新事务(id:%s) - %s"%(insertid,cname.encode('gbk'))
		mailname = mailname.decode('gbk')
		mailcontent = "%s\n事务类型:%s\n事务内容:%s"%(jobcourse.encode('gbk'),jobtype[cjobtype],ccontent.encode('gbk'))
		mailcontent = mailcontent.decode('gbk')
		sendmail.send_mail(mailfrom,maillist,mailname,mailcontent)
	return result
	
def deljob(dbhost,username,password,dbname,jobtable,jobdtable,jmtable,jobid):
	jobidstr = ''
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	for jid in jobid:
		jid = mysql.escape_string(jid)
		jobidstr += jid + ','
	jobidstr = jobidstr[:len(jobidstr) - 1]
	sql = "delete from %s where id in (%s)"%(jobtable,jobidstr)
	cursor.execute(sql)
	sql = "delete from %s where id in (%s)"%(jobdtable,jobidstr)
	cursor.execute(sql)
	sql = "delete from %s where jobid in (%s)"%(jmtable,jobidstr)
	cursor.execute(sql)
	db.commit()
	db.close()

def getjob(dbhost,username,password,dbname,jobtable,jobdtable,jobid,jobman,dosendmail,mailfrom,maillist):
	jobid = mysql.escape_string(jobid)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "UPDATE %s SET jobman = '%s' WHERE id = '%s'"%(jobtable,jobman,jobid)
	cursor.execute(sql)
	sql = "UPDATE %s SET status = %s WHERE id = '%s'"%(jobtable,1,jobid)
	cursor.execute(sql)
	curtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	jobcourse = "\n%s - %s接手了事务"%(curtime,jobman.encode('gbk'))
	jobcourse = jobcourse.decode('gbk')
	sql = "UPDATE %s SET course = concat(course,'%s') WHERE id = '%s'"%(jobdtable,jobcourse,jobid)
	cursor.execute(sql)
	db.commit()
	db.close()
	if dosendmail == 'True':
		jobinfo = getjobinfo(dbhost,username,password,dbname,jobtable,jobdtable,jobid)
		title = jobinfo['title']
		type = jobinfo['type']
		content = jobinfo['content']
		mailname = "接手事务(id:%s) - %s"%(str(jobid),title.encode('gbk'))
		mailname = mailname.decode('gbk')
		mailcontent = "%s\n事务类型:%s\n事务内容:%s"%(jobcourse.encode('gbk'),jobtype[type],content.encode('gbk'))
		mailcontent = mailcontent.decode('gbk')
		sendmail.send_mail(mailfrom,maillist,mailname,mailcontent)
		
	
def getjobman(dbhost,username,password,dbname,jobtable,jobid):
	jobid = mysql.escape_string(jobid)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	result = ''
	cursor = db.cursor()
	sql = "select jobman from %s where id = '%s'"%(jobtable,jobid)
	cursor.execute(sql)
	data = cursor.fetchone()
	result = data[0]
	db.close()
	return result
	
def changejobman(dbhost,username,password,dbname,usertable,jobtable,jobdtable,jobid,tojobman,dosendmail,mailfrom):
	jobid = mysql.escape_string(jobid)
	tojobman = mysql.escape_string(tojobman)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "select jobman from %s where id = '%s'"%(jobtable,jobid)
	cursor.execute(sql)
	data = cursor.fetchone()
	jobman = str(data[0])
	sql = "UPDATE %s SET jobman = '%s' WHERE id = '%s'"%(jobtable,tojobman,jobid)
	cursor.execute(sql)
	curtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	jobcourse = "\n%s - %s把事务转交给了%s"%(curtime,jobman.encode('gbk'),tojobman.encode('gbk'))
	jobcourse = jobcourse.decode('gbk')
	sql = "UPDATE %s SET course = concat(course,'%s') WHERE id = '%s'"%(jobdtable,jobcourse,jobid)
	cursor.execute(sql)
	db.commit()
	db.close()
	if dosendmail == 'True':
		maillist = []
		tjmail = getmailaddress(dbhost,username,password,dbname,usertable,jobtable,jobid,"jobman")
		maillist.append(tjmail)
		jcmail = getmailaddress(dbhost,username,password,dbname,usertable,jobtable,jobid,"jobcreateman")
		maillist.append(jcmail)
		jobinfo = getjobinfo(dbhost,username,password,dbname,jobtable,jobdtable,jobid)
		title = jobinfo['title']
		type = jobinfo['type']
		content = jobinfo['content']
		mailname = "转接事务(id:%s) - %s"%(str(jobid),title.encode('gbk'))
		mailname = mailname.decode('gbk')
		mailcontent = "%s\n事务类型:%s\n事务内容:%s"%(jobcourse.encode('gbk'),jobtype[type],content.encode('gbk'))
		mailcontent = mailcontent.decode('gbk')
		sendmail.send_mail(mailfrom,maillist,mailname,mailcontent)

def getjobcreateman(dbhost,username,password,dbname,jobtable,jobid):
	jobid = mysql.escape_string(jobid)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	result = ''
	cursor = db.cursor()
	sql = "select jobcreateman from %s where id = '%s'"%(jobtable,jobid)
	cursor.execute(sql)
	data = cursor.fetchone()
	result = data[0]
	db.close()
	return result

def getjobstatus(dbhost,username,password,dbname,jobtable,jobid):
	jobid = mysql.escape_string(jobid)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	result = ''
	cursor = db.cursor()
	sql = "select status from %s where id = '%s'"%(jobtable,jobid)
	cursor.execute(sql)
	data = cursor.fetchone()
	result = data[0]
	db.close()
	return result

def ftover1day(dbhost,username,password,dbname,jobtable,jobid):
	jobid = mysql.escape_string(jobid)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	result = ''
	cursor = db.cursor()
	sql = "select endtime from %s where id = '%s'"%(jobtable,jobid)
	cursor.execute(sql)
	data = cursor.fetchone()
	endtime = data[0]
	if endtime == '':
		result = 'False'
		return result
	curtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	curtime = datetime.datetime.strptime(curtime,'%Y-%m-%d %H:%M:%S')
	endtime = datetime.datetime.strptime(endtime,'%Y-%m-%d %H:%M:%S')
	overdays = (curtime - endtime).days
	if (int(overdays) >= 1):
		result = 'True'
	else:
		result = 'False'
	db.close()
	return result

def addjobcourse(dbhost,username,password,dbname,usertable,jobtable,jobdtable,jobid,jobcourse,dosendmail,mailfrom):
	if dosendmail == 'True':
		jcmail = getmailaddress(dbhost,username,password,dbname,usertable,jobtable,jobid,"jobcreateman")
		jcmail = [jcmail]
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	jobid = mysql.escape_string(jobid)
	jobcourse = mysql.escape_string(jobcourse)
	cursor = db.cursor()
	sql = "select jobman from %s where id = '%s'"%(jobtable,jobid)
	cursor.execute(sql)
	res = cursor.fetchone()
	jobman = str(res[0])
	curtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	jobcourse = "\n%s - %s:%s"%(curtime,jobman,jobcourse)
	sql = "UPDATE %s SET course = concat(course,'%s') WHERE id = '%s'"%(jobdtable,jobcourse,jobid)
	cursor.execute(sql)
	db.commit()
	db.close()
	if dosendmail == 'True':
		jobinfo = getjobinfo(dbhost,username,password,dbname,jobtable,jobdtable,jobid)
		title = jobinfo['title']
		type = jobinfo['type']
		content = jobinfo['content']
		mailname = "事务进展(id:%s) - %s"%(str(jobid),title.encode('gbk'))
		mailname = mailname.decode('gbk')
		mailcontent = "%s\n事务类型:%s\n事务内容:%s"%(jobcourse.encode('gbk'),jobtype[type],content.encode('gbk'))
		mailcontent = mailcontent.decode('gbk')
		sendmail.send_mail(mailfrom,jcmail,mailname,mailcontent)
	
def finishjob(dbhost,username,password,dbname,usertable,jobtable,jobdtable,jobid,jobtec,dosendmail,mailfrom):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	jobid = mysql.escape_string(jobid)
	jobtec = mysql.escape_string(jobtec)
	cursor = db.cursor()
	sql = "UPDATE %s SET technique = '%s',score = '%s' WHERE id = '%s'"%(jobdtable,jobtec,'3',jobid)
	cursor.execute(sql)
	sql = "UPDATE %s SET status = %s WHERE id = '%s'"%(jobtable,2,jobid)
	cursor.execute(sql)
	curtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	sql = "UPDATE %s SET endtime = '%s' WHERE id = '%s'"%(jobtable,curtime,jobid)
	cursor.execute(sql)
	sql = "select begintime from %s where id = '%s'"%(jobtable,jobid)
	cursor.execute(sql)
	res = cursor.fetchone()
	bt = datetime.datetime.strptime(res[0],'%Y-%m-%d %H:%M:%S')
	et = datetime.datetime.strptime(curtime,'%Y-%m-%d %H:%M:%S')
	ut = str(et-bt)
	sql = "UPDATE %s SET usetime = '%s' WHERE id = '%s'"%(jobtable,ut,jobid)
	cursor.execute(sql)
	sql = "select jobman from %s where id = '%s'"%(jobtable,jobid)
	cursor.execute(sql)
	res = cursor.fetchone()
	jobman = str(res[0])
	jobcourse = "\n%s - %s完成了事务"%(curtime,jobman.encode('gbk'))
	jobcourse = jobcourse.decode('gbk')
	sql = "UPDATE %s SET course = concat(course,'%s') WHERE id = '%s'"%(jobdtable,jobcourse,jobid)
	cursor.execute(sql)
	db.commit()
	db.close()
	zabbix.finzabbixjob(dbhost,username,password,dbname,zabbixtable,zabbixjobtable,jobid)
	if dosendmail == 'True':
		jcmail = getmailaddress(dbhost,username,password,dbname,usertable,jobtable,jobid,"jobcreateman")
		jcmail = [jcmail]
		jobinfo = getjobinfo(dbhost,username,password,dbname,jobtable,jobdtable,jobid)
		title = jobinfo['title']
		type = jobinfo['type']
		content = jobinfo['content']
		mailname = "事务完成(id:%s) - %s"%(str(jobid),title.encode('gbk'))
		mailname = mailname.decode('gbk')
		mailcontent = "%s\n事务类型:%s\n事务内容:%s"%(jobcourse.encode('gbk'),jobtype[type],content.encode('gbk'))
		mailcontent = mailcontent.decode('gbk')
		sendmail.send_mail(mailfrom,jcmail,mailname,mailcontent)
	
def jobrework(dbhost,username,password,dbname,usertable,jobtable,jobdtable,jobid,dosendmail,mailfrom):
	jobid = mysql.escape_string(jobid)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "UPDATE %s SET status = %s, endtime = '', usetime = '' WHERE id = '%s'"%(jobtable,1,jobid)
	cursor.execute(sql)
	sql = "select jobcreateman from %s where id = '%s'"%(jobtable,jobid)
	cursor.execute(sql)
	data = cursor.fetchone()
	jobcman = str(data[0])
	curtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	jobcourse = "\n%s - %s确认事务没有完成"%(curtime,jobcman.encode('gbk'))
	jobcourse = jobcourse.decode('gbk')
	sql = "UPDATE %s SET course = concat(course,'%s'),score = '',comment = '' WHERE id = '%s'"%(jobdtable,jobcourse,jobid)
	cursor.execute(sql)
	db.commit()
	db.close()
	if dosendmail == 'True':
		jmail = getmailaddress(dbhost,username,password,dbname,usertable,jobtable,jobid,"jobman")
		jmail = [jmail]
		jobinfo = getjobinfo(dbhost,username,password,dbname,jobtable,jobdtable,jobid)
		title = jobinfo['title']
		type = jobinfo['type']
		content = jobinfo['content']
		mailname = "事务返工(id:%s) - %s"%(str(jobid),title.encode('gbk'))
		mailname = mailname.decode('gbk')
		mailcontent = "%s\n事务类型:%s\n事务内容:%s"%(jobcourse.encode('gbk'),jobtype[type],content.encode('gbk'))
		mailcontent = mailcontent.decode('gbk')
		sendmail.send_mail(mailfrom,jmail,mailname,mailcontent)

def jobevaluate(dbhost,username,password,dbname,jobdtable,jmtable,jobid,jobscore,jobcomment,fromjm):
	jobid = mysql.escape_string(jobid)
	jobscore = mysql.escape_string(jobscore)
	jobcomment = mysql.escape_string(jobcomment)
	fromjm = mysql.escape_string(fromjm)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "UPDATE %s SET score = '%s', comment = '%s' WHERE id = '%s'"%(jobdtable,jobscore,jobcomment,jobid)
	cursor.execute(sql)
	if fromjm == "YES":
		sql = "delete from %s where jobid = %s"%(jmtable,jobid)
		cursor.execute(sql)
	db.commit()
	db.close()
		
def getjobmanlist(dbhost,username,password,dbname,usertable):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "select nickname from %s where role <= %s"%(usertable,1)
	cursor.execute(sql)
	data = cursor.fetchall()
	result = []
	for jobman in data:
		fdata = {'value':str(jobman[0]),
		'text':str(jobman[0])}
		result.append(fdata)
	result = json.dumps(result)
	db.commit()
	db.close()
	return result

if __name__ == "__main__":
	print "test"