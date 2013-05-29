# -*- coding: utf-8 -*-


from support import data_read 
from support import UnixTimeToDataTime
from support import Message
from os import sep
def msg_decrypt(bytes_tuple):
    k = 1
    message = ''
    for char in bytes_tuple:
        d_char = ((char^255)-k) & 255
        message += chr(d_char)
        k+=1
        if k>256:
            k=1
    return message.decode('utf-8')

def get_messages(_qhf_file,_offset,_messages_count,_version,_myUin,_hisUin,messages):
    for i in range(_messages_count):
        dt = UnixTimeToDataTime(data_read(_qhf_file, _offset+0x12, 'DWORD'))
        data_read(_qhf_file, _offset+0x1a, 'Byte')[0]
        direction = 'out' if data_read(_qhf_file, _offset+0x1a, 'Byte')[0]!=0 else 'in'
        if _version == 3:
            message_size_type = 'DWORD'
            message_text_offset = 0x23
        else:
            message_size_type = 'Word'
            message_text_offset = 0x21
        message_size = data_read(_qhf_file, _offset+0x1f, message_size_type)
        crypt_message_text = data_read(_qhf_file, _offset+message_text_offset, 'Byte', message_size)
        text = msg_decrypt(crypt_message_text)   
        message = Message(_myUin,_hisUin,direction,text,dt[0],dt[1])
        messages.append(message)
        _offset = _offset+0x23+message_size
    return messages

def parseQipHistory(file_name,messages):
    myUin = file_name.split(sep)[-3]
    try:
        with open(file_name, 'rb') as qhf_file:
            signature = data_read(qhf_file, 0x00, 'Char', 3)
            if not signature == 'QHF':
                print 'File type error'
                return messages
            version = data_read(qhf_file, 0x03, 'Byte')[0]
            if version not in [1, 2, 3]:
                print 'History version error'
                return messages
            _messages_count = data_read(qhf_file, 0x22, 'DWORD')
            _messages_count_check = data_read(qhf_file, 0x26, 'DWORD')
            if _messages_count == _messages_count_check:
                messages_count = _messages_count
            else:
                print 'History read error'
                return messages
            uin_len = data_read(qhf_file, 0x2c, 'Word')
            hisUin = data_read(qhf_file, 0x2e, 'Char', uin_len)
            nickname_len = data_read(qhf_file, 0x2e+uin_len, 'Word')
            nickname = data_read(qhf_file, 0x2e+uin_len+2, 'Char', nickname_len)
            header_size = 0x2e+uin_len+2+nickname_len
            return get_messages(qhf_file,header_size,messages_count,version,myUin,hisUin,messages)
    except:
            print 'File open fail'
            return messages