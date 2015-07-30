import csv, os, sys, re, glob, dateutil.parser, time
from datetime import datetime
import pickle as pkl
sys.path.append('Y:/Nate/git/nuvosun-python-lib')
import nuvosunlib as nsl
# since I have to run from the C: drive now, need to change folders into the file directory for storage files
os.chdir(os.path.dirname(os.path.realpath(__file__))) 

def getRunNumber(filePath, OESstartDate, tool):
    '''
    Returns run number for a given OES file path.
    '''
    runDates = nsl.getRunDates(bywebID = False)
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
        return None, None, False
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
                
    
    return currentRun, zoneList, dateMatched

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

startTime = time.time()

useLogFile = True # will write everything to the logfile instead of to console

basePath = 'Y:/Nate/OES/databases/'
OESdbFile = basePath + 'all OES data.csv'

logFile = open(basePath + 'add OES to db logfile.txt','a')

sys.stdout = logFile
sys.stderr = logFile

print ''
print ''
print '*******************************************************'
print '*******************************************************'
print 'starting db addition on', str(datetime.now())

tool = 'MC02'

# since wavelengths are always the same, just need to load them once
haveWavelengths = False

runDates = nsl.getRunDates()

baseOESdataPath = 'Y:/Nate/new MC02 OES program/backup from MC02 computer/data/'

OESfolders = getAllOESfolders(baseOESdataPath)

# check which data is already in database file
isWLrow = True
runsInDBdict = {}
runsInDB = []
runDatesInDB = []
runsInDBFile = basePath + 'runsInDB.pkl'
latestModDateFile = basePath + 'DBlatestMod.pkl'

if os.path.isfile(latestModDateFile):
    latestDBmodDate = os.path.getmtime(OESdbFile)
    with open(latestModDateFile) as pklFile:
        prevDBmodDate = pkl.load(pklFile)
    if latestDBmodDate == prevDBmodDate:
        DBrunListUptoDate = True
    else:
        DBrunListUptoDate = False
        with open(latestModDateFile,'wb') as pklFile:
            pkl.dump(latestDBmodDate, pklFile)

noLabelRow = True # used later to determine if need to write label row is csv database
if os.path.isfile(OESdbFile):
    print 'getting runs already in DB...'
    OESreader = csv.reader(open(OESdbFile,'rb'), delimiter =',')
    for row in OESreader:
        if not isWLrow:
            currentRunNumber = int(re.search('0*(\d\d\d)',row[1]).group(1))
            if currentRunNumber not in runsInDB:
                runsInDB.append(currentRunNumber)
                fullOESstartDT = datetime.fromtimestamp(float(row[4])).strftime('%m-%d-%y')
                oldOESstartDate = datetime.strptime(fullOESstartDT,'%m-%d-%y')
                runDatesInDB.append(oldOESstartDate)
                runsInDBdict[currentRunNumber] = {}
                runsInDBdict[currentRunNumber]['start date'] = oldOESstartDate
        else:
            isWLrow = False
            pass
print 'finished getting runs already in db'

if len(runsInDB)>0:
    noLabelRow = False
    with open(runsInDBFile,'wb') as pklFile:
        pkl.dump(runsInDB, pklFile)
else:
    for file in [OESdbFile, latestModDateFile, runsInDBFile]:
        if os.path.isfile(file):
            os.remove(file)

print sorted(runsInDB)

csvDataWriter = csv.writer(open(OESdbFile,'a'), delimiter = ',')
for folder in sorted(OESfolders.keys()):
    print ''
    print 'processing', OESfolders[folder]['path']
    # get date of run and convert to datetime--don't think I need this anymore
    if OESfolders[folder]['start date'] in runDatesInDB:
        print 'run date', OESfolders[folder]['start date'], 'already in OES database, skipping folder', folder
        continue
    currentRun, zoneList, dateMatched = getRunNumber(OESfolders[folder]['path'], OESfolders[folder]['start date'], OESfolders[folder]['tool'])
    if not dateMatched:
        print 'no run date matched', folder
        continue
    # load raw OES spectra
    ZoneOESdata = {}
    ZoneOESdates = {}
    for zone in zoneList:
        ZfileSearch = '*' + zone + '*'
        for f in glob.iglob(ZfileSearch):
            Zfile = f

        ZOESCSV = csv.reader(open(Zfile,'rb'), delimiter=',')

        firstRow = True
        ZoneOESdata[zone] = []
        ZoneOESdates[zone] = []
        for row in ZOESCSV:
            if not firstRow:
                #ZoneOESdata[zone].append(row[1:])
                #ZoneOESdates[zone].append((dateutil.parser.parse(row[0])-datetime.datetime(1970,1,1)).total_seconds())
                currentDatetime = (dateutil.parser.parse(row[0])-datetime(1970,1,1)).total_seconds()
                currentData = row[1:]
                csvDataWriter.writerow([tool,currentRun,process,zone,currentDatetime] + currentData)
                
                #cur.execute('INSERT INTO TABLE OESspectra VALUES(%s)', [tool, currentRun, process, zone, currentDatetime, currentData]) % '?,'*(5+len(wl))[:-1]
            else:
                firstRow = False
                if not haveWavelengths:
                    wl = row[1:]
                    haveWavelengths = True
                    if noLabelRow:
                        csvDataWriter.writerow(['tool','substrate','process','zone','datetime'] + wl)
                    '''print "CREATE TABLE IF NOT EXISTS OESspectra (tool TEXT, substrate INT, process TEXT, zone TEXT, datetime TEXT, %s)" % (' REAL, '.join('wl' + str(i) for i in range(len(wl)-2040)) + ' REAL')
                    exStr = "CREATE TABLE IF NOT EXISTS OESspectra (tool TEXT, substrate INT, process TEXT, zone TEXT, datetime TEXT, %s)" % (' REAL, '.join('wl' + str(i) for i in range(len(wl))) + ' REAL')
                    cur.execute(exStr)
                    cur.execute("CREATE TABLE IF NOT EXISTS OESwavelengths (%s)") % (' REAL, '.join(str(i) for i in range(len(wl))) + ' REAL')
                    cur.execute("INSERT INTO OESwavelengths VALUES (%s)",wl) % '?,'*(len(wl))[:-1]'''
                    
endTime = time.time()

print 'took', endTime - startTime, 'seconds'
print 'or', (endTime - startTime)/60, 'minutes'