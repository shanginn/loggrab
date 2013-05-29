#-*- coding: utf-8 -*-
from support import Message
from support import data_read
from support import UnixTimeToDataTime

def getHeader(_logFile):
    _offset=0
    _signature = ''
    try:
        for i in range(16):
            _signature += chr(data_read(_logFile,_offset,'Byte')[0])     # 'Miranda ICQ DB',0,26
            _offset+=1
    except:
        print 'Signature check fail'
        return 0
        
    if _signature == 'Miranda ICQ DB'+chr(0)+chr(26):
        _version = data_read(_logFile,_offset,'DWORDl')        #as 4 bytes, ie 1.2.3.10=0x0102030a
        _offset+=4
        _ofsFileEnd = data_read(_logFile,_offset,'DWORDl')     #оффсет до конца файла
        _offset+=4
        _slackSpace = data_read(_logFile,_offset,'DWORDl')    #a counter of the number of bytes that have been
                                                            #wasted so far due to deleting structures and/or
                                                            #re-making them at the end. We should compact when
                                                            #this gets above a threshold
        _offset+=4
        _contactCount = data_read(_logFile,_offset,'DWORDl')  #количество контактов в цепочке, исключая пользрвателя
        _offset+=4
        _ofsFirstContact = data_read(_logFile,_offset,'DWORDl')#оффсет до первой структуры DBContact в цепочке
        _offset+=4
        _ofsUser = data_read(_logFile,_offset,'DWORDl')       #оффсет до структуры DBContact представляющей пользователя
        _offset+=4
        _ofsFirstModuleName = data_read(_logFile,_offset,'DWORDl')#оффсет до первой структуры DBModuleName в цепочке
        #print 'header:', _signature,hex(_version),hex(_ofsFileEnd),_slackSpace,_contactCount,hex(_ofsFirstContact),hex(_ofsUser),hex(_ofsFirstModuleName)
        return _signature,_version,_ofsFileEnd,_slackSpace,_contactCount,_ofsFirstContact,_ofsUser,_ofsFirstModuleName
    else:
        print 'Signature check fail'
        return 0

def getContact(_logFile,_offset):
    _csignature = data_read(_logFile,_offset,'DWORDl')         #0x43DECADE
    _offset+=4
    _ofsNextContact = data_read(_logFile,_offset,'DWORDl')     #оффсет до следующего пользователя в цепочке, 0 если
                                                            #это контакт пользователя или последний котакт в цепочке
    _offset+=4
    _ofsFirstSettings = data_read(_logFile,_offset,'DWORDl')   #оффсет до первой DBContactSettings в
                                                            #цепочке для этого контакта
    _offset+=4
    _eventCount = data_read(_logFile,_offset,'DWORDl')         #количество событий для этого контакта
    _offset+=4
    _ofsFirstEvent = data_read(_logFile,_offset,'DWORDl')      #оффсет до первого и последнего DBEvent в
                                                            #цеопчке для этого контакта
    _offset+=4
    _ofsLastEvent = data_read(_logFile,_offset,'DWORDl')
    _offset+=4
    _ofsFirstUnreadEvent = data_read(_logFile,_offset,'DWORDl')#оффсет до первого(хронологически) непрочитоннаго 
                                                            #события в цепи, 0 если все прочитаны
    _offset+=4
    _timestampFirstUnread = data_read(_logFile,_offset,'DWORDl')#timestamp of the event at ofsFirstUnreadEvent
    #print 'contact: ', hex(csignature),hex(ofsNextContact),hex(ofsFirstSettings),eventCount,hex(ofsFirstEvent),hex(ofsLastEvent),hex(ofsFirstUnreadEvent),timestampFirstUnread
    return _csignature,_ofsNextContact,_ofsFirstSettings,_eventCount,_ofsFirstEvent,_ofsLastEvent,_ofsFirstUnreadEvent,_timestampFirstUnread

def getUinFromSettings(_logFile,_offset):
    while True:
        #DBContactSettings
        #В этих структурах ищем UIN контакта
        _ssignature = data_read(_logFile,_offset,'DWORDl')
        _offset+=4
        _ofsNextSettings = data_read(_logFile,_offset,'DWORDl')
        _offset+=4
        _ofsModuleName = data_read(_logFile,_offset,'DWORDl')
        _offset+=4
        _cbBlob = data_read(_logFile,_offset,'DWORDl')
        _offset+=4
        _blob = ''
        for b in range(_cbBlob):
            _blob+=chr(data_read(_logFile,_offset,'Byte')[0])
            _offset+=1
        if _blob.find('UIN') != -1:
            _offset = _offset-_cbBlob+_blob.find('UIN')+4
            _uin = data_read(_logFile,_offset,'DWORDl')
            break
        if not _ofsNextSettings:
            break
        _offset = _ofsNextSettings
    return _uin#_ssignature,_ofsNextSettings,_ofsModuleName,_cbBlob,_blob,_uin

