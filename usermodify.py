# -*- coding: UTF-8 -*-
import sys,modifystr,json
import MySQLdb as mysql
reload(sys) 
sys.setdefaultencoding('utf8')

def getuserdata(dbhost,username,password,dbname,table,page,rows,sort,order,sname,stype,scontent):
	result = []
	res = []
	statement = ''
	sortsm = ''
	page = mysql.escape_string(page)
	rows = mysql.escape_string(rows)
	sort = mysql.escape_string(sort)
	order = mysql.escape_string(order)
	sname = mysql.escape_string(sname)
	stype = mysql.escape_string(stype)
	scontent = mysql.escape_string(scontent)
	if (scontent != ''):
		if (stype == '0'):
			statement = "where %s = '%s'"%(sname,scontent)
		else:
			statement = "where %s like '%%%s%%'"%(sname,scontent)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "Select count(*) from %s %s"%(table,statement)
	cursor.execute(sql)
	data = cursor.fetchone()
	total = int(data[0])
	if page == '0':
		page = '1'
	if sort != '':
		sortsm = "order by %s %s"%(sort,order)
	sql = "Select * from %s %s %s limit %s,%s"%(table,statement,sortsm,str((int(page)-1)*int(rows)),rows)
	cursor.execute(sql)
	data = cursor.fetchall()
	db.close()
	for m in data:
		fdata = {'id':str(m[0]),
		'nickname':m[1].encode("utf-8"),
		'password':m[2].encode("utf-8"),
		'role':str(m[3]),
		'email':m[4].encode("utf-8"),
		'lastlogin':m[5].encode("utf-8")}
		res.append(fdata)
	result = json.dumps({"total":total,"rows":res})
	return result

def adduser(dbhost,username,password,dbname,table,cname,cpassword,cemail,crole):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cname = mysql.escape_string(cname)
	crole = mysql.escape_string(crole)
	cemail = mysql.escape_string(cemail)
	cursor = db.cursor()
	cpassword = modifystr.md5(cpassword)
	sql = "INSERT INTO %s (nickname,password,role,email,lastlogin) VALUES ('%s','%s','%s','%s','NEVERLOGIN')"%(table,cname,cpassword,crole,cemail)
	cursor.execute(sql)
	db.commit()
	db.close()
	
def deluser(dbhost,username,password,dbname,table,userid):
	useridstr = ''
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	for uid in userid:
		uid = mysql.escape_string(uid)
		useridstr += uid + ','
	useridstr = useridstr[:len(useridstr) - 1]
	cursor = db.cursor()
	sql = "delete from %s where id in (%s)"%(table,useridstr)
	cursor.execute(sql)
	db.commit()
	db.close()
	
def chkuser(dbhost,username,password,dbname,table,cusername):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cusername = mysql.escape_string(cusername)
	result = ''
	cursor = db.cursor()
	sql = "select count(*) from %s where nickname = '%s'"%(table,cusername)
	cursor.execute(sql)
	data = cursor.fetchone()
	if (data[0] == 0):
		result = 'False'
	else:
		result = 'True'
	db.close()
	return result

def updateuser(dbhost,username,password,dbname,table,userid,userinfo):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	usrpwd = modifystr.md5(userinfo['password'])
	usrrole = userinfo['role']
	usremail = userinfo['email']
	usremail = mysql.escape_string(usremail)
	userid = mysql.escape_string(userid)
	usrrole = int(mysql.escape_string(usrrole))
	if ( userinfo['password'] is None ):
		sql = "UPDATE %s SET %s = '%d',%s = '%s' WHERE id = '%s'"%(table,'role',usrrole,'email',usremail,userid)
	else:
		sql = "UPDATE %s SET %s = '%s',%s = '%d',%s = '%s' WHERE id = '%s'"%(table,'password',usrpwd,'role',usrrole,'email',usremail,userid)
	cursor.execute(sql)
	db.commit()
	db.close()

def updateusernp(dbhost,username,password,dbname,table,userid,userinfo):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	usrrole = userinfo['role']
	usremail = userinfo['email']
	usremail = mysql.escape_string(usremail)
	userid = mysql.escape_string(userid)
	usrrole = int(mysql.escape_string(usrrole))
	sql = "UPDATE %s SET %s = '%d',%s = '%s' WHERE id = '%s'"%(table,'role',usrrole,'email',usremail,userid)
	cursor.execute(sql)
	db.commit()
	db.close()
	
def chkpwd(dbhost,username,password,dbname,table,userid,pwd):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	result = ''
	cursor = db.cursor()
	sql = "select %s from %s where id = '%s'"%('password',table,userid)
	cursor.execute(sql)
	data = cursor.fetchone()
	rightpwd = data[0]
	pwd = modifystr.md5(pwd)
	if (pwd == rightpwd):
		result = 'True'
	else:
		result = 'False'
	db.close()
	return result

def changemail(dbhost,username,password,dbname,table,userid,content):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	content = mysql.escape_string(content)
	cursor = db.cursor()
	sql = "UPDATE %s SET %s = '%s' WHERE id = '%s'"%(table,'email',content,userid)
	cursor.execute(sql)
	db.commit()
	db.close()
	
def changepwd(dbhost,username,password,dbname,table,userid,content):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	content = modifystr.md5(content)
	sql = "UPDATE %s SET %s = '%s' WHERE id = '%s'"%(table,'password',content,userid)
	cursor.execute(sql)
	db.commit()
	db.close()

if __name__ == "__main__":
	print "test"