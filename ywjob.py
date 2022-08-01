# -*- coding: UTF-8 -*-
import sys,modifystr,json
import MySQLdb as mysql
reload(sys) 
sys.setdefaultencoding('utf8')

nametofield = {
'jobid':'id',
'jobstatus':'status',
'jobtype':'type',
'jobbt':'begintime',
'jobet':'endtime'
}

def getjobdata(dbhost,username,password,dbname,table,jmjobtable,page,rows,sort,order,btf,btt,etf,ett,status,type,othername,othertype,othercontent,ipaddr=""):
	result = []
	res = []
	condition = ''
	statement = ''
	findex = 0
	btcount = 0
	etcount = 0
	page = mysql.escape_string(page)
	rows = mysql.escape_string(rows)
	sort = mysql.escape_string(sort)
	order = mysql.escape_string(order)
	btf = mysql.escape_string(btf)
	btt = mysql.escape_string(btt)
	etf = mysql.escape_string(etf)
	ett = mysql.escape_string(ett)
	status = mysql.escape_string(status)
	type = mysql.escape_string(type)
	othername = mysql.escape_string(othername)
	othertype = mysql.escape_string(othertype)
	othercontent = mysql.escape_string(othercontent)
	#Éú³ÉÉ¸Ñ¡´®
	statement = 'where 1=1'
	for fn in (btf,btt,etf,ett,status,type,othercontent):
		if ((findex == 0 or findex == 1) and fn != ''):
			btcount += 1
			if (btcount == 2):
				condition = "begintime between '%s' and '%s'"%(btf,btt)
				statement = statement + ' and ' + condition
		if ((findex == 2 or findex == 3) and fn != ''):
			etcount += 1
			if (etcount == 2):
				condition = "endtime between '%s' and '%s'"%(etf,ett)
				statement = statement + ' and ' + condition
		if (findex >= 4 and fn != ''):
			if (findex == 4):
				condition = "status = %s"%(status)
			elif (findex == 5):
				condition = "type = %s"%(type)
			elif (findex == 6):
				if (othertype == '0'):
					condition = "%s = '%s'"%(othername,othercontent)
				else:
					condition = "%s like '%%%s%%'"%(othername,othercontent)
			statement = statement + ' and ' + condition
		findex += 1
	if ipaddr != "":
		condition = "%s.jobid = %s.id and %s.ipaddr = '%s'"%(jmjobtable,table,jmjobtable,ipaddr)
		statement = statement + ' and ' + condition
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	if ipaddr == "":
		sql = "Select count(*) from %s %s"%(table,statement)
	else:
		sql = "Select count(*) from %s,%s %s"%(table,jmjobtable,statement)
	cursor.execute(sql)
	data = cursor.fetchone()
	total = int(data[0])
	if page == '0':
		page = '1'
	if sort == '':
		if ipaddr == "":
			#sql = "Select * from %s %s order by status,type,begintime desc limit %s,%s"%(table,statement,str((int(page)-1)*int(rows)),rows)
			sql = "Select * from %s %s order by status,endtime desc limit %s,%s"%(table,statement,str((int(page)-1)*int(rows)),rows)
		else:
			#sql = "Select %s.* from %s,%s %s order by status,type,begintime desc limit %s,%s"%(table,table,jmjobtable,statement,str((int(page)-1)*int(rows)),rows)
			sql = "Select %s.* from %s,%s %s order by status,begintime desc limit %s,%s"%(table,table,jmjobtable,statement,str((int(page)-1)*int(rows)),rows)
	else:
		if ipaddr == "":
			sql = "Select * from %s %s order by %s %s limit %s,%s"%(table,statement,nametofield[sort],order,str((int(page)-1)*int(rows)),rows)
		else:
			sql = "Select %s.* from %s,%s %s order by %s %s limit %s,%s"%(table,table,jmjobtable,statement,nametofield[sort],order,str((int(page)-1)*int(rows)),rows)
	cursor.execute(sql)
	data = cursor.fetchall()
	db.close()
	for m in data:
		fdata = {'jobid':str(m[0]),
		'jobtype':str(m[1]),
		'jobtitle':m[2].encode("utf-8"),
		'jobbt':m[3].encode("utf-8"),
		'jobet':m[4].encode("utf-8"),
		'jobut':m[5].encode("utf-8"),
		'jobcman':m[6].encode("utf-8"),
		'jobman':m[7].encode("utf-8"),
		'jobstatus':str(m[8])}
		res.append(fdata)
	result = json.dumps({"total":total,"rows":res})
	return result

def getjobdatadetail(dbhost,username,password,dbname,table,id):
	result = []
	res = []
	id = mysql.escape_string(id)
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "Select * from %s where id = '%s'"%(table,id)
	cursor.execute(sql)
	data = cursor.fetchall()
	db.close()
	for m in data:
		fdata = {'jobcontent':m[1].encode("utf-8"),
		'jobcourse':m[2].encode("utf-8"),
		'jobtec':m[3].encode("utf-8"),
		'jobscore':str(m[4]),
		'jobcomment':m[5].encode("utf-8")}
		res.append(fdata)
	result = json.dumps({"rows":res})
	return result

if __name__ == "__main__":
	print "test"