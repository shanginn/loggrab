# -*- coding: utf-8 -*-
import sqlite3 as lite
import struct
import os
import datetime


class Message:
    def __init__(self,myUin,hisUin,direction,text,date,time):
        self.myUin=myUin
        self.hisUin=hisUin
        self.text=text
        self.date=date
        self.time=time
        self.direction=direction
    def printMessage(self):
        if self.direction == 'out':
            print self.date +"\\("+ str(self.time) +") " + str(self.myUin) + ": " + self.text.strip()
        else:
            print self.date +"\\("+ str(self.time)+") " + str(self.hisUin) + ": " + self.text.strip() 

def exportMessages(messages):
    connect = lite.connect(str(messages[0].myUin)+".db")
    cursor = connect.cursor()
    for i,message in enumerate(messages):
        if i>0 and message.myUin != messages[i-1].myUin:
            connect.commit()
            connect.close()
            connect = lite.connect(str(message.myUin)+".db")
            cursor = connect.cursor()
        # Создаем таблицу _UIN, т.к. имя таблицы не может полностью состоять из цифр
        cursor.execute("CREATE TABLE IF NOT EXISTS _"+str(message.hisUin)+" (direction text,text text,date text,time text)")
        insert = "INSERT INTO _"+str(message.hisUin)+" VALUES (?,?,?,?)"
        message.printMessage()
        cursor.execute(insert,(message.direction,message.text.decode('utf-8'),message.date.decode('utf-8'),message.time))
    connect.commit()
    connect.close()
        
def importMessages(database):
    retMessages = []
    myUin = database.split(os.sep)[-1][-4::-1][::-1]
    connect = lite.connect(database)
    cursor = connect.cursor()
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    for table in tables:
        table = table[0]
        hisUin = table
        messages = cursor.execute("SELECT * FROM "+table).fetchall()
        for message in messages:
            retMessages.append(Message(myUin,hisUin[1::],message[0],message[1],message[2],message[3]))
    return retMessages

def data_read(from_file, offset, data_type, size=1):
    from_file.seek(offset)
    if data_type == 'Char':
        return from_file.read(size)
    elif data_type == 'Byte':
        result = ()
        for i in range(size):
            result += struct.unpack('B', from_file.read(1))
        return result
    elif data_type == 'Word':
        size = 2
        return struct.unpack('>H', from_file.read(size))[0]
    elif data_type == 'Wordl':
        size = 2
        return struct.unpack('<H', from_file.read(size))[0]
    elif data_type == 'DWORD':
        size = 4
        return struct.unpack('>I', from_file.read(size))[0]
    elif data_type == 'DWORDl':
        size = 4
        return struct.unpack('<I', from_file.read(size))[0]


def UnixTimeToDataTime(unixtime):
    data = datetime.datetime.fromtimestamp(unixtime).strftime('%Y.%m.%d')
    time = datetime.datetime.fromtimestamp(unixtime).strftime('%H:%M:%S')
    return data,time