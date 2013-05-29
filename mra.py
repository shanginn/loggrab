#-*- coding: utf-8 -*-
import struct
import datetime
from support import Message
from support import data_read


def FiletimeToDateTime(ftlo,fthi):
    timestamp = fthi
    timestamp <<= 32
    timestamp |= ftlo
    return datetime.datetime(1601, 1, 1, 0, 0, 0) + datetime.timedelta(microseconds=timestamp/10)

def find_mra_sign(where,start_offset):
    mra = [0x6D, 0x00, 0x72, 0x00, 0x61, 0x00, 0x68, 0x00, 0x69, 0x00, 0x73, 0x00, 0x74, 0x00, 0x6F, 0x00, 0x72, 0x00, 0x79, 0x00, 0x5F, 0x00]
    leng = len(mra)
    for j in range(leng):
        where.seek(start_offset+j)
        r = where.read(1)
        if struct.unpack('B', r)[0]!=mra[j]:
            #print hex(struct.unpack('B', r)[0])
            break
        if leng-1 == j:
            return start_offset
    return 0
def set_offset(__type):
    return 0x1C0 if __type == 'icq' else 0x194 if  __type == 'mra' else 0

def getMessage(_logFile,_offset,_db_type):
    # Заполняем структуру _message
    _size = data_read(_logFile,_offset,'DWORDl')         #unsigned int size;
    _offset+=4
    _prev_id = data_read(_logFile,_offset,'DWORDl')     #unsigned int prev_id;
    _offset+=4
    _next_id = data_read(_logFile,_offset,'DWORDl')     #unsigned int next_id;
    _offset+=4
    _xz1 = data_read(_logFile,_offset,'DWORDl')         #unsigned int xz1;
    _offset+=4
    _file_time = []                                     #FILETIME time;
    _file_time.append(data_read(_logFile,_offset,'DWORDl'))#DWORD dwLowDateTime;
    _offset+=4
    _file_time.append(data_read(_logFile,_offset,'DWORDl'))#DWORD dwHighDateTime;
    _offset+=4
    _type_message = data_read(_logFile,_offset,'DWORDl')#unsigned int type_message;
    _offset+=4
    _direction = 'out' if data_read(_logFile,_offset,'DWORDl') == 1 else 'in'#char flag_incoming;
    _offset+=4
    _count_nick = data_read(_logFile,_offset,'DWORDl')  #unsigned int count_nick;
    _offset+=4
    _magic_num = data_read(_logFile,_offset,'DWORDl')   #unsigned int magic_num; // 0x38
    _offset+=4
    _count_message = data_read(_logFile,_offset,'DWORDl')#unsigned int count_message; // именно количество, не размер в байтах
    _offset+=4
    _xz2 = data_read(_logFile,_offset,'DWORDl')         #unsigned int xz2; //
    _offset+=4 
    _size_lps_rtf = data_read(_logFile,_offset,'DWORDl')#unsigned int size_lps_rtf; // байт
    _offset+=4 
    _xz3 = data_read(_logFile,_offset,'DWORDl')         #unsigned int xz3; //
    _offset+=4
    if _db_type == 'icq':
        _xz4 = data_read(_logFile,_offset,'DWORDl')
        _offset+=8
    _date_time = str(FiletimeToDateTime(_file_time[0],_file_time[1])).split(' ')
    _date,_time = _date_time[0].replace('-','.'),_date_time[1].split('.')[0]
    _nick = u''
    for c in range(_count_nick-1): # Читаем ник
        _nick +=unichr(data_read(_logFile,_offset,'Wordl'))
        _offset += 2
    # Указатель теперь указывает на сообщение в unicode
    if data_read(_logFile,_offset,'Wordl') == 0 and _type_message == 0x11:
        _count_message = data_read(_logFile,_offset+1,'DWORDl')/2+1
        _offset += 3
    _text = u''
    for c in range(_count_message):
        _text += unichr(data_read(_logFile,_offset,'Wordl'))
        _offset+=2
    return _prev_id,_next_id,_date,_time,_direction,_text,_nick

def parseMraHistory(mra_file,messages):
    try:
        with open(mra_file,"rb") as logFile:
            offset_to_OT = data_read(logFile,0x10,'DWORDl') # OT - offset table
            end_id_mail = data_read(logFile,0x2C+data_read(logFile,offset_to_OT+4,'DWORDl'),'DWORDl') # Номер последнего емэйла в таблице оффсетов
            count_emails = data_read(logFile,0x20+data_read(logFile,offset_to_OT+4,'DWORDl'),'DWORDl') #Количество переписок
            db_type = '' 
            for i in range(count_emails):
                offset_end_mail = data_read(logFile,offset_to_OT+end_id_mail*4,'DWORDl') # оффсет до последнего мыла
                mail_data_id1,mail_data_id2 = data_read(logFile,offset_end_mail+4,'DWORDl'),data_read(logFile,offset_end_mail+8,'DWORDl')
                if find_mra_sign(logFile,offset_end_mail+0x1C0) and db_type == '':#если нашлась сигнатура mrahistory_
                    db_type = 'icq'
                elif find_mra_sign(logFile,offset_end_mail+0x194) and db_type == '':
                    db_type = 'mra'
                else:
                    pass
                    
                if find_mra_sign(logFile,offset_end_mail+set_offset(db_type)):
                    id1,id2 = data_read(logFile,offset_end_mail+4+0x24,'DWORDl'),data_read(logFile,offset_end_mail+8+0x24,'DWORDl')
                    logFile.seek(offset_end_mail+4+set_offset(db_type)+12) #Оффсет до ников(емэйлов)
                    splitUinLine = logFile.readline()[::2].split("\x00")[0].split("_") #Получаем UIN'ы
                    myUin,hisUin = splitUinLine[0],splitUinLine[1] 
                    id_message = id1
                    while id_message:
                        offset = data_read(logFile,offset_to_OT+4*id_message,'DWORDl')                   
                        prev_id,next_id,date,time,direction,text,nick = getMessage(logFile,offset,db_type)
                        messages.append(Message(myUin,hisUin,direction,text,date,time))
                        id_message=prev_id           
                end_id_mail = mail_data_id2
        return messages
    except:
            print 'File open fail'