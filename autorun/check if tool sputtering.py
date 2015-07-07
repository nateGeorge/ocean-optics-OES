import subprocess, datetime, re
from openpyxl import load_workbook

today = datetime.datetime.now()
    
schedF = ns.getLatestScheduleFile()

wb = load_workbook(schedF, data_only=True)
whiteBoardWS = wb.get_sheet_by_name("White Board")
rowCount = 0
for row in whiteBoardWS.iter_rows():
    if row[0].value == 'MC01':
        MC01row = rowCount
    elif row[0].value == 'MC02':
        MC02row = rowCount
    elif row[0].value == 'MC03':
        MC03row = rowCount
    elif row[0].value == 'LC1':
        LC1row = rowCount
    rowCount +=1
for column in whiteBoardWS.columns:
    try:
        columnDate = column[1].value
        if columnDate.year == today.year and columnDate.month == today.month and columnDate.day == today.day:
            if column[MC02row].value == None:
				print 'starting monitor for BE or PC start'
                subprocess.Popen(['python','Y:/Nate/new MC02 OES program/backup from MC02 computer/monitorProcessStart.pyw','PC+BE'])
            elif re.search('BE', column[MC02row].value):
				print 'starting monitor for BE start, run', runNum
                runNum = re.search('\d\d\d', column[MC02row].value)
                subprocess.Popen(['python','Y:/Nate/new MC02 OES program/backup from MC02 computer/monitorProcessStart.pyw','BE',runNum])
            elif re.search('PC', column[MC02row].value):
				print 'starting monitor for PC start, run', runNum
                runNum = re.search('\d\d\d', column[MC02row].value)
                subprocess.Popen(['python','Y:/Nate/new MC02 OES program/backup from MC02 computer/monitorProcessStart.pyw','BE',runNum])
            elif re.search('PM', column[MC02row].value):
                exit()
    except Exception as e:
        print e