# -*- coding: UTF-8 -*-
import sys,modifystr,json,xlwt,StringIO,time
import MySQLdb as mysql
reload(sys) 
sys.setdefaultencoding('utf8')

def getsvrdata(loadtype,dbhost,username,password,dbname,table,page,rows,sort,order,stf,stt,sname,stype,scontent,nickname,role):
	result = []
	res = []
	sortsm = ''
	condition = ''
	findex = 0
	atcount = 0
	statement = "where (canedit like '%%[%s]%%' or canedit = '' or %s = 0)"%(nickname,role)
	sort = mysql.escape_string(sort)
	order = mysql.escape_string(order)
	sname = mysql.escape_string(sname)
	stype = mysql.escape_string(stype)
	scontent = mysql.escape_string(scontent)
	#生成筛选串
	for fn in (stf,stt,scontent):
		if ((findex == 0 or findex == 1) and fn != ''):
			atcount += 1
			if (atcount == 2):
				condition = "latime between '%s' and '%s'"%(stf,stt)
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
	if sort != '':
		sortsm = "order by %s %s"%(sort,order)	
	if loadtype == 'excel':
		page = 1
		rows = total
	sql = "Select * from %s %s %s limit %s,%s"%(table,statement,sortsm,str((int(page)-1)*int(rows)),rows)
	cursor.execute(sql)
	data = cursor.fetchall()
	db.close()
	for m in data:
		fdata = {'id':str(m[0]),
		'name':m[1].encode("utf-8"),
		'remarks':m[2].encode("utf-8"),
		'latime':m[3].encode("utf-8"),
		'canedit':m[4].encode("utf-8")}
		res.append(fdata)
	if loadtype != 'excel':
		result = json.dumps({"total":total,"rows":res})
	else:
		#生成excel格式
		wb=xlwt.Workbook(encoding='utf-8')
		borders = xlwt.Borders()
		borders.left = 1
		borders.right = 1
		borders.top = 1
		borders.bottom = 1
		borders.bottom_colour=0x3A 
		style = xlwt.XFStyle()
		style2 = xlwt.XFStyle()
		font = xlwt.Font()
		font2 = xlwt.Font()
		font.name = 'SimSun'
		font.height = 15*20
		font2.name = 'SimSun'
		font2.height = 10*20
		style.font = font
		style.borders = borders
		style2.font = font2
		style2.borders = borders
		ws=wb.add_sheet('数据',cell_overwrite_ok=True)
		ws.write(0,0,'ID',style)
		ws.write(0,1,'名称',style)
		ws.write(0,2,'备注',style)
		ws.write(0,3,'允许操作的用户',style)
		i = 1
		for data in res:
			ws.write(i,0,data['id'],style2)
			ws.write(i,1,data['name'],style2)
			ws.write(i,2,data['remarks'],style2)
			if data['canedit'] == '':
				ws.write(i,3,'所有人',style2)
			else:
				ws.write(i,3,data['canedit'],style2)
			i += 1
		ws.panes_frozen = True
		ws.horz_split_pos = 1
		ws.col(0).width = 0x0d00 + 10*100
		ws.col(1).width = 0x0d00 + 30*100
		ws.col(2).width = 0x0d00 + 100*100
		ws.col(3).width = 0x0d00 + 200*100
		sio = StringIO.StringIO()
		wb.save(sio)
		result = sio.getvalue()
	return result

