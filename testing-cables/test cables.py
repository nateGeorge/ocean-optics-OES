'''
To do:
- add subplots so that 4 zones can be shown at once
- enable customization of zone mapping and zones shown at once
- add pass/fail test for each zone (when intensity reaches a certain level, turn the plot green and write 'pass')
'''


import seabreeze
seabreeze.use('pyseabreeze')
import seabreeze.spectrometers as sb
import pylab as plt
import ctypes, time, matplotlib
import numpy as np
import matplotlib.animation as animation
import easygui as eg

multiplexComPort = 15
multiNotConnected = True

matplotlib.rcParams.update({'font.size': 40})

mpdll = ctypes.WinDLL('Y:\Nate\Wayne\MPM2000drv.dll')

a = mpdll.MPM_OpenConnection('COM' + str(multiplexComPort)) #OES multiplexer is COM1 for now

print a

b = mpdll.MPM_InitializeDevice()

print b

while multiNotConnected:
    if a != 1 or b != 1:
        openDebug = eg.msgbox('Cannot connect to multiplexer (try unplugging the usb cable and plugging the multiplexer usb cable back in).  Multiplexer is set as COM' + str(multiplexComPort) + '.')
        exit()
    else:
        print 'successfully connected to multiplexer'
        multiNotConnected = False
# if need to select between multiple multiplexers, use this line:
# serialNo = mpdll.MPM_GetSerialNumber() #giving 0 for both multiplexers...not sure if this is correct.  OES multiplexer is COM1

mpdll.MPM_SetChannel(2)

#connects to first connected spectrometer it finds, takes intTime as integration time in nanoseconds, darkChannel as 
#multiplexer channel that is blocked from all light
#default int time is 1s, channel6 on the multiplexer is blocked off on MC02
#measures dark spectrum
#returns the spectrometer instance, spectrometer wavelengths, and measured dark spectrum
time.sleep(1)
devices = sb.list_devices()

#print devices[0] #use this line to print device name

time.sleep(1) #need to wait for a second, otherwise gives error in next step
spec = sb.Spectrometer(devices[0])
# sets integration time to 1 second
spec.integration_time_micros(1000000) #actually in nanoseconds not microseconds...WTF
time.sleep(2)

def plotdata(*args):
    int1 = spec.intensities()
    wl = spec.wavelengths()
    ax = plt.subplot(1,1,1)
    xLimMin = 200
    xLimMax = 800
    wlLimMinIndex = min(range(len(wl)), key=lambda i: abs(wl[i]-xLimMin))
    wlLimMaxIndex = min(range(len(wl)), key=lambda i: abs(wl[i]-xLimMax))
    plotInt = int1[wlLimMinIndex:wlLimMaxIndex]
    plotWl = wl[wlLimMinIndex:wlLimMaxIndex]
    
    fig.clf()
    plt.plot(plotWl, np.array(plotInt))
    plt.xlim([xLimMin,xLimMax])
    plt.ylim([min(plotInt),max(plotInt)])
    
fig=plt.figure()
try:
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
except AttributeError:
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    

ani = animation.FuncAnimation(fig, plotdata, interval=1000)
plt.show()
    