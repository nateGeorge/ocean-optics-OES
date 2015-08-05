# takes 3 arguments: run number (i.e. 500), process (i.e. BE), and tool (i.e. MC02, but not really necessary as it picks this up automatically)

'''
spectrometer range: 200 to 900 nm
previous program used these OES lines:
Cu 325-327 doublet (323.153 to 328.6779). these have relative intensities (RI) of 10000 each, next nearest 
high intensity line is at 202, with relative int of 7000
In 451 (449.8283 to 452.3268)  has RI of 18000
Ga 416 (415.7486 to 418.6306)

Ar 763
Ar 812

Zones, targets, and multiplexer channels:

Zone    Target  Multiplexer channel
1B  Ti          15
2B  Mo          16
3B  Ti          1
4B  Mo          2
5A  In          11
5B  CuGa        12
6A  CIG         13
6B  CIG         14

'''
import ctypes, time, os, csv, matplotlib, subprocess, sys, re
import sqlite3 as sq
import pylab as plt
import easygui as eg
import seabreeze
seabreeze.use('pyseabreeze')
import seabreeze.spectrometers as sb
from datetime import datetime
from scipy import integrate
import pylab as plt
import matplotlib.dates as mdates
sys.path.append("Y:/Nate/git/nuvosun-python-lib/")
import nuvosunlib as nsl

# option for summing Z5-6, Z5A+Z5B
# enabling will require restructuring the database
calcSumOfZones = False
if calcSumOfZones:
    fullZoneList = zoneList + sumZoneList
else:
    fullZoneList = zoneList

# connect to sqlite DB and get cursor

plotOESfile = 'C:/OESdata/plot OES 3.1.py'
autoBackupfile = 'C:/OESdata/auto backup files, read schedule and start measurements.py'
MPMdriverPath = 'Y:/Nate/Wayne/'

files = os.listdir('C:/OESdata')
for file in files:
    if re.search('MC\d\d.txt',file):
        tool = file[:4]

BEzoneList, PCzoneList, zoneToIndexMap, MPcomPort, BEintTime, BEnumScans, PCintTime, PCnumScans = nsl.load_OES_config(tool)

try:
    runNum = sys.argv[1]
    process = sys.argv[2]
except:
    BEproc = eg.ynbox(msg='Which process is running?', title='choose process', choices=('BE','PC'))
    if BEproc:
        process = 'BE'
    elif not BEproc:
        process = 'PC'
    try:
        runNum = str(eg.integerbox(msg='enter run number (a format like \'440\' is fine)', title='enter run number', upperbound=99999))
        runNum = runNum.lstrip('S')
        runNum = runNum.lstrip('s')
        runNum = runNum.lstrip('0')
        print 'using',runNum,'as run number'
    except:
        runNum = None
        
try:
    tool = sys.argv[3]
except:
    files = os.listdir('C:/OESdata')
    for file in files:
        if re.search('MC\d\d.txt',file):
            tool = file[:4]

if process == 'BE':
    zoneList = BEzoneList
    sumZoneList = []
    procIntTime = BEintTime * 1000000 # convert to microseconds
    procNumScans = BEnumScans
    dataBase = sq.connect('C:/OESdata/allBEOESData.db')
    curse = dataBase.cursor()
elif process == 'PC':
    zoneList = PCzoneList
    sumZoneList = ['5A + 5B', 'zones 5 + 6']
    procIntTime = PCintTime * 1000000 # convert to microseconds
    procNumScans = PCnumScans
    dataBase = sq.connect('C:/OESdata/allPCOESData.db')
    curse = dataBase.cursor()
else:
    eg.msgbox(msg='You must choose either BE or PC. Try running the program again.')
    
ArMinIndex, ArMaxIndex = nsl.get_WL_indices(745.0, 760.0,
                                                    nsl.getOOWls())  # gets wl indices for ar peak to detect if plasma is on or not


