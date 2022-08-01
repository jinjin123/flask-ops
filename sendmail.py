#!/usr/bin/env python
# -*- coding: gbk -*-
import smtplib,mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#############
#要发给谁
mailto_list=["ouyangshan@jianke.com"]
#####################
#设置服务器，用户名、口令以及邮箱的后缀
mail_host="172.16.240.16"
mail_user="ouyangshan"
mail_pass="22454089"
mail_postfix="jianke.com"
######################
def send_mail(mailfrom,to_list,sub,content):
	'''
	to_list:发给谁
	sub:主题
	content:内容
	send_mail("aaa@126.com","sub","content")
	'''
	me = "hello"+"<"+mailfrom['user']+"@"+mailfrom['postfix']+">"
	msg = MIMEMultipart()
	msg['Subject'] = sub
	msg['From'] = me
	msg['To'] = ";".join(to_list)
	msgText = MIMEText(content,'plain','utf-8')
	msg.attach(msgText)   
	try:
		s = smtplib.SMTP()
		s.connect(mailfrom['host'])
		s.login(mailfrom['user'],mailfrom['pwd'])
		s.sendmail(me, to_list, msg.as_string())
		s.close()
		return True
	except Exception as e:
		print (str(e))
		return False
if __name__ == '__main__':
	mailfrom={'host':mail_host,'user':mail_user,'pwd':mail_pass,'postfix':mail_postfix}
	if send_mail(mailfrom,mailto_list,"subject","content"):
		print ("发送成功")
	else:
		print ("发送失败")
