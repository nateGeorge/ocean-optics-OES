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

Zone	Target	Multiplexer channel
1B	Ti			15
2B	Mo			16
3B	Ti			1
4B	Mo			2
5A	In			11
5B	CuGa		12
6A	CIG			13
6B	CIG			14

'''
import ctypes, time, os, csv, matplotlib, subprocess
import pylab as plt
import seabreeze
seabreeze.use('pyseabreeze')
import seabreeze.spectrometers as sb
from datetime import datetime
from scipy import integrate
import pylab as plt
import matplotlib.dates as mdates

def connect_to_multiplexer(comPort):
	#takes com port as a string, e.g. 'COM1'
	mpdll.MPM_OpenConnection(comPort)

	mpdll.MPM_InitializeDevice()

	#serialNo = mpdll.MPM_GetSerialNumber() #giving 0 for both multiplexers...not sure if this is correct.  OES multiplexer is COM1

	


def connect_to_spectrometer(intTime=1000000,darkChannel=6):
	#connects to first connected spectrometer it finds, takes intTime as integration time in nanoseconds, darkChannel as 
	#multiplexer channel that is blocked from all light
	#default int time is 1s, channel6 on the multiplexer is blocked off on MC02
	#measures dark spectrum
	#returns the spectrometer instance, spectrometer wavelengths, and measured dark spectrum
	
	devices = sb.list_devices()
	
	#print devices[0] #use this line to print device name
	
	time.sleep(1) #need to wait for a second, otherwise gives error in next step
	spec = sb.Spectrometer(devices[0])
	spec.integration_time_micros(intTime) #actually in nanoseconds not microseconds...WTF
	mpdll.MPM_SetChannel(darkChannel)
	time.sleep(1) # have to wait at least 0.5s for multiplexer to switch
	
	#averages 15 measurements for the dark backround spectrum
	darkInt = spec.intensities()
	for each in range(14):
		darkInt += spec.intensities()
	darkInt = darkInt/15.0
	return spec, spec.wavelengths(), darkInt


def measure_OES_spectrum(OESchannel,darkInt):
	#takes OESchannel as the multiplexer channel that connects to the minichamber to measure a spectrum
	#returns intensity average of 10 scans corrected with dark intensity spectrum
	
	mpdll.MPM_SetChannel(OESchannel)
	time.sleep(1) #need to wait at least 0.5s for multiplexer to switch inputs
	#take average of 15 measurements
	int1 = spec.intensities()
	for each in range(14):
		int1 += spec.intensities()
	int1 = int1/15.0
	int1 -= darkInt
	return datetime.strftime(datetime.now(), '%m/%d/%y %H:%M:%S %p'), int1 #datetime string is made to match existing format in datasystem
	
def get_WL_indices(minWL,maxWL):
	#returns the indices of the wl list where the min and max wavelengths are, supplied as minWL and maxWL
	lowerWLindex=min(range(len(wl)), key=lambda i: abs(wl[i]-minWL))
	upperWLindex=min(range(len(wl)), key=lambda i: abs(wl[i]-maxWL))
	return lowerWLindex, upperWLindex	
	
def prepare_for_OES_measurements(savedir, savedate):
	#get indices of wavelength and intensity arrays for integration of OES peaks
	elementList = ['Cu','In','Ga','Se','Ar','Na','Mo','Ti','O2','H2']
	OESminList = [323.0, 449.0, 415.0, 470.0, 760.0, 587.0, 378.0, 496.0, 775.0, 654.0] #wavelength minimums for OES integration
	OESmaxList = [329.0, 453.0, 419.0, 475.0, 766.0, 591.0, 382.0, 508.0, 779.0, 658.0] #wavelength maxs
	OESmaxMins = {}
	for each in range(len(elementList)):
		#gets indices of wavelength and intensity arrays for integration
		OESmaxMins[str(elementList[each])+'MIN'], OESmaxMins[str(elementList[each])+'MAX'] = get_WL_indices(OESminList[each], OESmaxList[each])


	#make list of elements and zones measured
	zoneList = ['5A','5B','6A','6B']
	measuredElementList = elementList #use this: ['Cu', 'In', 'Ga', 'Ar', 'O2', 'H2'] to restrict list as needed
	combinedList = [zone + ' ' + element for zone in zoneList for element in measuredElementList] #Combines list like 5A Cu, 5A In, etc...
	'''OESdataDict = {}
	for each in combinedList:
		OESdataDict['DT'+each]=[]'''
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
					for each in range(len(row)-1):
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

		
def measure_allZones_OES(wl, zoneList, measuredElementList, OESmaxMins, savedir, savedate, OESdataDict, darkChannel):
    #need to measure dark int spectrum each time because of drift (probably from temperature)
	mpdll.MPM_SetChannel(darkChannel)
	time.sleep(1) # have to wait at least 0.5s for multiplexer to switch
	
	#averages 15 measurements for the dark backround spectrum
	darkInt = spec.intensities()
	for each in range(14):
		darkInt += spec.intensities()
	darkInt = darkInt/15.0

	#measures the OES spectra in each zone, and for each element.  appends the CSV files storing the data.
	for each in range(len(zoneList)):
		OESdataDict[zoneList[each]]['DT'], rawOESspectrum = measure_OES_spectrum(each+11, darkInt)
		for element in measuredElementList:
			#integrates raw OES spectrum
			OESdataDict[zoneList[each]][element] = integrate.simps(rawOESspectrum[OESmaxMins[element+'MIN']:OESmaxMins[element+'MAX']],wl[OESmaxMins[element+'MIN']:OESmaxMins[element+'MAX']])

		notWritten = True
		while notWritten:
			try:
				with open(savedir + savedate + ' -- ' + zoneList[each] + ' OES raw spectra.csv', 'ab') as csvfile:
					spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
					spamwriter.writerow([OESdataDict[zoneList[each]]['DT']]+[eachInt for eachInt in rawOESspectrum])
				notWritten = False
			except IOError:
				print '\n*****************'
				print zoneList[each] + ' raw spectra file (' + savedir + savedate + ' -- ' + zoneList[each] + ' OES raw spectra.csv' + ') is open another program, please close it'
				print '*****************\n'
				time.sleep(5)
			
		#opens file to save OES integrated data, but checks if it is open elsewhere first and warns user
		notWritten = True
		while notWritten:
			try:	
				with open(savedir + savedate + ' -- OES signals.csv', 'ab') as csvfile:
					spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
					
					'''if OESdataDict[zoneList[0]][measuredElementList[0]] == []: #if the zone hasn't been measured yet, puts
						for zone in zoneList:
							for element in measuredElementList:
								OESdataDict[zone][element] = 0'''
					spamwriter.writerow([OESdataDict[zoneList[each]]['DT']]+[OESdataDict[zone][element] for zone in zoneList for element in measuredElementList])
				notWritten = False
			except IOError:
				print '\n*****************'
				print 'OES file (' + savedir + savedate + ' -- OES signals.csv' + ') is open another program, please close it'
				print '*****************\n'
				time.sleep(5)
		
	return OESdataDict
				
if __name__ == '__main__':
	mpdll = ctypes.WinDLL('C:\Wayne\MPM2000drv.dll')
	
	savedate = datetime.strftime(datetime.now(),'%m-%d-%y') #made DT format similar to data system format
	savedir = 'C:/OESdata/' + 'PC ' + savedate + '/'
	
	print '\n connecting to multiplexer... \n'
	connect_to_multiplexer('COM1') #OES multiplexer is COM1 for now
	
	print '\n initializing spectrometer... \n'
	spec,wl,darkInt = connect_to_spectrometer()

	print '\n preparing data files... \n'	
	zoneList, measuredElementList, OESmaxMins, OESdataDict = prepare_for_OES_measurements(savedir, savedate)

	'''f = plt.figure()
	ax = f.add_subplot(111)
	ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
	OESfullDataDict = OESdataDict # OESfullDataDict is the entire time series of OES data for plotting'''
	
	plotCounter = 0
	while True:
		'''for zone in zoneList:
			for element in measuredElementList:
				parsedDates = []
				plotDates = []
				for eachTime in OESfullDataDict[zone]['DT']:
					parsedDates.append(datetime.strptime(OESfullDataDict[zone]['DT'], '%m/%d/%y %H:%M:%S %p'))
					plotDates.append(matplotlib.dates.date2num(parsedDates[-1]))
				print len(plotDates), len(OESfullDataDict[zone][element])
				ax.plot_date(plotDates, OESfullDataDict[zone][element], label = str(zone) + str(element))
		plt.legend()
		f.show()'''
		print '\n collecting spectra for zones ' + ', '.join(zoneList) + '... \n'
		OESdataDict = measure_allZones_OES(wl, zoneList, measuredElementList, OESmaxMins, savedir, savedate, OESdataDict, darkChannel=6)
		if plotCounter == 0:
			subprocess.Popen(['python','Y:/Nate/new MC02 OES program/backup from MC02 computer/plot PC OES 2.0.pyw'])
			plotCounter += 1
		#f.clf()
		
		
	
	mpdll.MPM_CloseConnection()

	

#connect to oceanoptics spectrometer usb2000+

'''spec = oo.get_a_random_spectrometer()

def get_and_plot_spec():
	data = spec.spectrum()
	for each in range(100):
		data[1] += spec.spectrum()[1]
	plt.plot(data[0],data[1])
	plt.show()

while True:
	channel = raw_input('enter channel: ')
	mpdll.MPM_SetChannel(int(channel))
	get_and_plot_spec()'''