import sys, os, glob, re
from datetime import datetime
sys.path.append("Y:/Nate/git/nuvosun-python-lib/")
import nuvosunlib as nsl


def getAllOESfolders(baseDataDir):
    '''
    Returns list of all folders in OES directory, baseDataDir.
    '''
    OESfolders = {}
    OESfiles = os.listdir(baseDataDir)
    for file in OESfiles:
        filePath = baseDataDir + file
        if os.path.isdir(filePath):
            OESfolders[file] = {}
            OESfolders[file]['path'] = filePath
            getRunNumber(filePath)
            OESstartDate = re.search('\d\d-\d\d-\d\d',folder).group(0)
            OESstartDate = datetime.datetime.strptime(OESstartDate, '%m-%d-%y')
    return OESfolders

def getRunNumber(filePath):
    '''
    Returns run number for a given OES file path.
    '''
    runDates = nsl.getRunDates()
    print sorted(runDates.keys())
    print sorted(runDates[runDates.keys()[0]].keys())
    
    OESfiles = os.listdir(filePath)
    for file in OESfiles:
        if re.search('1B',file):
            print 'detected \'1B\' in file ' + file + ', labeling BE'
            BEprocess = True
            PCprocess = False
            process = 'BE'
            tempZoneList = ['1B','2B','3B','4B']
        elif re.search('5A',file):
            print 'detected \'5A\' in file ' + file + ', labeling PC'
            PCprocess = True
            BEprocess = False
            process = 'PC'
            tempZoneList = ['5A','5B','6A','6B']
    # get run number from list of run dates
    dateMatched = False
    for run in runDates:
        if BEprocess:
            #print runDates[run]['BE date'], OESstartDate
            if runDates[run]['BE date'] == OESstartDate and runDates[run]['BE tool'] == tool:
                currentRun = run
                dateMatched = True
                print 'found run ' + run + ' on date ' + str(runDates[run]['BE date']) + ' matching OES start date of ' + str(OESstartDate)
        elif PCprocess:
            #print runDates[run]['PC date'], OESstartDate
            if runDates[run]['PC date'] == OESstartDate and runDates[run]['PC tool'] == tool:
                currentRun = run
                dateMatched = True
                print 'found run ' + run + ' on date ' + str(runDates[run]['PC date']) + ' matching OES start date of ' + str(OESstartDate)
    if not dateMatched:
        print 'no run date matched', folder
        return None
    # get list of actual zones measured
    zoneList = {}
    for zone in tempZoneList:
        ZfileSearch = '*' + zone + '*'
        fCount = 0
        for f in glob.iglob(filePath + '/' + ZfileSearch):
            zoneList[zone] = f
            fCount += 1
            if fCount>1:
                print currentRun, 'has more than 1 file'
                print 'files:'
                print os.listdir(filePath)
                print 'file path:', filePath
                exit()
                
    
    return currentRun, zoneList
            
def copyOESdata(savedir, runNum):
    '''
    Copies all files from OES directory, savedir, to experiment summaries folder on the shared drive.
    '''
    expBasepath = 'Y:/Experiment Summaries/Year ' + str(datetime.now().year) + '/'
    expRunPath = basepath + '\\' + 'S' + str(runNum).zfill(5) + '\\'
    expRunPath = basepath + '\\' + 'S' + str(runNum).zfill(5) + '\\' + tool + ' OES data' 
    for eachPath in [expBasepath,expRunPath,expOESpath]:
        if not os.path.exists(expRunPath):
            os.mkdir(expRunPath)
    nsl.backupFiles(savedir,expOESpath)


    

OESdir = 'Y:/Nate/new MC02 OES program/backup from MC02 computer/data/' # change to : 'Y:/Experiment Summaries/MC sputter tools OES/data/raw from tool'
OESfolders = getAllOESfolders(OESdir)
for key in sorted(OESfolders.keys()):
    currentRun, zoneList = getRunNumber(key)
    print currentRun