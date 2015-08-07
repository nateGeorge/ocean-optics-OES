import csv, sys, re, dateutil.parser, glob, os, time, datetime
from openpyxl import load_workbook
import numpy as np
sys.path.append("Y:/Nate/git/nuvosun-python-lib/")
import nuvosunlib as nsl
from scipy import integrate
# since I have to run from the C: drive now, need to change folders into the file directory for storage files
os.chdir(os.path.dirname(os.path.realpath(__file__)))


def write_OES_data(OESdetails):
    '''
    Returns nothing, writes OESdata to oes DB as name implies.
    
    :param: OESdetails -- array of the first three columns from the allOESdata csv, which is tool, substrate, process.
    '''
    print 'writing OES data'
    '''for zone in normalizedData.keys():
        print zone
        for key in normalizedData[zone]:
            print key
            print len(normalizedData[zone][key])'''
    if OESdetails[2] == 'BE':
        for zone in BEzones:
            for rowCount in range(len(oesDataDict[zone][oesDataDict[zone].keys()[0]])):
                processedBEOEScsv.writerow(OESdetails + [zone,zoneDTs[zone][rowCount]]
                                + [oesDataDict[zone][element][rowCount] for element in elementDict.keys()] + [
                                    normalizedData[zone][key][rowCount] for key in keysToAdd])

    elif OESdetails[2] == 'PC':
        for zone in PCzones:
            for rowCount in range(len(oesDataDict[zone][oesDataDict[zone].keys()[0]])):
                # write data to file
                try:
                    processedPCOEScsv.writerow(OESdetails + [zone,zoneDTs[zone][rowCount]]
                                + [oesDataDict[zone][element][rowCount] for element in elementDict.keys()] + [
                                    normalizedData[zone][key][rowCount] for key in keysToAdd])
                except IndexError:
                    print 'index error at row:', rowCount, ', zone', zone
                    time.sleep(1)

        for rowCount in range(len(oesDataDict[zone][oesDataDict[zone].keys()[0]])):
            # calculate OES signals summed over all zones
            try:
                for key in keysToAdd:
                    normSum = 0
                    for zone in PCzones:
                        normSum += normalizedData[zone][key][rowCount]
                    normalizedDataSums[key] = normSum
                for element in elementDict.keys():
                    sum = 0
                    for zone in PCzones:
                        sum += oesDataDict[zone][element][rowCount]
                    sumOesDataDict[element] = sum
            # write the summed data to file
                processedPCOEScsv.writerow(OESdetails + ['all zones',zoneDTs['6B'][rowCount]]
                                    + [sumOesDataDict[element] for element in elementDict.keys()] + [
                                        normalizedDataSums[key] for key in keysToAdd])
            except IndexError:
                print 'index error at row', rowCount, ', zone', zone

def initialize_OES_dicts():
    for zone in (BEzones + PCzones):
        zoneDTs[zone] = []
        oesDataDict[zone] = {}
        for key in elementDict.keys():
            oesDataDict[zone][key] = []
    for key in elementDict.keys():
        sumOesDataDict[key] = []

    for zone in (BEzones + PCzones):
        normalizedData[zone] = {}
        for key in keysToAdd:
            normalizedData[zone][key] = []

    for key in keysToAdd:
        normalizedDataSums[key] = []

# sys.stdout = open('OES processessing log file.txt','wb')
# sys.stderr = open('OES processessing err file.txt','wb')

processedBEfile = 'Y:/Experiment Summaries/MC sputter tools OES/data/databases/PROCESSED all OES data BE - with normalizations.csv'
processedPCfile = 'Y:/Experiment Summaries/MC sputter tools OES/data/databases/PROCESSED all OES data PC - with normalizations.csv'
OESdbFile = 'Y:/Experiment Summaries/MC sputter tools OES/data/databases/all OES data.csv'

processedPCUpToDate, processedBEUpToDate, writtenPCruns, writtenBEruns, oldOESDTDW = nsl.get_saved_runsInprocessedOESDBList()

