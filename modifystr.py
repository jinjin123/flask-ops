#!/usr/bin/python
# -*- coding: utf-8 -*-
import re,os,sys,hashlib
reload(sys) 
sys.setdefaultencoding('utf8')

def removesymbol(string):
    rsstring = re.sub("[\s+\\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+", "",string)
    return rsstring

def md5(str):
	m = hashlib.md5()   
	m.update(str)
	return m.hexdigest()
	
if __name__ == "__main__":
    temp = "test!@#test"
    string = removesymbol(temp)
    print (string)
