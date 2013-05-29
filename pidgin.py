# -*- coding: utf-8 -*-
from support import Message
try:
    from lxml import etree
except ImportError:
    import xml.etree.cElementTree as etree
from os import sep

def parsePidginHistory(file_name,messages):   
    myUin = file_name.split(sep)[-3]
    hisUin = file_name.split(sep)[-2]
    nick = ''
    try:
        with open(file_name.split('logs')[0]+"accounts.xml") as xmlFile:
            xml = etree.parse(xmlFile) 
            root = xml.getroot()
            for account in root.findall('account'):
                if account.find('name').text == myUin and account.find('alias') is not None:
                    nick = account.find('name').text      
                if file_name.endswith(".txt"):
                    try:
                        with open(file_name) as log:
                            date = str(log.readline().split(' at ')[1].split(' on ')[0][0:-9])
                            for line in log:
                                if line[8]!=')':
                                    time = line[1:9]
                                else:
                                    time = line[1:8]
                                who = line.split(') ')[1].split(':')[0].strip() #Получаем uin\nick
                                if who == nick or who == myUin:
                                    direction = 'out'
                                else:
                                    direction = 'in'
                                text = line.split(who+":")[1].strip()
                                messages.append(Message(myUin,hisUin,direction,text,date,time))
                    except:
                        print 'File open fail'
                if file_name.endswith(".html"):
                    try:
                        with open(file_name) as log:
                            date = str(log.readline().split(' at ')[1].split(' on ')[0][0:-9])
                            for line in log:
                                if line.startswith('<font color="#16569E">') or line.startswith('<font color="#A82F2F">'):
                                    if line[46]!=')':
                                        time = line[38:45]
                                    else:
                                        time = line[38:46]
                                    if line.startswith('<font color="#16569E">'):
                                        direction = 'out'
                                        text = line.split('</b></font> ')[1][0:-6].replace('<br/>','\n')
                                    else:
                                        direction = 'in'
                                        text = line.split('</b></font> ')[1][6:-13]
                                    who = line.split('<b>')[1].split('</b>')[0].strip()[0:-1] #Получаем uin\nick  
                                    messages.append(Message(myUin,hisUin,direction,text,date,time))
                    except:
                        print 'File open fail'                  
                return messages
    except:
        return messages