def getEvent(_logFile,_offset):
    _esignature = data_read(_logFile,_offset,'DWORDl')     #0x45DECADE
    _offset+=4
    _ofsPrev = data_read(_logFile,_offset,'DWORDl')        #оффсет до предыдущего и следующего сообщения в
                                                        #цепочке. Цепочка отсортированная хронологически
    _offset+=4
    _ofsNext = data_read(_logFile,_offset,'DWORDl')
    _offset+=4
    _ofsModuleName = data_read(_logFile,_offset,'DWORDl')  #оффсет до структуры DBModuleName имени владельца события
    _offset+=4
    _timestamp = UnixTimeToDataTime(data_read(_logFile,_offset,'DWORDl'))      #секунд с 00:00:00 01/01/1970
    _offset+=4
    _flags = data_read(_logFile,_offset,'DWORDl')
    _i=4
    _flag = [0,0,0,0,0]                                  #Флаги
    for f in bin(_flags).split('b')[1][::-1]:            #1: первое сообщение в цепочке;
        _flag[_i]=int(f)                                  #   только для внутреннего использования: *do not* use this flag
        _i-=1                                            #2: событие отправленно пользователем
                                                        #   если не установлен - событие получено пользователем
                                                        #4: событие прочитано пользователем. It does not need
                                                        #   to be processed any more except for history.
                                                        #8: событие содержит текст, написанный справа налево
                                                        #16:событие содержит текст в utf-8
    _offset+=4
    _eventType = data_read(_logFile,_offset,'Wordl')       #module-defined event type
    _offset+=2
    _direction = 'out' if _flag[3] else 'in'
    _cbBlob = data_read(_logFile,_offset,'DWORDl') if _flag[0] else data_read(_logFile,_offset,'DWORDl')/3  #number of bytes in the blob
    _offset+=4 
    _text = ''
    for b in range(_cbBlob):
        _text += chr(data_read(_logFile,_offset,'Byte')[0])#the blob. module-defined formatting
        _offset+=1
    #print 'event: ', hex(esignature),hex(ofsPrev),hex(ofsNext),hex(ofsModuleName),timestamp,flag,hex(eventType),cbBlob,text,
    return _esignature,_ofsPrev,_ofsNext,_ofsModuleName,_timestamp,_flag,_eventType,_direction,_text
    
def parseMirandaHistory(miranda_file,_messages):    
    try:
        with open(miranda_file,'rb') as logFile:
            header = getHeader(logFile)
            if header:
                signature,version,ofsFileEnd,slackSpace,contactCount,ofsFirstContact,ofsUser,ofsFirstModuleName = header
            else:
                return _messages
            csignature,ofsNextContact,ofsFirstSettings,eventCount,ofsFirstEvent,ofsLastEvent,ofsFirstUnreadEvent,timestampFirstUnread = getContact(logFile,ofsUser)
            myUin = getUinFromSettings(logFile,ofsFirstSettings)
            #все контакты
            offset = ofsFirstContact
            for contact in range(contactCount):
                csignature,ofsNextContact,ofsFirstSettings,eventCount,ofsFirstEvent,ofsLastEvent,ofsFirstUnreadEvent,timestampFirstUnread = getContact(logFile,offset)
                #print '('+ str(contact) + ')','contact: ', hex(csignature),hex(ofsNextContact),hex(ofsFirstSettings),eventCount,hex(ofsFirstEvent),hex(ofsLastEvent),hex(ofsFirstUnreadEvent),timestampFirstUnread
                offset = ofsFirstSettings
                hisUin = getUinFromSettings(logFile,ofsFirstSettings)
                if eventCount:
                    offset = ofsFirstEvent
                    for event in range(eventCount):
                        esignature,ofsPrev,ofsNext,ofsModuleName,timestamp,flag,eventType,direction,text = getEvent(logFile,offset)
                        """
                        #DB Module Name
                        offset = ofsModuleName
                        msignature = data_read(logFile,offset,'DWORDl')     #0x4DDECADE
                        offset+=4
                        ofsNextModule = data_read(logFile,offset,'DWORDl')  #offset to the next module name in the chain
                        offset+=4
                        cbBlobModule = data_read(logFile,offset,'Byte')[0]  #number of characters in this module name
                        offset+=1
                        blobModule = ''
                        for b in range(cbBlobModule):                       #name, no nul terminator
                            blobModule += chr(data_read(logFile,offset,'Byte')[0])
                            offset+=1
                        myNick = blobModule
                        """
                        offset = ofsNext
                        _messages.append(Message(myUin,hisUin,direction,text,timestamp[0],timestamp[1]))
                offset = ofsNextContact
            return _messages
    except:
        print 'File open fail'
        return _messages