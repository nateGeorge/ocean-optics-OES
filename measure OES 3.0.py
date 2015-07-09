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

plotOESfile = 'C:/Users/operator/Desktop/plot OES 3.1.py'
MPMdriverPath = 'Y:/Nate/Wayne/'

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

if process == 'BE':
    zoneList = ['1B','2B','3B','4B']
elif process == 'PC':
    zoneList = ['5A','5B','6A','6B']
else:
    eg.msgbox(msg='You must choose either BE or PC. Try running the program again.')
    
zoneToIndexMap = {'1B':1, '2B':2, '3B':15, '4B':16, '5A':11, '5B':12, '6A':13, '6B':14}
    
ArMinIndex, ArMaxIndex = nsl.get_WL_indices(745.0, 760.0,
                                                    nsl.getOOWls())  # gets wl indices for ar peak to detect if plasma is on or not


def connect_to_multiplexer(comPort):
    #takes com port as a string, e.g. 'COM1'
    multiNotConnected = True
    
    a = mpdll.MPM_OpenConnection(comPort)
    b = mpdll.MPM_InitializeDevice()
    
    while multiNotConnected:
        if a == 1 and b == 1:
            print 'connected to multiplexer successfully'
            multiNotConnected = False
        else:
            print 'unable to connect to multiplexer...check to make sure com port is correct, try unplugging and replugging multiplexer USB cable'
            raw_input('press enter to exit')
            exit()
            
            #work in progress...popup message to warn operator of what's going on
            
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

    

    #serialNo = mpdll.MPM_GetSerialNumber() #giving 0 for both multiplexers...not sure if this is correct.  OES multiplexer is COM1

    


def connect_to_spectrometer(intTime=4500000,darkChannel=6,numberOfScans=6):
    #connects to first connected spectrometer it finds, takes intTime as integration time in nanoseconds, darkChannel as 
    #multiplexer channel that is blocked from all light
    #default int time is 1s, channel6 on the multiplexer is blocked off on MC02
    #measures dark spectrum
    #returns the spectrometer instance, spectrometer wavelengths, and measured dark spectrum
    time.sleep(1)
    devices = sb.list_devices()
    
    #print devices[0] #use this line to print device name
    
    time.sleep(1) #need to wait for a second, otherwise gives error in next step
    try:
        spec = sb.Spectrometer(devices[0])
    except IndexError:
        print 'couldn\'t find spectrometer.'
        print 'try unplugging usb cable from spectrometer and restart measurement'
        raw_input('press enter to exit')
        exit()
    spec.integration_time_micros(intTime) #actually in nanoseconds not microseconds...WTF
    mpdll.MPM_SetChannel(darkChannel)
    time.sleep(1) # have to wait at least 0.5s for multiplexer to switch
    
    #averages 15 measurements for the dark backround spectrum
    darkInt = spec.intensities()
    for each in range(numberOfScans - 1):
        darkInt += spec.intensities()
    darkInt = darkInt/float(numberOfScans)
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


def measure_OES_spectrum(OESchannel,darkInt,numberOfScans=3):
    #takes OESchannel as the multiplexer channel that connects to the minichamber to measure a spectrum
    #returns intensity average of 10 scans corrected with dark intensity spectrum
    
    mpdll.MPM_SetChannel(OESchannel)
    time.sleep(1) #need to wait at least 0.5s for multiplexer to switch inputs
    #take average of 15 measurements
    int1 = spec.intensities()
    for each in range(numberOfScans - 1):
        int1 += spec.intensities()
    int1 = int1/float(numberOfScans)
    int1 -= darkInt 
    
    return datetime.strftime(datetime.now(), '%m/%d/%y %H:%M:%S %p'), int1 #datetime string is made to match existing format in datasystem
    
def get_WL_indices(minWL,maxWL):
    #returns the indices of the wl list where the min and max wavelengths are, supplied as minWL and maxWL
    lowerWLindex=min(range(len(wl)), key=lambda i: abs(wl[i]-minWL))
    upperWLindex=min(range(len(wl)), key=lambda i: abs(wl[i]-maxWL))
    return lowerWLindex, upperWLindex   
    
def prepare_for_OES_measurements(savedir, savedate):
    #get indices of wavelength and intensity arrays for integration of OES peaks
    elementDict, normalizationKeys = nsl.OESparameters(True)
    elementList = elementDict.keys()
    OESmaxMins = {}
    for element in elementList:
        #gets indices of wavelength and intensity arrays for integration
        OESmaxMins[element+'MIN'], OESmaxMins[element+'MAX'] = get_WL_indices(elementDict[element]['minWL'], elementDict[element]['maxWL'])


    #make list of elements and zones measured
    measuredElementList = elementList + normalizationKeys#use this: ['Cu', 'In', 'Ga', 'Ar', 'O2', 'H2'] to restrict list as needed
    combinedList = [zone + ' ' + element for zone in zoneList for element in measuredElementList] #Combines list like 5A Cu, 5A In, etc...
    OESdataDict={}
    for zone in zoneList:
        OESdataDict[zone] = {}
        OESdataDict[zone]['DT'] = ''
        for element in measuredElementList:
            OESdataDict[zone][element]= ''
    
    #start OES raw spectra files for each zone, and save wavelengths on first row (if doesn't already exist)
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
        
    #start OES integrated signals file and save labels on first row (if doesn't already exist)
    if os.path.isfile(savedir + savedate + ' -- OES signals.csv'):
        with open(savedir + savedate + ' -- ' + zone + ' OES raw spectra.csv', 'rb') as csvfile:
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
    return zoneList, measuredElementList, OESmaxMins, OESdataDict

        
