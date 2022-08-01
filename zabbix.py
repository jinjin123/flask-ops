# -*- coding: UTF-8 -*-
import json,urllib2,sys
from urllib2 import URLError
import MySQLdb as mysql
reload(sys) 
sys.setdefaultencoding('utf8')

class ZabbixAPI:
	def __init__(self,address,username,password): 
		self.address = address 
		self.username = username 
		self.password = password 
		self.url = '%s/api_jsonrpc.php' % self.address 
		self.header = {"Content-Type":"application/json"} 

	def user_login(self): 
		data = json.dumps({ 
		"jsonrpc": "2.0", 
		"method": "user.login", 
		"params": { 
		"user": self.username, 
		"password": self.password 
		}, 
		"id": 0
		}) 
		request = urllib2.Request(self.url, data) 
		for key in self.header: 
			request.add_header(key, self.header[key]) 
		try: 
			result = urllib2.urlopen(request) 
		except URLError as e: 
			print "Auth Failed, please Check your name and password:", e.code 
		else: 
			response = json.loads(result.read()) 
			result.close() 
			self.authID = response['result'] 
			return self.authID 

	def trigger_get(self): 
		res = []
		data = json.dumps({ 
		"jsonrpc":"2.0", 
		"method":"trigger.get", 
		"params": { 
		"output": [ 
		"triggerid", 
		"description", 
		"priority"
		], 
		"filter": { 
		"value": 1
		}, 
		"expandData":"hostname", 
		"sortfield": "priority", 
		"sortorder": "DESC"
		}, 
		"auth": self.user_login(), 
		"id":1 
		})
		request = urllib2.Request(self.url, data) 
		for key in self.header: 
			request.add_header(key, self.header[key]) 
		try: 
			result = urllib2.urlopen(request) 
		except URLError as e: 
			print "Error as ", e 
		else: 
			response = json.loads(result.read()) 
			result.close() 
			issues = response['result']
			content = ''
			total = 0
			if issues: 
				for line in issues:
					host = line['host'].encode("utf-8")
					tid = line['triggerid'].encode("utf-8")
					if (self.triggerhost_getstatus(host) != '1') and (self.trigger_getstatus(tid) != '1'):
						fdata = {'host':line['hostname'].encode("utf-8"),
						'description':line['description'].encode("utf-8")}
						res.append(fdata)
				total = len(res)
			content = str({"total":total,"rows":res})
			return content

	def triggerhost_getstatus(self,host):
		data = json.dumps({ 
		"jsonrpc":"2.0", 
		"method":"host.get", 
		"params": {
			"output": "extend",
			"filter": {
				"host": [
					host
				]
			}
		},
		"auth": self.user_login(), 
		"id":1 
		})
		request = urllib2.Request(self.url, data) 
		for key in self.header: 
			request.add_header(key, self.header[key]) 
		try: 
			result = urllib2.urlopen(request) 
		except URLError as e: 
			print "Error as ", e 
		else: 
			response = json.loads(result.read()) 
			result.close() 
			issues = response['result']
			if issues:
				status = issues[0]['status']
			return status

	def trigger_getstatus(self,tid):
		data = json.dumps({ 
		"jsonrpc": "2.0",
		"method": "trigger.get",
		"params": {
			"triggerids": tid,
			"output": "extend",
			"selectFunctions": "extend"
		},
		"auth": self.user_login(),
		"id": 1
		})
		request = urllib2.Request(self.url, data) 
		for key in self.header: 
			request.add_header(key, self.header[key]) 
		try: 
			result = urllib2.urlopen(request) 
		except URLError as e: 
			print "Error as ", e 
		else: 
			response = json.loads(result.read()) 
			result.close() 
			issues = response['result']
			if issues:
				status = issues[0]['status']
			return status

