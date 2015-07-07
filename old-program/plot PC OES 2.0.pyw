from datetime import datetime
import csv, matplotlib.dates, matplotlib, math
import easygui as eg
import pylab as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates
import numpy as np

#matplotlib.rcParams.update({'font.size': 22})

savedate = datetime.strftime(datetime.now(),'%m-%d-%y') #made DT format similar to data system format
savedir = 'C:/OESdata/' + 'PC ' + savedate + '/'


def create_oesdict():
	#make list of elements and zones measured
	zoneList = ['5A','5B','6A','6B']
	elementList = ['Cu','In','Ga','Se','Ar','Na','Mo','Ti','O2','H2']
	measuredElementList = elementList #use this: ['Cu', 'In', 'Ga', 'Ar', 'O2', 'H2'] to restrict list as needed
	combinedList = [zone + ' ' + element for zone in zoneList for element in measuredElementList] #Combines list like 5A Cu, 5A In, etc...
	'''OESdataDict = {}
	for each in combinedList:
		OESdataDict['DT'+each]=[]'''
	OESdataDict={}
	for zone in zoneList:
		OESdataDict[zone] = {}
		OESdataDict[zone]['DT'] = []
		for element in measuredElementList:
			OESdataDict[zone][element]= []
			
	return OESdataDict,zoneList,measuredElementList

def getdata():
	OESdataDict,zoneList,measuredElementList=create_oesdict()
	with open(savedir + savedate + ' -- OES signals.csv', 'rb') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		firstRow = True
		for row in spamreader:
			if not firstRow and row[-1]!='':
				for zoneCount in range(len(zoneList)):
					OESdataDict[zoneList[zoneCount]]['DT'].append(datetime.strptime(row[0],'%m/%d/%y %H:%M:%S %p'))
					for elCount in range(len(measuredElementList)):
						OESdataDict[zoneList[zoneCount]][measuredElementList[elCount]].append(row[1+zoneCount*len(measuredElementList)+elCount])
			else: #skips first row which is labels
				firstRow = False
	'''for zone in zoneList:
		OESdataDict[zone]['DT']=np.array(OESdataDict[zone]['DT'])
		for element in measuredElementList:
			OESdataDict[zone][element]=np.array(OESdataDict[zone][element],dtype='float64')'''

	return OESdataDict
				
def plotdata(*args):
		plt.clf()
		OESdataDict = getdata()
		Cu3 = {}
		CuSum = 0
		InSum = 0
		GaSum = 0
		
		Cu3total = 0
		for zone in OESdataDict.keys():
			Cu3[zone] = float(OESdataDict[zone]['Cu'][-1])/(float(OESdataDict[zone]['In'][-1])+float(OESdataDict[zone]['Ga'][-1]))
			
			CuSum += float(OESdataDict[zone]['Cu'][-1]) / float(OESdataDict[zone]['Ar'][-1])
			InSum += float(OESdataDict[zone]['In'][-1]) / float(OESdataDict[zone]['Ar'][-1])
			GaSum += float(OESdataDict[zone]['Ga'][-1]) / float(OESdataDict[zone]['Ar'][-1])
			
			if zone != '6A': #exclude zone 6A for now cause it's junk
				Cu3total += Cu3[zone]
			Cu3[zone] = math.ceil(Cu3[zone]*100)/100.0
		Cu3total = Cu3total/3 #average from 4 zones
		Cu3total = math.ceil(Cu3total*100)/100.0
		Cu3Sumtotal = CuSum / (InSum + GaSum)
		Cu3Sumtotal = math.ceil(Cu3Sumtotal*100)/100.0
		Cu3total *=1.446

		# plot the data
		zoneChoices = ['5A', '5B', '6A','6B'] 
		elementsToPlot = {'Ar' : '#b2b2b2', 'Cu' : '#b2b2b2', 'In', '#0099ff', 'Na' : '#009933', 'Ga' : '#ff5c33'} # dict of elements and colors for plotting
		ax5A = plt.subplot2grid((2, 2), (0,0), axisbg='k')
		ax5B = plt.subplot2grid((2, 2), (1,0), axisbg='k')
		ax6A = plt.subplot2grid((2, 2), (0,1), axisbg='k')
		ax6B = plt.subplot2grid((2, 2), (1,1), axisbg='k')
		
		for zone in zoneChoices:
			OESdates = matplotlib.dates.date2num(OESdataDict[zone]['DT'])
		
			# changes ticks and axes to white color
			eval('ax' + zone).tick_params(color='w',labelcolor='w')
			for spine in eval('ax' + zone).spines.values():
				spine.set_edgecolor('w')
		
			eval('ax'+zone).xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
			
			for element in elementsToPlot.keys():
				eval('ax'+zone).plot_date(OESdates, OESdataDict[zone][element], color = elementsToPlot[element])
				eval('ax'+zone).plot_date(OESdates, OESdataDict[zone][element], '-', color = elementsToPlot[element], linewidth = 4, label = element)
				eval('ax'+zone).set_title(zone, color = 'w')
				eval('ax'+zone).grid(color='w', linewidth=2)
		
		ax5A.set_ylabel('OES integrated intensity', color='w')
		ax5B.set_xlabel('time', color='w')
		
		legend = ax5A.legend(bbox_to_anchor=(0.2, 1.1), loc='upper right', borderaxespad=0., shadow=True, labelspacing=0, numpoints=1)
		# The frame is matplotlib.patches.Rectangle instance surrounding the legend.
		frame = legend.get_frame()
		frame.set_facecolor('0.90')
			# Set the fontsize
		#for label in legend.get_texts():
		#	label.set_fontsize('25')
		#ax1.set_ylim([0,60])
		#ax1.axhline(45,ls='--',color='#ff0000',linewidth=4)
		
		cu3stringlist = [str(zone)+ ':' + str(Cu3[zone]) for zone in sorted(Cu3.keys())]
		cu3string = ''
		for each in cu3stringlist:
			cu3string += each + ' ' 
		plt.figtext(0.6,0.95,'Cu3: ' + cu3string,fontsize=12,color='white')
		plt.figtext(0.6,0.92,'overall Cu3: ' + str(Cu3total),fontsize=12,color='white')
		#plt.title('OES zone ' + zoneToPlot,color='w')
		fig.canvas.set_window_title('OES zones ' + zoneChoices[0] + ' - ' + zoneChoices[-1])
		
fig=plt.figure(facecolor='k')

#plt.xlabel('Time',color='w')

'''
msg ="choose a zone to plot"
title = "plot OES spectra"
zoneChoices = ['1B','2B','5A','5B','6A','6B']
global zoneToPlot
zoneToPlot = eg.choicebox(msg, title, zoneChoices)'''

ani = animation.FuncAnimation(fig, plotdata, interval=15000)
#fig.subplots_adjust(bottom=0.1, left=0.05, right=0.9, top=0.95)
plt.show()