import sys, subprocess, os, re
sys.path.append('Y:/Nate/git/nuvosun-python-lib')
import nuvosunlib as nsl
from time import ctime

try:
    monitorStart = sys.argv[1]
except:
    monitorStart = True

files = os.listdir('C:/OESdata')
for file in files:
    if re.search('MC\d\d.txt',file):
        tool = file[:4]

sys.stdout = open('Y:/Nate/new MC02 OES program/backup from MC02 computer/data/OESbackupLogFile.txt','a+')
sys.stderr = open('Y:/Nate/new MC02 OES program/backup from MC02 computer/data/OESbackupErrFile.txt','a+')

print '\r\n\r\n***************************\r\n','starting backup check on ', ctime()

nsl.backupFiles('C:/OESdata/','Y:/Nate/new MC02 OES program/backup from MC02 computer/data/')

if monitorStart:
    subprocess.Popen(['python','C:/OESdata/check if tool sputtering.py',tool])