#-*- coding:utf-8 -*-
import os

def listyourdir(level, path):
    for i in os.listdir(path):
        if os.path.isfile(path + os.sep + i) and i[-2:] == 'py':
          addEncoding(path + os.sep + i)
            
        elif os.path.isdir(path + os.sep + i):
            listyourdir(level + 1, path + os.sep +i)

def addEncoding(filename):
    f = open(filename, 'r')
    content = f.read()
    f.close()
    new = open(filename, 'w')
    newContent = "#-*- coding:utf-8 -*-\n" + content
    new.write(newContent)
    new.close()

if __name__ == '__main__':
    listyourdir(0,
            os.path.abspath('.'))
