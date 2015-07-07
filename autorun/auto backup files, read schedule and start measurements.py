import sys
sys.path.append('Y:/Nate/git/nuvosun-python-lib')
import nuvosunlib as nsl
from time import ctime

sys.stdout = open('Y:/Nate/new MC02 OES program/backup from MC02 computer/data/OESbackupLogFile.txt','a+')
sys.stderr = open('Y:/Nate/new MC02 OES program/backup from MC02 computer/data/OESbackupErrFile.txt','a+')

print '\r\n\r\n***************************\r\n','starting backup check on ', ctime()

nsl.backupFiles('C:/OESdata/','Y:/Nate/new MC02 OES program/backup from MC02 computer/data/')