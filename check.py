#!/usr/bin/env python3
import psutil
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
botpid = -1

def check_bot_on():
    return botpid != -1 and psutil.pid_exists(botpid)

def loadpid():
    try:
        with open('pid.txt', 'r') as fr:
            global botpid
            lpid, botpid = botpid, int(fr.read().strip())
            print('1' if check_bot_on() else 'PID Loaded [%d --> %d]' % (lpid, botpid))
    except Exception as ex:
        print('No PID file found.')

loadpid()