def getserveraction(dbhost,username,password,dbname,table,id,page,rows,sort,order,atf,att,sname,stype,scontent):
	result = []
	res = []
	condition = ''
	statement = ''
	findex = 0
	atcount = 0
	id = mysql.escape_string(id)
	page = mysql.escape_string(page)
	rows = mysql.escape_string(rows)
	sort = mysql.escape_string(sort)
	order = mysql.escape_string(order)
	atf = mysql.escape_string(atf)
	att = mysql.escape_string(att)
	sname = mysql.escape_string(sname)
	stype = mysql.escape_string(stype)
	scontent = mysql.escape_string(scontent)
	#生成筛选串
	for fn in (atf,att,scontent):
		if ((findex == 0 or findex == 1) and fn != ''):
			atcount += 1
			if (atcount == 2):
				condition = "acttime between '%s' and '%s'"%(atf,att)
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
	sql = "Select count(*) from %s where serverid = '%s' %s"%(table,id,statement)
	cursor.execute(sql)
	data = cursor.fetchone()
	total = int(data[0])
	if page == '0':
		page = '1'
	if sort == '':
		sql = "Select * from %s where serverid = '%s' %s order by acttime desc limit %s,%s"%(table,id,statement,str((int(page)-1)*int(rows)),rows)
	else:
		sql = "Select * from %s where serverid = '%s' %s order by %s %s limit %s,%s"%(table,id,statement,sort,order,str((int(page)-1)*int(rows)),rows)
	cursor.execute(sql)
	data = cursor.fetchall()
	db.close()
	for m in data:
		fdata = {'id':str(m[0]),
		'action':m[2].encode("utf-8"),
		'actman':m[3].encode("utf-8"),
		'acttime':m[4].encode("utf-8")}
		res.append(fdata)
	result = json.dumps({"total":total,"rows":res})
	return result
	
def cesvr(dbhost,username,password,dbname,table,name,id):
	result = 'False'
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	name = mysql.escape_string(name)
	id = mysql.escape_string(id)
	cursor = db.cursor()
	sql = "Select count(*) from %s where (canedit like '%%[%s]%%' or canedit = '') and id = %s"%(table,name,id)
	cursor.execute(sql)
	data = cursor.fetchone()
	total = int(data[0])
	if total >= 1:
		result = 'True'
	db.commit()
	db.close()
	return result
	
def addserver(dbhost,username,password,dbname,table,svrname,remarks,onlyusers):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	svrname = mysql.escape_string(svrname)
	remarks = mysql.escape_string(remarks)
	onlyusers = mysql.escape_string(onlyusers)
	cursor = db.cursor()
	sql = "INSERT INTO %s (name,remarks,latime,canedit) VALUES ('%s','%s','%s','%s')"%(table,svrname,remarks,'',onlyusers)
	cursor.execute(sql)
	db.commit()
	db.close()

def changesvr(dbhost,username,password,dbname,table,id,svrname,remarks,onlyusers):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	id = mysql.escape_string(id)
	svrname = mysql.escape_string(svrname)
	remarks = mysql.escape_string(remarks)
	onlyusers = mysql.escape_string(onlyusers)
	cursor = db.cursor()
	sql = "UPDATE %s SET name='%s',remarks='%s',canedit='%s' where id = '%s'"%(table,svrname,remarks,onlyusers,id)
	cursor.execute(sql)
	db.commit()
	db.close()
	
def delsvr(dbhost,username,password,dbname,svrtable,svracttable,ids):
	serveridstr = ''
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	for id in ids:
		id = mysql.escape_string(id)
		serveridstr += id + ','
	serveridstr = serveridstr[:len(serveridstr) - 1]
	cursor = db.cursor()
	sql = "delete from %s where serverid in (%s)"%(svracttable,serveridstr)
	cursor.execute(sql)
	sql = "delete from %s where id in (%s)"%(svrtable,serveridstr)
	cursor.execute(sql)
	db.commit()
	db.close()
	
def addsvract(dbhost,username,password,dbname,stable,satable,serverid,name,svraction):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	curtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	serverid = mysql.escape_string(serverid)
	svraction = mysql.escape_string(svraction)
	cursor = db.cursor()
	sql = "INSERT INTO %s (serverid,action,actman,acttime) VALUES (%s,'%s','%s','%s')"%(satable,serverid,svraction,name,curtime)
	cursor.execute(sql)
	sql = "UPDATE %s SET latime='%s' where id = '%s'"%(stable,curtime,serverid)
	cursor.execute(sql)
	db.commit()
	db.close()
	
def delsvract(dbhost,username,password,dbname,table,id):
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	id = mysql.escape_string(id)
	cursor = db.cursor()
	sql = "delete from %s where id = %s"%(table,id)
	cursor.execute(sql)
	db.commit()
	db.close()

if __name__ == "__main__":
	print "test"