elementDict = nsl.OESparameters()
oesDataDict = {}
sumOesDataDict = {}
zoneDTs = {}
normalizedData = {}
normalizedDataSums = {}

# array of keys for normalization of data, used in normalizedData dict
keysToAdd = [key + '/Fi' for key in elementDict.keys()] + [key + '/Ar-811' for key in elementDict.keys()] + [
    key + '/(Fi*Ar-811)' for key in elementDict.keys()]
removeKeys = ['Fi/Fi','Ar-811/Ar-811','Fi/Ar-811','Fi/(Fi*Ar-811)','Ar-811/(Fi*Ar-811)']
for key in removeKeys:
    keysToAdd.remove(key)

BEzones = ['1B','2B','3B','4B']
PCzones = ['5A','5B','6A','6B']

# check if we've already processed the most recent OES data
OESreader = csv.reader(open(OESdbFile, 'rb'), delimiter=',')

# write headers to BE file
processedBEOEScsv = csv.writer(open(processedBEfile, 'wb'), delimiter=',')
processedBEOEScsv.writerow(['tool', 'substrate', 'process', 'zone', 'datetime'] + elementDict.keys() + keysToAdd)

# write headers to PC file
processedPCOEScsv = csv.writer(open(processedPCfile, 'wb'), delimiter=',')
processedPCOEScsv.writerow(['tool', 'substrate', 'process', 'zone', 'datetime'] + elementDict.keys() + keysToAdd)

importedWavelengths = False

BEruns = {}
PCruns = {}
OESDTDW = {}
OESDTDW['BE'] = {}
OESDTDW['PC'] = {}

tempRowCount = 0  # for sampling small amount of OESdbFile
firstSubstrate = True
fileWritten = False
lastRun = 0