def measure_allZones_OES(wl, zoneList, measuredElementList, OESmaxMins, savedir, savedate, OESdataDict, darkChannel, processStarted, numberOfScans = 6):
    global shutOffStartTime
    global shutOffTimerStarted
    global timeSinceShutOff
    
    #need to measure dark int spectrum each time because of drift (probably from temperature)
    mpdll.MPM_SetChannel(darkChannel)
    time.sleep(1) # have to wait at least 0.5s for multiplexer to switch
    
    #averages 15 measurements for the dark background spectrum
    darkInt = spec.intensities()
    for each in range(numberOfScans - 1):
        darkInt += spec.intensities()
    darkInt = darkInt/float(numberOfScans)
    # write darkInt to file in case something is screwed up
    notWritten = True
    while notWritten:
        try:
            with open(savedir + savedate + ' -- ' + ' OES raw spectra -- Dark Int.csv', 'ab') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([datetime.strftime(datetime.now(), '%m/%d/%y %H:%M:%S %p')]+[eachInt for eachInt in darkInt])
            notWritten = False
        except IOError:
            print '\n*****************'
            print ' raw spectra file (' + savedir + savedate + ' -- ' + ' OES raw spectra -- Dark Int.csv' + ') is open another program, please close it'
            print '*****************\n'
            time.sleep(5)
        

    #measures the OES spectra in each zone, and for each element.  appends the CSV files storing the data.
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
                #integrates raw OES spectrum
                OESdataDict[zone][element] = integrate.simps(rawOESspectrum[OESmaxMins[element+'MIN']:OESmaxMins[element+'MAX']],wl[OESmaxMins[element+'MIN']:OESmaxMins[element+'MAX']])
                
                #checks to see if machine has shut down (plasma is off).  once it is off for 10 minutes, stop measuring
                if element == 'Fi':
                    if OESdataDict[zone][element] >= 5000:
                        if not processStarted:
                            processStarted = True
                        shutOffTimerStarted = False
                        timeSinceShutOff = 0
                    elif OESdataDict[zone][element] <= 5000 and processStarted:
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
                            if timeSinceShutOff > 150: # if all 4 zones are off twice through the cycle
                                print 'shutting down program because shutofftimer exceeded (targets off for 10 mins)'
                                # close plotting process if it is open
                                if subprocess.Popen.poll(plottingProc) == None:
                                    subprocess.Popen.terminate(plottingProc)
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
            
        #opens file to save OES integrated data, but checks if it is open elsewhere first and warns user
        notWritten = True
        while notWritten:
            try:    
                with open(savedir + savedate + ' -- OES signals.csv', 'ab') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow([OESdataDict[zone]['DT']]+[OESdataDict[zone][element] for zone in zoneList for element in measuredElementList])
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
    multiplexerComPort = 'COM5'
    
    mpdll = ctypes.WinDLL(MPMdriverPath + 'MPM2000drv.dll')
    
    savedate = datetime.strftime(datetime.now(),'%m-%d-%y') #made DT format similar to data system format
    savedir = 'C:/OESdata/' + 'PC ' + savedate + '/'
    
    print '\n connecting to multiplexer... \n'
    connect_to_multiplexer(multiplexerComPort) #OES multiplexer is COM5 for now
    
    print '\n initializing spectrometer... \n'
    spec,wl,darkInt = connect_to_spectrometer()

    print '\n preparing data files... \n'   
    zoneList, measuredElementList, OESmaxMins, OESdataDict = prepare_for_OES_measurements(savedir, savedate)
    
    plotCounter = 0
    while True:
        print '\n collecting spectra for zones ' + ', '.join(zoneList) + '... \n'
        OESdataDict, processStarted = measure_allZones_OES(wl, zoneList, measuredElementList, OESmaxMins, savedir, savedate, OESdataDict, processStarted = processStarted, darkChannel=6)
        if plotCounter == 0:
            if runNum != None:
                plottingProc = subprocess.Popen(['python',plotOESfile,'True',str(runNum),process])
            else:
                plottingProc = subprocess.Popen(['python',plotOESfile,'True','none',process])
            plotCounter += 1
    
    mpdll.MPM_CloseConnection()
