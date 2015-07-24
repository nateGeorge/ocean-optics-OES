import sys, os, glob, re
from datetime import datetime
sys.path.append("Y:/Nate/git/nuvosun-python-lib/")
import nuvosunlib as nsl

runDates = nsl.getRunDates(bywebID = False)

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
            OESstartDate = re.search('\d\d-\d\d-\d\d', file).group(0)
            OESfolders[file]['start date'] = datetime.strptime(OESstartDate, '%m-%d-%y')
            if re.search('MC\d\d', file):
                tool = re.search('MC\d\d', file).group(0)
                OESfolders[file]['tool'] = tool
            else:
                tool = 'MC02'
                OESfolders[file]['tool'] = 'MC02'
            #getRunNumber(filePath, OESstartDate, tool)
    return OESfolders

def getRunNumber(filePath, OESstartDate, tool):
    '''
    Returns run number for a given OES file path.
    '''
    
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
            BEdates = []
            for key in runDates[run]['BE Run'].keys():
                if key != 'DW range':
                    BEdates.append(datetime.strftime(key,'%m-%d-%y'))
            #print BEdates, OESstartDate, runDates[run]['BE Tool'], tool
            if OESstartDate in runDates[run]['BE Run'].keys() and runDates[run]['BE Tool'] == tool:
                currentRun = run
                dateMatched = True
                print 'found run ' + run + ' on date ' + str(runDates[run]['BE Run'].keys()[1]) + ' matching OES start date of ' + str(OESstartDate)
        elif PCprocess:
            PCdates = []
            for key in runDates[run]['PC Run'].keys():
                if key != 'DW range':
                    PCdates.append(datetime.strftime(key,'%m-%d-%y'))
            #print PCdates, OESstartDate, runDates[run]['PC Tool'], tool
            if OESstartDate in runDates[run]['BE Run'].keys() and runDates[run]['PC Tool'] == tool:
                currentRun = run
                dateMatched = True
                print 'found run ' + run + ' on date ' + str(runDates[run]['PC Run'].keys()[1]) + ' matching OES start date of ' + str(OESstartDate)
    if not dateMatched:
        print 'no run date matched', filePath
        return None, None
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
for folder in sorted(OESfolders.keys()):
    currentRun, zoneList = getRunNumber(OESfolders[folder]['path'], OESfolders[folder]['start date'], OESfolders[folder]['tool'])
    print currentRun