rowLabels = {'tool': 0, 'substrate': 1, 'process': 2, 'zone': 3, 'datetime': 4}
for row in OESreader:
    if importedWavelengths:
        '''if row[2] != 'PC':
            continue
        tempRowCount +=1
        if tempRowCount == 1000:
            break'''
        #if not re.search('(\d\d\d)',row[1]): # temporary fix for accidental extra label row in middle of db file
        #    continue

        currentRunNumber = int(re.search('(\d\d\d)', row[1]).group(1))

        # for temporary testing, only includes first run
        #if currentRunNumber != 421:
		#    break


        # if currentRunNumber == 426:
        #   print tempRowCount
        if lastRun != currentRunNumber:
            if currentRunNumber not in PCruns.keys():
                if not firstSubstrate and not fileWritten:
                    write_OES_data(lastOESdetails)
                    fileWritten = True
                initialize_OES_dicts()
                if row[2] == 'PC':
                    if currentRunNumber in writtenPCruns:
                        print 'skipping run', currentRunNumber, 'cause already in processed file'
                        lastRun = currentRunNumber
                        continue
                    print 'adding', currentRunNumber, 'to PC runs'
                    PCruns[currentRunNumber] = {}
                    PCruns[currentRunNumber]['tool'] = row[0]
                    lastOESdetails = row[:3] # tool, substrate, process -- for writing to processed file
                    lastRun = currentRunNumber
                    OESDTDW['PC'][currentRunNumber] = {}
                    OESDTDW['PC'][currentRunNumber]['DT'] = []
                    OESDTDW['PC'][currentRunNumber]['DW'] = []
                    # for runs less than 438, hadn't replaced broken optical cable on the outside of mc02 for Z6B
                    Z6BrowCount = 0
                    Z6ArawSpec = []

            if currentRunNumber not in BEruns.keys():
                if not firstSubstrate and not fileWritten:
                    write_OES_data(lastOESdetails)
                firstSubstrate = False
                initialize_OES_dicts()
                if row[2] == 'BE':
                    if currentRunNumber in writtenBEruns:
                        print 'skipping run', currentRunNumber, 'cause already in processed file'
                        lastRun = currentRunNumber
                        continue
                    print 'adding', currentRunNumber, 'to BE runs'
                    BEruns[currentRunNumber] = {}
                    BEruns[currentRunNumber] = row[0]
                    lastOESdetails = row[:3] # tool, substrate, process -- for writing to processed file
                    lastRun = currentRunNumber
                    OESDTDW['BE'][currentRunNumber] = {}
                    OESDTDW['BE'][currentRunNumber]['DT'] = []
                    OESDTDW['BE'][currentRunNumber]['DW'] = []

            fileWritten = False
            firstSubstrate = False

        # tool,currentRun,process,zone,currentDatetime = row[:5]
        # didn't have Z6B working (broken before 438, unplugged for 448), set 6B spectra equal to 6A
        if row[rowLabels['process']] == 'PC' and (currentRunNumber <= 438 or currentRunNumber == 448):
            if row[3] == '6A':
                rawSpectrum = np.array(row[5:], dtype='float64')
                Z6ArawSpec.append(rawSpectrum)
            elif row[3] == '6B':
                # the allOESdata file is ordered by zones, so need to go through all 6A data first, then all 6B
                rawSpectrum = Z6ArawSpec[Z6BrowCount]
                Z6BrowCount += 1
            else:
                rawSpectrum = np.array(row[5:], dtype='float64')
        else:
            rawSpectrum = np.array(row[5:], dtype='float64')

        if currentRunNumber == 421:  # hadn't implemented correct dark spectrum subtraction for 421, so need to correct for it here
            zeroingFactor = np.average(rawSpectrum[normMinIndex:normMaxIndex])
            rawSpectrum = rawSpectrum - zeroingFactor

            
        # add datetimes to the appropriate arrays, and integrate and normalize the various elemental signals
        zoneDTs[row[3]].append(row[4]) # row[3] is zone, row[4] datetime
        # add integration of OES signals
        for element in elementDict.keys():
            oesDataDict[row[3]][element].append(integrate.simps(
                rawSpectrum[elementDict[element]['minWLindex']:elementDict[element]['maxWLindex']],
                wl[elementDict[element]['minWLindex']:elementDict[element]['maxWLindex']]))
        # calculate normalizations 
        for key in keysToAdd:
            if key[-2:] == 'Fi':
                normalizedData[row[3]][key].append(oesDataDict[row[3]][key[:-3]][-1] / oesDataDict[row[3]]['Fi'][-1])
            elif key[-6:] == 'Ar-811':
                normalizedData[row[3]][key].append(oesDataDict[row[3]][key[:-7]][-1] / oesDataDict[row[3]]['Ar-811'][-1])
            elif key[-11:] == '(Fi*Ar-811)':
                normalizedData[row[3]][key].append(oesDataDict[row[3]][key[:-12]][-1] / (
                    oesDataDict[row[3]]['Fi'][-1] * oesDataDict[row[3]]['Ar-811'][-1]))

        if row[2] == 'BE':
            OESDTDW['BE'][currentRunNumber]['DT'].append(row[4])
        if row[2] == 'PC':
            OESDTDW['PC'][currentRunNumber]['DT'].append(row[4])

    else:
        wl = np.array(row[5:], dtype='float64')
        importedWavelengths = True
        ArMinIndex, ArMaxIndex = nsl.get_WL_indices(745.0, 760.0,
                                                    wl)  # gets wl indices for ar peak to detect if plasma is on or not
        normMinIndex, normMaxIndex = nsl.get_WL_indices(200.0, 250.0,
                                                        wl)  # gets wl indices for adjusting spectra to correct 0 for run 421

# need to write the last data we collected before moving on
write_OES_data(lastOESdetails)

# update OESDTDW array so we can save the whole thing

for proc in ['BE','PC']:
    if oldOESDTDW != None:
        for run in oldOESDTDW[proc].keys():
            OESDTDW[proc][run] = oldOESDTDW[proc][run]


nsl.set_saved_runsInprocessedOESDBList(PCruns.keys(), BEruns.keys(), OESDTDW)