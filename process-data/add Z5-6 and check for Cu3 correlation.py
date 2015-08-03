import pandas as pd

#effFile = 'Y:/Nate/OES/databases/OES-XRF-eff-data.csv'
#processedPCfile = 'Y:/Nate/OES/databases/PROCESSED all OES data PC - with normalizations.csv'
effFile = 'Y:/Nate/OES/databases/up to 450/OES-XRF-eff-data.csv'
processedPCfile = 'Y:/Nate/OES/databases/up to 450/PROCESSED all OES data PC - with normalizations and XRF.csv'


oesDF = pd.DataFrame.from_csv(processedPCfile)

print oesDF.columns
oesByRun = oesDF.groupby(['substrate','zone'])
for name, group in oesByRun:
    print name
    print name[1]