# -*- coding: UTF-8 -*-
import sys,modifystr,json
import MySQLdb as mysql
reload(sys) 
sys.setdefaultencoding('utf8')

def deljmp(dbhost,username,password,dbname,table,jid):
	jid = mysql.escape_string(jid)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "delete from %s where jobid = %s"%(table,jid)
	cursor.execute(sql)
	db.commit()
	db.close()
	
def getjids(dbhost,username,password,dbname,table,ip):
	result = []
	ip = mysql.escape_string(ip)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "Select jobid from %s where ipaddr = '%s'"%(table,ip)
	cursor.execute(sql)
	data = cursor.fetchall()
	db.close()
	for m in data:
		result.append(str(m[0]))
	return result
	
def canevaluate(dbhost,username,password,dbname,jobtable,jmtable,ip):
	result = 'False'
	ip = mysql.escape_string(ip)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "select count(*) from %s,%s where %s.jobid = %s.id and %s.status = 2 and %s.ipaddr='%s'"%(jobtable,jmtable,jmtable,jobtable,jobtable,jmtable,ip)
	cursor.execute(sql)
	data = cursor.fetchone()
	db.close()
	if (int(data[0]) > 0):
		result = 'True'
	return result

if __name__ == "__main__":
	print "test"