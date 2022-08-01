# -*- coding: UTF-8 -*-
import sys,modifystr,json
import MySQLdb as mysql
reload(sys) 
sys.setdefaultencoding('utf8')

def getnote(dbhost,username,password,dbname,table,page,rows,sort,order,sname,smode,stext):
	result = []
	res = []
	statement = ''
	sortsm = ''
	page = mysql.escape_string(page)
	rows = mysql.escape_string(rows)
	sort = mysql.escape_string(sort)
	order = mysql.escape_string(order)
	sname = mysql.escape_string(sname)
	smode = mysql.escape_string(smode)
	stext = mysql.escape_string(stext)
	#Éú³ÉÉ¸Ñ¡´®
	if stext != '':
		if smode == '0':
			statement = "where %s = '%s'"%(sname,stext)
		else:
			statement = "where %s like '%%%s%%'"%(sname,stext)
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
		'title':m[1].encode("utf-8"),
		'creator':m[2].encode("utf-8"),
		'content':m[3].encode("utf-8")}
		res.append(fdata)
	result = json.dumps({"total":total,"rows":res})
	return result

def addnote(dbhost,username,password,dbname,table,title,content,name):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	title = mysql.escape_string(title)
	content = mysql.escape_string(content)
	cursor = db.cursor()
	sql = "INSERT INTO %s (title,creator,content) VALUES ('%s','%s','%s')"%(table,title,name,content)
	cursor.execute(sql)
	db.commit()
	db.close()
	
def delnote(dbhost,username,password,dbname,table,noteid):
	noteidstr = ''
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	for nid in noteid:
		nid = mysql.escape_string(nid)
		noteidstr += nid + ','
	noteidstr = noteidstr[:len(noteidstr) - 1]
	sql = "delete from %s where id in (%s)"%(table,noteidstr)
	cursor.execute(sql)
	db.commit()
	db.close()

def mdfnote(dbhost,username,password,dbname,table,id,title,content):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	id = mysql.escape_string(id)
	title = mysql.escape_string(title)
	content = mysql.escape_string(content)
	cursor = db.cursor()
	sql = "UPDATE %s SET title='%s',content='%s' where id = '%s'"%(table,title,content,id)
	cursor.execute(sql)
	db.commit()
	db.close()

def getnotecreator(dbhost,username,password,dbname,table,id):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	id = mysql.escape_string(id)
	cursor = db.cursor()
	sql = "Select creator from %s where id='%s'"%(table,id)
	cursor.execute(sql)
	data = cursor.fetchone()
	result = data[0]
	db.close()
	return result

if __name__ == "__main__":
	print "test"