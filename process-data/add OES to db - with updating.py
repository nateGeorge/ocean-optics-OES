import csv, os, sys, re, datetime, glob, dateutil.parser, time
sys.path.append('Y:/Nate/git/nuvosun-python-lib')
import nuvosunlib as nsl

# since I have to run from the C: drive now, need to change folders into the file directory for storage files
os.chdir(os.path.dirname(os.path.realpath(__file__))) 

'''import sqlite3

con = sqlite3.connect('dbname=allOESdata user=postgres')

cur = con.cursor()'''
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
print 'starting db addition on', str(datetime.datetime.now())

tool = 'MC02'

# since wavelengths are always the same, just need to load them once
haveWavelengths = False

runDates = nsl.getRunDates()

baseOESdataPath = 'Y:/Nate/new MC02 OES program/backup from MC02 computer/data/'
	
# get list of OES runs:
folders = os.listdir(baseOESdataPath)

print 'using folders:'
for folder in folders:
	print folder

# check which data is already in database file




isWLrow = True
runsInDBdict = {}
runsInDB = []
runDatesInDB = []

noLabelRow = True # used later to determine if need to write label row is csv database
if os.path.isfile(OESdbFile):
	print 'getting runs already in DB...'
	OESreader = csv.reader(open(OESdbFile,'rb'), delimiter =',')
	for row in OESreader:
		if not isWLrow:
			currentRunNumber = int(re.search('00(\d\d\d)',row[1]).group(1))
			if currentRunNumber not in runsInDB:
				runsInDB.append(currentRunNumber)
				fullOESstartDT = datetime.datetime.fromtimestamp(float(row[4])).strftime('%m-%d-%y')
				oldOESstartDate = datetime.datetime.strptime(fullOESstartDT,'%m-%d-%y')
				runDatesInDB.append(oldOESstartDate)
				runsInDBdict[currentRunNumber] = {}
				runsInDBdict[currentRunNumber]['start date'] = oldOESstartDate
		else:
			isWLrow = False
			pass
print 'finished getting runs'

if len(runsInDB)>0:
	noLabelRow = False
else:
	if os.path.isfile(OESdbFile):
		os.remove(OESdbFile)

print sorted(runsInDB)

csvDataWriter = csv.writer(open(OESdbFile,'a'), delimiter = ',')
for folder in folders:
	print ''
	print 'processing', folder
	# get date of run and convert to datetime
	if re.search('\d\d-\d\d-\d\d',folder):
		OESstartDate = re.search('\d\d-\d\d-\d\d',folder).group(0)
		OESstartDate = datetime.datetime.strptime(OESstartDate, '%m-%d-%y')
	else:
		print folder, 'is not an OES folder'
		continue
	if OESstartDate in runDatesInDB:
		print 'run date', str(OESstartDate), 'already in OES database, skipping folder', folder
		continue
	os.chdir(baseOESdataPath + folder)
	# detect if is BE or PC process from zones listed in file names
	OESfiles = os.listdir('.')
	print 'OES files in folder are'
	for file in OESfiles:
		print file
	for file in OESfiles:
		if re.search('1B',file):
			print 'detected \'1B\' in file ' + file + ', labeling BE'
			BEprocess = True
			PCprocess = False
			process = 'BE'
			zoneList = ['1B','2B','3B','4B']
		elif re.search('5A',file):
			print 'detected \'5A\' in file ' + file + ', labeling PC'
			PCprocess = True
			BEprocess = False
			process = 'PC'
			zoneList = ['5A','5B','6A','6B']
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
				currentDatetime = (dateutil.parser.parse(row[0])-datetime.datetime(1970,1,1)).total_seconds()
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