import os
import fnmatch
from support import exportMessages  
from qip import parseQipHistory as Qip
from pidgin import parsePidginHistory as Pidgin
from miranda import parseMirandaHistory as Miranda
from mra import parseMraHistory as Mra

def checkType(path,mes):
    filename = path.split(os.sep)[-1]
    ext = filename.split('.')[-1]
    if (ext == 'html' or ext == 'txt') and fnmatch.fnmatch(filename,'????-??-??.?????*'):
        print '-=-=-'
        print path
        mes = Pidgin(path,mes)
    elif ext == 'qhf':
        print '-=-=-'
        print path
        mes = Qip(path,mes)
    elif ext == 'dbs':
        print '-=-=-'
        print path
        mes = Mra(path,mes)
    elif ext == 'qdb':
        print '-=-=-'
        print path
        print 'icq7.2' #icq7.2
    elif ext == 'dat':
        print '-=-=-'
        print path
        mes = Miranda(path,mes)
    return mes

def fileSearch(where):
    messages = []
    for root, dirnames, filenames in os.walk(where):
        for filename in filenames:
            checkType(os.path.join(root, filename),messages)
    return messages
    
messages = fileSearch(os.path.expanduser("~")+r'\AppData\Roaming')
if messages:
    exportMessages(messages)