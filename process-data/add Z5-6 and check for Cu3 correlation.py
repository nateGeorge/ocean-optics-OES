import time
import pandas as pd

#effFile = 'Y:/Nate/OES/databases/OES-XRF-eff-data.csv'
#processedPCfile = 'Y:/Nate/OES/databases/PROCESSED all OES data PC - with normalizations.csv'
effFile = 'Y:/Nate/OES/databases/up to 450/OES-XRF-eff-data.csv'
processedPCfile = 'Y:/Nate/OES/databases/up to 450/PROCESSED all OES data PC - with normalizations and XRF.csv'


oesDF = pd.DataFrame.from_csv(processedPCfile)

#print oesDF.columns
oesByRun = oesDF.groupby(['substrate'])
for name, group in oesByRun:
    runData = group.groupby(['zone'])
    sumZ5 = runData['5A'] + runData['5B']
    for zone, grp in sumZ5:
        print zone
        for each in grp:
            print each
            if each == 'Cu-515':
                for row in grp[each]:
                    print row
                    time.sleep(0.3)