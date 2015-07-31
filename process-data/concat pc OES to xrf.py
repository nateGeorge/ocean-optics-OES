import csv, sys, re, dateutil.parser, glob, os, time, datetime
from openpyxl import load_workbook
import numpy as np
import traceback as tb
sys.path.append("Y:/Nate/git/nuvosun-python-lib/")
import nuvosunlib as nsl
from scipy import integrate
# since I have to run from the C: drive now, need to change folders into the file directory for storage files
os.chdir(os.path.dirname(os.path.realpath(__file__)))


processedPCfile = 'Y:/Nate/OES/databases/PROCESSED all OES data PC - with normalizations.csv'
processedBEfile = 'Y:/Nate/OES/databases/PROCESSED all OES data BE - with normalizations.csv'

processedPCUpToDate, processedBEUpToDate, writtenPCruns, writtenBEruns, OESDTDW = nsl.get_saved_runsInprocessedOESDBList()

XRFdata = nsl.get_XRF_data(sorted(writtenPCruns),minDW=-15.0)

XRFkeysToInterp = sorted(XRFdata[XRFdata.keys()[0]].keys())
XRFkeysToInterp.remove('DT')
min_maxXRFtimes = {}

for run in sorted(writtenPCruns):
    min_maxXRFtimes[run] = {}
    min_maxXRFtimes[run]['min'] = float(XRFdata[str(run)]['DT'][0])
    min_maxXRFtimes[run]['max'] = float(XRFdata[str(run)]['DT'][-1])
    for key in XRFkeysToInterp:
        OESDTDW['PC'][run][key] = np.interp(OESDTDW['PC'][run]['DT'], XRFdata[str(run)]['DT'],
                                            XRFdata[str(run)][key])  # xrfDTforInterp, xrfDWforInterp)
    # print len(OESDTforInterp), len(OESDTDW['PC'][run]['DT']), len(DWfromXRF[run]['DT']), len(DWfromXRF[run]['DW'])

processedPCOESreader = csv.reader(open(processedPCfile, 'rb'), delimiter=',')
notLabels = False
OESpcProcData = {}
for row in processedPCOESreader:
    if notLabels:
        currentRunNumber = int(re.search('(\d\d\d)', row[1]).group(1))
        if currentRunNumber not in OESpcProcData.keys():
            try:
                print 'adding XRF data to run ', currentRunNumber, '.  len of DW array:', len(OESDTDW['PC'][currentRunNumber]['DW'])
                OESpcProcData[currentRunNumber] = []
                rowCounter = 0
                atAllZones = False
            except Exception as e:
                print sys.exc_info()
                #print tb.print_tb(sys.exc_info()[2])
        try:
            if row[3] == 'all zones' and not atAllZones:
                rowCounter = rowCounter - len(OESDTDW['PC'][currentRunNumber]['DT'])
                atAllZones = True
            '''print row[4]
            print min_maxXRFtimes[currentRunNumber]
            print float(row[4]) - min_maxXRFtimes[currentRunNumber]['min']
            print min_maxXRFtimes[currentRunNumber]['max'] - float(row[4])'''
            if float(row[4]) >= min_maxXRFtimes[currentRunNumber]['min'] and float(row[4]) <= min_maxXRFtimes[currentRunNumber]['max']:
                print 'within bounds'
                OESpcProcData[currentRunNumber].append(
                row + [OESDTDW['PC'][currentRunNumber][key][rowCounter] for key in XRFkeysToInterp])
        except IndexError:
            print rowCounter, len(OESDTDW['PC'][currentRunNumber]['DW']), currentRunNumber
            print 'index error'
        except Exception as e:
                print sys.exc_info()
                #print tb.print_tb(sys.exc_info()[2])
        rowCounter += 1
    else:
        labels = row + XRFkeysToInterp
        notLabels = True  

PCOEScsvWithDW = csv.writer(open(processedPCfile[:-4] + ' and XRF.csv', 'wb'), delimiter=',')
PCOEScsvWithDW.writerow(labels)
print OESpcProcData.keys()
for run in OESpcProcData.keys():
    PCOEScsvWithDW.writerows(OESpcProcData[run])
            