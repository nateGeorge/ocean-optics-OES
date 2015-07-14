'''
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

import ctypes, time, os, csv, matplotlib, subprocess, sys, datetime, re
import seabreeze
seabreeze.use('pyseabreeze')
import seabreeze.spectrometers as sb
sys.path.append('Y:/Nate/git/nuvosun-python-lib/')
import nuvosunlib as nsl

measureOESfile = 'C:/Users/operator/Desktop/measure OES 3.0.py'

processesToMonitor = sys.argv[1]
runNum = sys.argv[2]

BEzones = ['1B','2B','3B','4B']
PCzones = ['5A','5B','6A','6B']

if processesToMonitor == 'BE':
    indexToZoneMap = {'1B':1, '2B':2, '3B':15, '4B':16}
elif processesToMonitor == 'PC':
    indexToZoneMap = {'5A':11, '5B':12, '6A':13, '6B':14}
elif processesToMonitor == 'BE+PC':
    indexToZoneMap = {'1B':1, '2B':2, '3B':15, '4B':16, '5A':11, '5B':12, '6A':13, '6B':14}

MPMdriverPath = 'Y:/Nate/Wayne/'
mpdll = ctypes.WinDLL(MPMdriverPath + 'MPM2000drv.dll')

def connect_to_multiplexer(comPort):
    #takes com port as a string, e.g. 'COM1'
    mpdll.MPM_OpenConnection(comPort)

    mpdll.MPM_InitializeDevice()

    #serialNo = mpdll.MPM_GetSerialNumber() #giving 0 for both multiplexers...not sure if this is correct.  OES multiplexer is COM1

def connect_to_spectrometer(intTime=1000000,darkChannel=6,numberOfScans=15):
    #connects to first connected spectrometer it finds, takes intTime as integration time in nanoseconds, darkChannel as 
    #multiplexer channel that is blocked from all light
    #default int time is 1s, channel6 on the multiplexer is blocked off on MC02
    #measures dark spectrum
    #returns the spectrometer instance, spectrometer wavelengths, and measured dark spectrum
    
    time.sleep(1) # sometimes needs a small delay here...don't know why
    devices = sb.list_devices()
    
    #print devices[0] #use this line to print device name
    
    time.sleep(1) #need to wait for a second, otherwise gives error in next step
    spec = sb.Spectrometer(devices[0])
    spec.integration_time_micros(intTime) #actually in nanoseconds not microseconds...WTF
    return spec
    
def check_for_plasma(OESchannel,darkChannel,numberOfScans=15):
    global arOnCount
    global arOffCount
    global spec
    #takes OESchannel as the multiplexer channel that connects to the minichamber to measure a spectrum
    #returns intensity average of 10 scans corrected with dark intensity spectrum
    
    mpdll.MPM_SetChannel(darkChannel)
    time.sleep(1) # have to wait at least 0.5s for multiplexer to switch
    
    #averages 15 measurements for the dark background spectrum
    darkInt = spec.intensities()
    for each in range(numberOfScans-1):
        darkInt += spec.intensities()
    darkInt = darkInt/float(numberOfScans)
    wl = spec.wavelengths()
    
    mpdll.MPM_SetChannel(OESchannel)
    time.sleep(1) #need to wait at least 0.5s for multiplexer to switch inputs
    #take average of 15 measurements
    int1 = spec.intensities()
    for each in range(numberOfScans - 1):
        int1 += spec.intensities()
    int1 = int1/float(numberOfScans)
    int1 -= darkInt
    
    arLine750 = int1[ArMinIndex:ArMaxIndex]
    arInt = max(arLine750)
    print 'monitoring',processesToMonitor,'argon intensity in zone',zone,'=',arInt
    if arInt > 500:
        arOnCount += 1
        arOffCount = 0
        if arOnCount >= 8: # if plasma has been on for 2 measuring cycles
            if processesToMonitor == 'BE':
                subprocess.Popen(['python',measureOESfile,runNum,'BE'])
            elif processesToMonitor == 'PC':
                subprocess.Popen(['python',measureOESfile,runNum,'PC'])
            else:
                if zone in BEzones:
                    subprocess.Popen(['python',measureOESfile,runNum,'BE'])
                if zone in PCzones:
                    subprocess.Popen(['python',measureOESfile,runNum,'PC'])
            spec.close()
            exit()
    else:
        # sometimes a zone or two can be low in intensity because of broken parts
        # this will make sure all zones have been off through one measuring cycle before resetting the 
        # plasma detection timer
        arOffCount += 1
        if arOffCount >= 4:
            arOnCount = 0
            arOffCount = 0
    
    return datetime.datetime.strftime(datetime.datetime.now(), '%m/%d/%y %H:%M:%S %p'), int1 #datetime string is made to match existing format in datasystem

ArMinIndex, ArMaxIndex = nsl.get_WL_indices(745.0, 760.0,
                                                    nsl.getOOWls())  # gets wl indices for ar peak to detect if plasma is on or not
connect_to_multiplexer('COM5')

global spec
spec = connect_to_spectrometer()
global arOnCount
arOnCount = 0
global arOffCount
arOffCount = 0
while True:
    for zone in indexToZoneMap.keys():
        check_for_plasma(indexToZoneMap[zone], darkChannel = 6)