def connect_to_multiplexer(comPort):
    # takes com port as a string, e.g. 'COM1'
    multiNotConnected = True
    
    a = mpdll.MPM_OpenConnection(comPort)
    b = mpdll.MPM_InitializeDevice()
    
    while multiNotConnected:
        if a == 1 and b == 1:
            print 'connected to multiplexer successfully'
            multiNotConnected = False
        else:
            print 'unable to connect to multiplexer...check to make sure com port is correct, try unplugging and replugging multiplexer USB cable'
            eg.msgbox('unable to connect to multiplexer...check to make sure com port is correct, try unplugging and replugging multiplexer USB cable. Com port set as ' + MPcomPort)
            raw_input('press enter to exit')
            exit()
            
            # work in progress...popup message to warn operator of what's going on
            
            '''
            fig = plt.figure()
            plt.axis('off')
            data = random.random((5,5))
            try:
                figManager = plt.get_current_fig_manager()
                figManager.window.showMaximized()
            except AttributeError:
                mng = plt.get_current_fig_manager()
                mng.window.state('zoomed')
            ax = fig.add_subplot(111)
            ax.imshow(data,interpolation='nearest')
            ax.annotate('not able to connect to multiplexer...check to make sure com port is correct, try unplugging and replugging multiplexer USB cable', xytext = (0,0.5), xy = (0,0.5))
            fig.show()
            time.sleep(1)
            fig.close()
            '''

    

    # serialNo = mpdll.MPM_GetSerialNumber() #giving 0 for both multiplexers...not sure if this is correct.  OES multiplexer is COM1

def connect_to_spectrometer(intTime=procIntTime,darkChannel=6,numberOfScans=procNumScans):
    # connects to first connected spectrometer it finds, takes intTime as integration time in microseconds, darkChannel as 
    # multiplexer channel that is blocked from all light
    # default int time is 1s, channel6 on the multiplexer is blocked off on MC02
    # measures dark spectrum
    # returns the spectrometer instance, spectrometer wavelengths, and measured dark spectrum
    time.sleep(1)
    devices = sb.list_devices()
    
    # print devices[0] #use this line to print device name
    
    time.sleep(1) #need to wait for a second, otherwise gives error in next step
    try:
        spec = sb.Spectrometer(devices[0])
    except IndexError:
        print 'couldn\'t find spectrometer.'
        print 'try unplugging usb cable from spectrometer and restart measurement'
        raw_input('press enter to exit')
        exit()
    spec.integration_time_micros(intTime)
    mpdll.MPM_SetChannel(darkChannel)
    time.sleep(1) # have to wait at least 0.5s for multiplexer to switch
    
    print 'taking background reading, should take ', str(2*numberOfScans*intTime/(1000000.)),'seconds'
    darkInt = spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)
    for each in range(numberOfScans*2 - 1):
        darkInt += spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)
    darkInt = darkInt/float(numberOfScans*2)
    wl = spec.wavelengths()
    # write darkInt to file in case its needed
    
    if not os.path.isdir(savedir):
        os.mkdir(savedir)
    if not os.path.isfile(savedir + savedate + ' -- ' + ' OES raw spectra -- Dark Int.csv'):
        notWritten = True
        while notWritten:
            try:
                with open(savedir + savedate + ' -- ' + ' OES raw spectra -- Dark Int.csv', 'wb') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow(['DateTime']+[eachWL for eachWL in wl])
                    notWritten = False
            except IOError:
                print '\n*****************'
                print ' raw spectra file (' + savedir + savedate + ' -- ' + ' OES raw spectra -- Dark Int.csv' + ') is open another program, please close it'
                print '*****************\n'
                time.sleep(5)
    
    notWritten = True
    while notWritten:
        try:
            with open(savedir + savedate + ' -- ' + ' OES raw spectra -- Dark Int.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([datetime.strftime(datetime.now(), '%m/%d/%y %H:%M:%S %p')]+[eachInt for eachInt in darkInt])
            notWritten = False
        except IOError:
            print '\n*****************'
            print zoneList[each] + ' raw spectra file (' + savedir + savedate + ' -- ' + ' OES raw spectra -- Dark Int.csv' + ') is open another program, please close it'
            print '*****************\n'
            time.sleep(5)
    
    return spec, spec.wavelengths(), darkInt


def measure_OES_spectrum(OESchannel,darkInt,numberOfScans=procNumScans):
    # takes OESchannel as the multiplexer channel that connects to the minichamber to measure a spectrum
    # returns intensity average of 10 scans corrected with dark intensity spectrum
    
    mpdll.MPM_SetChannel(OESchannel)
    time.sleep(1) #need to wait at least 0.5s for multiplexer to switch inputs
    # take average of 15 measurements
    int1 = spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)
    for each in range(numberOfScans - 1):
        int1 += spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)
    int1 = int1/float(numberOfScans)
    int1 -= darkInt 
    
    return datetime.strftime(datetime.now(), '%m/%d/%y %H:%M:%S %p'), int1 #datetime string is made to match existing format in datasystem
    
