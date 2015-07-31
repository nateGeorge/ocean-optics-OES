import sys, csv, os
import numpy as np
import traceback as tb
sys.path.append("Y:/Nate/git/nuvosun-python-lib/")
import nuvosunlib as nsl
# since I have to run from the C: drive now, need to change folders into the file directory for storage files
os.chdir(os.path.dirname(os.path.realpath(__file__)))

upToDate, OESmtime, runsInDB, runDatesInDB = nsl.get_saved_runsInOESDBList()

processedPCfile = 'Y:/Nate/OES/databases/PROCESSED all OES data PC - with normalizations.csv'
effFile = 'Y:/Nate/OES/databases/OES-XRF-eff-data.csv'

effDataTypes = ['Cell Eff Avg',
        'Cell Voc Avg','Cell Jsc Avg','Cell FF Avg','Cell Rs Avg','Cell Rsh Avg']

# concatenate OES data to efficiency
runs = []
# load PCOES data with DW and XRF
PCOESandXRFdata = {}
PCOESandXRFdataSubs = {} # with primary keys as substrates
PCOEScsvWithDWreader = csv.DictReader(open(processedPCfile[:-4] + ' and XRF.csv', 'rb'))
for row in PCOEScsvWithDWreader:
    for key, value in row.iteritems():
        PCOESandXRFdata.setdefault(key,[]).append(value)

charKeys = ['substrate', 'zone', 'process', 'tool', 'datetime']

print PCOESandXRFdata.keys()
for count in range(len(PCOESandXRFdata['DW'])):
    run = PCOESandXRFdata['substrate'][count]
    zone = PCOESandXRFdata['zone'][count]
    PCOESandXRFdataSubs.setdefault(run,{})
    PCOESandXRFdataSubs[run].setdefault(zone,{})
    for key in PCOESandXRFdata.keys():
        if key not in charKeys:
            PCOESandXRFdataSubs[run][zone].setdefault(key,[]).append(PCOESandXRFdata[key][count])
         
#print sorted(PCOESandXRFdataSubs.keys())
#print PCOESandXRFdataSubs['332'].keys()
OESpcDataConcatWithEff = {}


effDataSubs = nsl.effData_by_substrate(nsl.import_eff_file(substrateRange = [330,500]))


#print sorted(effDataSubs.keys())
for run in sorted(PCOESandXRFdataSubs.keys()):
    print 'interpolating', run
    for zone in sorted(PCOESandXRFdataSubs[run].keys()):
        OESpcDataConcatWithEff.setdefault(run,{})
        OESpcDataConcatWithEff[run].setdefault(zone,{})
        for key in PCOESandXRFdataSubs[run][zone].keys():
            if key != 'DW':
                OESpcDataConcatWithEff[run][zone][key] = nsl.interp_to_eff(np.array(effDataSubs[int(run)]['DW'], dtype='float64'),np.array(PCOESandXRFdataSubs[run][zone]['DW'], dtype='float64'),np.array(PCOESandXRFdataSubs[run][zone][key], dtype='float64'))
            '''try:
                OESpcDataConcatWithEff[run][zone][key] = nsl.interp_to_eff(np.array(effDataSubs[int(run)]['DW'], dtype='float64'),np.array(PCOESandXRFdataSubs[run][zone]['DW'], dtype='float64'),np.array(PCOESandXRFdataSubs[run][zone][key], dtype='float64'))
            except Exception as e:
                print tb.print_tb(sys.exc_info()[2])'''

oesxrfeffKeys = sorted(OESpcDataConcatWithEff[run][zone].keys())
effKeys = sorted(effDataSubs[int(run)].keys())
with open(effFile,'wb') as csvfile:
    csvWriter = csv.writer(csvfile, delimiter = ',')
    csvWriter.writerow(['substrate','zone'] + oesxrfeffKeys + effKeys)
    for run in sorted(OESpcDataConcatWithEff.keys()):
        for zone in sorted(OESpcDataConcatWithEff[run].keys()):
            try:
                for count in range(len(OESpcDataConcatWithEff[run][zone]['H-656'])):
                    csvWriter.writerow([run,zone] + [OESpcDataConcatWithEff[run][zone][key][count] for key in oesxrfeffKeys] + [effDataSubs[int(run)][key][count] for key in effKeys])
            except Exception as e:
                sys.exc_info()