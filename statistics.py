# -*- coding: UTF-8 -*-
import sys,modifystr,json,datetime,xlwt,StringIO
import MySQLdb as mysql
reload(sys) 
sys.setdefaultencoding('utf8')

def jobstat(loadtype,dbhost,username,password,dbname,jobtable,jobdtable,page,rows,sort,order,ftimef,ftimet,ftype):
	result = []
	res = []
	names = []
	finjobs = []
	totaltime = []
	avgtime = []
	totalscore = []
	avgscore = []
	rs = ''
	rd = ''
	condition = ''
	statement = ''
	findex = 0
	tcount = 0
	page = mysql.escape_string(page)
	rows = mysql.escape_string(rows)
	sort = mysql.escape_string(sort)
	order = mysql.escape_string(order)
	ftimef = mysql.escape_string(ftimef)
	ftimet = mysql.escape_string(ftimet)
	ftype = mysql.escape_string(ftype)
	for fn in (ftimef,ftimet,ftype):
		if ((findex == 0 or findex == 1) and fn != ''):
			tcount += 1
			if (tcount == 2):
				condition = "%s.begintime between '%s' and '%s'"%(jobtable,ftimef,ftimet)
				statement = statement + ' and ' + condition
		if (findex == 2 and fn != ''):
			condition = "%s.type = %s"%(jobtable,ftype)
			statement = statement + ' and ' + condition
		findex += 1
	db = mysql.connect(user=username, passwd=password, \
		db=dbname, host=dbhost, charset="utf8")
	cursor = db.cursor()
	sql = "select %s.jobman,%s.usetime,%s.score from %s,%s where %s.id = %s.id and %s.status = 2 %s" \
	%(jobtable,jobtable,jobdtable,jobtable,jobdtable,jobtable,jobdtable,jobtable,statement)
	cursor.execute(sql)
	data = cursor.fetchall()
	db.close()
	for m in data:
		if m[0] not in names:
			names.append(m[0])
			finjobs.append(0)
			totaltime.append(datetime.timedelta())
			totalscore.append(0)
			avgtime.append(datetime.timedelta())
			avgscore.append(0)
		for i in range(len(names)):
			if (names[i] == m[0]):
				finjobs[i] += 1
				if 'days' in m[1]:
					dt = m[1].split(' days, ')
					day = dt[0]
					time = dt[1].split(':')
				elif 'day' in m[1]:
					dt = m[1].split(' day, ')
					day = dt[0]
					time = dt[1].split(':')
				else:
					day = 0
					time = m[1].split(':')
				hour = time[0]
				minute = time[1]
				second = time[2]
				totaltime[i] += datetime.timedelta(days=int(day),hours=int(hour),minutes=int(minute),seconds=int(second))
				totalscore[i] += int(m[2])
	for i in range(len(names)):
		avgtime[i] = str(totaltime[i] / finjobs[i])
		if '.' in avgtime[i]:
			avgtime[i] = avgtime[i].split('.')[0]
		totaltime[i] = str(totaltime[i])
		avgscore[i] = totalscore[i] / finjobs[i]
		fdata = {'name':names[i].encode("utf-8"),
		'finjobs':finjobs[i],
		'totaltime':totaltime[i].encode("utf-8"),
		'avgtime':avgtime[i].encode("utf-8"),
		'totalscore':totalscore[i],
		'avgscore':avgscore[i]}
		res.append(fdata)
	total = len(res)
	if sort == '':
		res = sorted(res, key=lambda x:x['finjobs'],reverse=1)
	else:
		if order == 'asc':
			res = sorted(res, key=lambda x:x[sort])
		else:
			res = sorted(res, key=lambda x:x[sort],reverse=1)
	if page == '0':
		page = '1'
	if loadtype == 'excel':
		page = 1
		rows = total
	rs = (int(page)-1)*int(rows)
	rd = rs + int(rows)
	res = res[rs:rd]
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
		ws=wb.add_sheet('统计',cell_overwrite_ok=True)
		ws.write(0,0,'姓名',style)
		ws.write(0,1,'完成事务数',style)
		ws.write(0,2,'总耗时',style)
		ws.write(0,3,'平均耗时',style)
		ws.write(0,4,'总评分',style)
		ws.write(0,5,'平均评分',style)
		i = 1
		for data in res:
			ws.write(i,0,data['name'],style2)
			ws.write(i,1,data['finjobs'],style2)
			ws.write(i,2,data['totaltime'],style2)
			ws.write(i,3,data['avgtime'],style2)
			ws.write(i,4,data['totalscore'],style2)
			ws.write(i,5,data['avgscore'],style2)
			i += 1
		ws.panes_frozen = True
		ws.horz_split_pos = 1
		ws.col(0).width = 0x0d00 + 15*100
		ws.col(1).width = 0x0d00 + 5*100
		ws.col(2).width = 0x0d00 + 15*100
		ws.col(3).width = 0x0d00 + 10*100
		ws.col(4).width = 0x0d00 + 5*100
		ws.col(5).width = 0x0d00 + 5*100
		sio = StringIO.StringIO()
		wb.save(sio)
		result = sio.getvalue()
	return result

if __name__ == "__main__":
	print "test"