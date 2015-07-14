import sys, subprocess
sys.path.append('Y:/Nate/git/nuvosun-python-lib')
import nuvosunlib as nsl
from time import ctime

try:
    monitorStart = sys.argv[1]
except:
    monitorStart = True

tool = 'MC02'

sys.stdout = open('Y:/Nate/new MC02 OES program/backup from MC02 computer/data/OESbackupLogFile.txt','a+')
sys.stderr = open('Y:/Nate/new MC02 OES program/backup from MC02 computer/data/OESbackupErrFile.txt','a+')

print '\r\n\r\n***************************\r\n','starting backup check on ', ctime()

nsl.backupFiles('C:/OESdata/','Y:/Nate/new MC02 OES program/backup from MC02 computer/data/')

if monitorStart:
    subprocess.Popen(['python','C:/OESdata/check if tool sputtering.py',tool])