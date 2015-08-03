import time, csv
import pandas as pd
import numpy as np

def is_outlier(points, thresh=15):
    """
    Returns a boolean array with True if points are outliers and False 
    otherwise.

    Parameters:
    -----------
        points : An numobservations by numdimensions array of observations
        thresh : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value will be classified as outliers.

    Returns:
    --------
        mask : A numobservations-length boolean array.

    References:
    ----------
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
    """
    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh

#effFile = 'Y:/Nate/OES/databases/OES-XRF-eff-data.csv'
#processedPCfile = 'Y:/Nate/OES/databases/PROCESSED all OES data PC - with normalizations.csv'
effFile = 'Y:/Nate/OES/databases/up to 450/OES-XRF-eff-data.csv'
processedPCfile = 'Y:/Nate/OES/databases/up to 450/PROCESSED all OES data PC - with normalizations and XRF.csv'


oesDF = pd.DataFrame.from_csv(processedPCfile)
comboAmnts = np.array(range(10))/10.0
comboAmnts = np.append(comboAmnts,1.0)
with open('Y:\Nate\OES\databases\Z5-6 sums.csv','wb') as csvfile:
    sumsWriter = csv.writer(csvfile, delimiter=',')
    sumsWriter.writerow(['substrate','Cu3','DW'] + ['Cu-515/In-451 5A*' + str(amnt) + ' 5B*' + str(1-amnt) for amnt in comboAmnts])

#print oesDF.columns
oesByRun = oesDF.groupby(['substrate'])
for name, group in oesByRun:
    print 'run:',name
    Z5sums = {}
    outliers = []
    runData = group.groupby(['zone'])
    print 'expected length 5A, 5B:',len(runData.get_group('5A')['Cu-515']), len(runData.get_group('5B')['Cu-515'])
    # sometimes one dataset is longer than the other by one
    if len(runData.get_group('5A')['Cu-515']) != len(runData.get_group('5B')['Cu-515']):
        minIndex = min(len(runData.get_group('5A')['Cu-515']), len(runData.get_group('5B')['Cu-515']))
    else:
        minIndex = len(runData.get_group('5A')['Cu-515'])
    Z5AOESratio = runData.get_group('5A')['Cu-515'][:minIndex]/runData.get_group('5A')['In-451'][:minIndex]
    Z5BOESratio = runData.get_group('5B')['Cu-515'][:minIndex]/runData.get_group('5B')['In-451'][:minIndex]
    for amnt in comboAmnts:
        Z5sums['Cu-515/In-451 5A*' + str(amnt) + ' 5B*' + str(1-amnt)] = (amnt*Z5AOESratio + (1-amnt)*Z5BOESratio)
        Z5sums['Cu3'] = (runData.get_group('5A')['Cu3'][:minIndex] + runData.get_group('5B')['Cu3'][:minIndex])/2
        Z5sums['DW'] = (runData.get_group('5A')['DW'][:minIndex] + runData.get_group('5B')['DW'][:minIndex])/2
        outliers.append(is_outlier(Z5sums['Cu-515/In-451 5A*' + str(amnt) + ' 5B*' + str(1-amnt)]))
        outliers.append(is_outlier(Z5sums['Cu3']))
        print len(Z5sums['Cu-515/In-451 5A*' + str(amnt) + ' 5B*' + str(1-amnt)]), len(Z5sums['Cu3'])
    with open('Y:\Nate\OES\databases\Z5-6 sums.csv','ab') as csvfile:
        sumsWriter = csv.writer(csvfile, delimiter=',')
        for cnt in range(len(Z5sums['Cu3'])):
            if cnt not in outliers:
                sumsWriter.writerow([name,Z5sums['Cu3'][cnt],Z5sums['DW'][cnt]] + [Z5sums['Cu-515/In-451 5A*' + str(amnt) + ' 5B*' + str(1-amnt)][cnt] for amnt in comboAmnts])