def getevents(dbhost,username,password,dbname,table,page,rows,sort,order,htf,htt,sname,stype,scontent,showfinish='false'):
	result = []
	res = []
	statement = ''
	findex = 0
	atcount = 0
	page = mysql.escape_string(page)
	rows = mysql.escape_string(rows)
	sort = mysql.escape_string(sort)
	order = mysql.escape_string(order)
	htf = mysql.escape_string(htf)
	htt = mysql.escape_string(htt)
	sname = mysql.escape_string(sname)
	stype = mysql.escape_string(stype)
	scontent = mysql.escape_string(scontent)
	showfinish = mysql.escape_string(showfinish)
	if showfinish == 'false':
		condition = 'where status <> 2'
	else:
		condition = 'where 1 = 1'
	statement = condition
	#É¸Ñ¡´®
	for fn in (htf,htt,scontent):
		if ((findex == 0 or findex == 1) and fn != ''):
			atcount += 1
			if (atcount == 2):
				condition = "time between '%s' and '%s'"%(htf,htt)
				statement = statement + ' and ' + condition
		if ((findex == 2) and fn != ''):
			if (stype == '0'):
				condition = "%s = '%s'"%(sname,scontent)
			else:
				condition = "%s like '%%%s%%'"%(sname,scontent)
			statement = statement + ' and ' + condition
		findex += 1
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "Select count(*) from %s %s"%(table,statement)
	cursor.execute(sql)
	data = cursor.fetchone()
	total = int(data[0])
	if page == '0':
		page = '1'
	if sort == '':
		sql = "Select * from %s %s order by time desc limit %s,%s"%(table,statement,str((int(page)-1)*int(rows)),rows)
	else:
		sql = "Select * from %s %s order by %s %s limit %s,%s"%(table,statement,sort,order,str((int(page)-1)*int(rows)),rows)
	cursor.execute(sql)
	data = cursor.fetchall()
	db.close()
	for m in data:
		fdata = {'did':str(m[1]),
		'hostname':m[2].encode("utf-8"),
		'description':m[3].encode("utf-8"),
		'time':m[4].encode("utf-8"),
		'status':str(m[5])}
		res.append(fdata)
	result = json.dumps({"total":total,"rows":res})
	return result

def ignoreevent(dbhost,username,password,dbname,table,id):
	id = mysql.escape_string(id)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "UPDATE %s SET status = 2 WHERE zeid = '%s'"%(table,id)
	cursor.execute(sql)
	sql = "UPDATE %s SET zeid = null where zeid = %s"%(table,id)
	cursor.execute(sql)
	db.commit()
	db.close()
	
def setstatusdoing(dbhost,username,password,dbname,table,id):
	id = mysql.escape_string(id)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "UPDATE %s SET status = 1 WHERE zeid = '%s'"%(table,id)
	cursor.execute(sql)
	db.commit()
	db.close()

def addzabbixjob(dbhost,username,password,dbname,table,jid,zeid):
	jid = mysql.escape_string(jid)
	zeid = mysql.escape_string(zeid)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "insert into %s (jid,zeid) values (%s,%s)"%(table,jid,zeid)
	cursor.execute(sql)
	db.commit()
	db.close()

def finzabbixjob(dbhost,username,password,dbname,ztable,zjtable,jid):
	jid = mysql.escape_string(jid)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	data = ''
	sql = "select zeid from %s where jid = '%s'"%(zjtable,jid)
	cursor.execute(sql)
	data = cursor.fetchall()
	if (len(data) != 0):
		sql = "UPDATE %s SET status = 2 WHERE zeid = '%s'"%(ztable,data[0][0])
		cursor.execute(sql)
		sql = "UPDATE %s SET zeid = null where zeid = %s"%(ztable,data[0][0])
		cursor.execute(sql)
		sql = "delete from %s where jid = %s"%(zjtable,jid)
		cursor.execute(sql)
		db.commit()
	db.close()

def delzfe(dbhost,username,password,dbname,table,rng,zfetime):
	rng = mysql.escape_string(rng)
	zfetime = mysql.escape_string(zfetime)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	if (rng == '0'):
		sql = "delete from %s where status = 2"%(table)
	elif (rng == '1'):
		sql = "delete from %s where status = 2 and time < '%s'"%(table,zfetime)
	cursor.execute(sql)
	db.commit()
	db.close()
	
if __name__ == "__main__": 
	address='http://172.16.240.250/zabbix'
	username='admin'
	password='1991jianke'
	zabbixapi = ZabbixAPI(address=address, username=username, password=password) 
	content = zabbixapi.trigger_get()
	print content