def get_WL_indices(minWL,maxWL):
    # returns the indices of the wl list where the min and max wavelengths are, supplied as minWL and maxWL
    lowerWLindex=min(range(len(wl)), key=lambda i: abs(wl[i]-minWL))
    upperWLindex=min(range(len(wl)), key=lambda i: abs(wl[i]-maxWL))
    return lowerWLindex, upperWLindex   
    
def prepare_for_OES_measurements(savedir, savedate):
    # get indices of wavelength and intensity arrays for integration of OES peaks
    elementDict, normalizationKeys = nsl.OESparameters(True)
    elementList = elementDict.keys()
    OESmaxMins = {}
    for element in elementList:
        # gets indices of wavelength and intensity arrays for integration
        OESmaxMins[element+'MIN'], OESmaxMins[element+'MAX'] = get_WL_indices(elementDict[element]['minWL'], elementDict[element]['maxWL'])


    # make list of elements and zones measured
    measuredElementList = elementList + normalizationKeys#use this: ['Cu', 'In', 'Ga', 'Ar', 'O2', 'H2'] to restrict list as needed
    combinedList = [zone + ' ' + element for zone in (fullZoneList) for element in measuredElementList] #Combines list like 5A Cu, 5A In, etc...
    OESdataDict={}
    for zone in fullZoneList:
        OESdataDict[zone] = {}
        OESdataDict[zone]['DT'] = ''
        for element in measuredElementList:
            OESdataDict[zone][element]= ''
    
    # start OES raw spectra files for each zone, and save wavelengths on first row (if doesn't already exist)
    for zone in zoneList:
        if not os.path.isdir(savedir):
            os.mkdir(savedir)
        if not os.path.isfile(savedir + savedate + ' -- ' + zone + ' OES raw spectra.csv'):
            notWritten = True
            while notWritten:
                try:
                    with open(savedir + savedate + ' -- ' + zone + ' OES raw spectra.csv', 'wb') as csvfile:
                        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                        spamwriter.writerow(['DateTime']+[eachWL for eachWL in wl])
                        notWritten = False
                except IOError:
                    print '\n*****************'
                    print zoneList[each] + ' raw spectra file (' + savedir + savedate + ' -- ' + zoneList[each] + ' OES raw spectra.csv' + ') is open another program, please close it'
                    print '*****************\n'
                    time.sleep(5)
                    
    # create sqlite DB if not already existing
    
    exstr = '(tool TEXT, datetime TEXT, ' + ', '.join(['\"' + e + '\"' + ' REAL' for e in combinedList]) + ')'
    curse.execute("CREATE TABLE IF NOT EXISTS oesdata " + exstr)
        
    # start OES integrated signals file and save labels on first row (if doesn't already exist)
    if os.path.isfile(savedir + savedate + ' -- OES signals.csv'):
        with open(savedir + savedate + ' -- OES signals.csv', 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            firstRow = True
            if not firstRow:
                for row in spamreader:
                    for each in range(len(row)-1): # if the file is already there, we read in the data
                        OESdataDict[combinedList[each][:2]][combinedList[each][2:]].append(row[each+1])
                        OESdataDict[combinedList[each][:2]['DT']].append(row[0])
            else:
                firstRow = False
    else:
        notWritten = True
        while notWritten:
            try:
                with open(savedir + savedate + ' -- OES signals.csv', 'wb') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow(['DateTime']+combinedList)
                    notWritten = False
            except IOError:
                print '\n*****************'
                print zoneList[each] + ' raw spectra file (' + savedir + savedate + ' -- ' + zoneList[each] + ' OES raw spectra.csv' + ') is open another program, please close it'
                print '*****************\n'
                time.sleep(5)
    return zoneList, measuredElementList, OESmaxMins, OESdataDict, combinedList

        
def measure_allZones_OES(wl, zoneList, measuredElementList, OESmaxMins, savedir, savedate, OESdataDict, combinedList, darkInt, processStarted, numberOfScans = procNumScans, darkChannel = 6):
    global shutOffStartTime
    global shutOffTimerStarted
    global timeSinceShutOff
    
    # measures the OES spectra in each zone, and for each element.  appends the CSV files storing the data.
    for zone in zoneList:
        OESdataDict[zone]['DT'], rawOESspectrum = measure_OES_spectrum(zoneToIndexMap[zone], darkInt)          
        for element in measuredElementList:
            if re.search('/', element):
                # calculate normalizations
                if element[-2:] == 'Fi':
                    OESdataDict[zone][element] = (OESdataDict[zone][element[:-3]] / OESdataDict[zone]['Fi'])
                elif element[-6:] == 'Ar-811':
                    OESdataDict[zone][element] = (OESdataDict[zone][element[:-7]] / OESdataDict[zone]['Ar-811'])
                elif element[-11:] == '(Fi*Ar-811)':
                    OESdataDict[zone][element] = (OESdataDict[zone][element[:-12]] / (
                        OESdataDict[zone]['Fi'] * OESdataDict[zone]['Ar-811']))
            else:
                # integrates raw OES spectrum
                OESdataDict[zone][element] = integrate.simps(rawOESspectrum[OESmaxMins[element+'MIN']:OESmaxMins[element+'MAX']],wl[OESmaxMins[element+'MIN']:OESmaxMins[element+'MAX']])
                
                # checks to see if machine has shut down (plasma is off).  once it is off for 3 minutes, stop measuring
                if element == 'Fi':
                    if OESdataDict[zone][element] >= 10000:
                        if not processStarted:
                            processStarted = True
                        shutOffTimerStarted = False
                        timeSinceShutOff = 0
                    elif OESdataDict[zone][element] <= 10000 and processStarted:
                        if not shutOffTimerStarted:
                            if element == 'Ar-811':
                                print 'starting shutoff timer because zone', zone, 'is off'
                            shutOffStartTime = datetime.now()
                            shutOffTimerStarted = True
                        else:
                            timeSinceShutOff = (datetime.now() - shutOffStartTime).total_seconds()
                            if element == 'Ar-811':
                                print 'zone',zone,'is off, time since tool stopped sputtering is,',timeSinceShutOff
                                print 'close this window to shut down OES'
                            if timeSinceShutOff > 5*60: # if sputtering off for 5 mins
                                print 'shutting down program because shutofftimer exceeded (targets off for 5 mins)'
                                expBasepath = 'Y:/Experiment Summaries/Year ' + str(datetime.now().year) + '/'
                                expRunPath = expBasepath + '/' + 'S' + str(runNum).zfill(5) + '/'
                                expOESPath = expRunPath + tool + ' OES data' + '/'
                                expOESprocPath = expOESPath + process
                                for eachPath in [expBasepath,expRunPath,expOESpath,expOESprocPath]:
                                    if not os.path.exists(eachPath):
                                        os.mkdir(eachPath)
                                nsl.backupFiles(savedir,expOESprocPath)
                                # close plotting process if it is open
                                if subprocess.Popen.poll(plottingProc) == None:
                                    subprocess.Popen.terminate(plottingProc)
                                subprocess.Popen(['python',autoBackupfile,'False'])
                                mpdll.MPM_CloseConnection()
                                dataBase.close()
                                raw_input('press enter to exit')
                                exit()
                        
        
        notWritten = True
        while notWritten:
            try:
                with open(savedir + savedate + ' -- ' + zone + ' OES raw spectra.csv', 'ab') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow([OESdataDict[zone]['DT']]+[zoneInt for zoneInt in rawOESspectrum])
                notWritten = False
            except IOError:
                print '\n*****************'
                print zone + ' raw spectra file (' + savedir + savedate + ' -- ' + zone + ' OES raw spectra.csv' + ') is open another program, please close it'
                print '*****************\n'
                time.sleep(5)
        
        # if running PC, add zones 5A+5B, and all zones for composition measurements
        # disabled for now, too complex and unnecessary. Set calcSumOfZones = True to enable, will have to re-create database also
        if calcSumOfZones:
            if process == 'PC':
                if zone == '5B':
                    for element in OESdataDict['5B'].keys():
                        if element != 'DT':
                            OESdataDict['5A + 5B'][element] = OESdataDict['5A'][element] + OESdataDict['5B'][element]
                        OESdataDict['5A + 5B']['DT'] = OESdataDict['5B']['DT']
                if zone == '6B':
                    for element in OESdataDict['6B'].keys():
                        if element != 'DT':
                            OESdataDict['zones 5 + 6'][element] = OESdataDict['5A'][element] + OESdataDict['5B'][element] + OESdataDict['6A'][element] + OESdataDict['6B'][element]
                        OESdataDict['zones 5 + 6']['DT'] = OESdataDict['6B']['DT']
        
        # save integration data to sqlite database
        qs = '?, '*(len(combinedList) + 2)
        exStr = 'INSERT INTO oesdata VALUES (' + qs[:-2] + ')'
        curse.execute(exStr, [tool] + [OESdataDict[zone]['DT']]+[OESdataDict[zone][element] for zone in (fullZoneList) for element in measuredElementList])
        dataBase.commit()
        # opens file to save OES integrated data, but checks if it is open elsewhere first and warns user
        notWritten = True
        while notWritten:
            try:    
                with open(savedir + savedate + ' -- OES signals.csv', 'ab') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow([OESdataDict[zone]['DT']]+[OESdataDict[zone][element] for zone in (fullZoneList) for element in measuredElementList])
                notWritten = False
            except IOError:
                print '\n*****************'
                print 'OES file (' + savedir + savedate + ' -- OES signals.csv' + ') is open another program, please close it'
                print '*****************\n'
                time.sleep(5)
        
    return OESdataDict, processStarted
                
if __name__ == '__main__':
    global shutOffStartTime
    global shutOffTimerStarted
    global timeSinceShutOff
    global plottingProc
    shutOffTimerStarted = False
    timeSinceShutOff = 0
    processStarted = False
    shutOffStartTime = 0
    multiplexerComPort = MPcomPort
    
    mpdll = ctypes.WinDLL(MPMdriverPath + 'MPM2000drv.dll')
    
    savedate = datetime.strftime(datetime.now(),'%m-%d-%y') # made DT format similar to data system format
    if runNum != None:
        savedir = 'C:/OESdata/' + process + ' ' + savedate + ' ' + tool + ' ' + runNum.zfill(5) + '/'
    else:
        savedir = 'C:/OESdata/' + process + ' ' + savedate + ' ' + tool + '/'
    
    print '\n connecting to multiplexer... \n'
    connect_to_multiplexer(multiplexerComPort)
    
    print '\n initializing spectrometer... \n'
    spec,wl,darkInt = connect_to_spectrometer()

    print '\n preparing data files... \n'   
    zoneList, measuredElementList, OESmaxMins, OESdataDict, combinedList = prepare_for_OES_measurements(savedir, savedate)
    
    plotCounter = 0
    while True:
        print '\n collecting spectra for zones ' + ', '.join(zoneList) + '... \n'
        OESdataDict, processStarted = measure_allZones_OES(wl, zoneList, measuredElementList, OESmaxMins, savedir, savedate, OESdataDict, combinedList, processStarted = processStarted, darkInt=darkInt)
        if plotCounter == 0:
            if runNum != None:
                plottingProc = subprocess.Popen(['python',plotOESfile,'True',str(runNum),process])
            else:
                plottingProc = subprocess.Popen(['python',plotOESfile,'True','none',process])
            plotCounter += 1
