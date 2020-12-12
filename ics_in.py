import os
from constraint import *
from icalendar import Calendar, Event
import datetime

os.chdir('/users/arjan/downloads/uni yr3/Individual Project/ics files/')

main = []
temp = []

# read ics file
with open('main.ics', 'r') as f:
    # read line by line
    for line in f:
        # stores data between begin:vevent and end:vevent
        if line.strip() == 'BEGIN:VEVENT':
            temp = []
            temp.append(line.strip())
        elif line.strip() == 'END:VEVENT':
            temp.append(line.strip())
            main.append(temp)
            temp = []
        elif line.strip() == 'BEGIN:VCALENDAR':
            continue
        else:
            temp.append(line.strip())

status = []
for i in range(len(main)):
    loc = [s for s in main[i] if 'LOCATION' in s][0]
    n = loc.split(' ')[-1].replace('(', '').replace(')', '')
    status.append(n)

indexes = [i for i, x in enumerate(status) if x == 'Asynchronous']

current_asyn = main[indexes[0]]
module = [m for m in current_asyn if 'DESCRIPTION' in m]
module = module[0].split(':')[1].split('\\')[0]

format = '%d/%m/%Y %H:%M:%S'
start_data = [d for d in current_asyn if 'DTSTART' in d][0]
start_date = start_data.split(':')[1].split('T')[0]
start_time = start_data.split(':')[1].split('T')[1].split('Z')[0]
start_date = datetime.datetime(int(start_date[:4]), int(start_date[4:6]), int(start_date[6:]))
start_date = start_date.strftime("%d/%m/%Y")
start_time = datetime.time(int(start_time[:2]), int(start_time[2:4]), int(start_time[4:]))
start_time = start_time.strftime("%H:%M:%S")
startDateTime = start_date + ' ' + start_time
startDateTime = datetime.datetime.strptime(startDateTime, format)
print(startDateTime.weekday())
end_data = [d for d in current_asyn if 'DTEND' in d][0]
end_date = end_data.split(':')[1].split('T')[0]
end_time = end_data.split(':')[1].split('T')[1].split('Z')[0]
end_date = datetime.datetime(int(end_date[:4]), int(end_date[4:6]), int(end_date[6:]))
end_date = end_date.strftime("%d/%m/%Y")
end_time = datetime.time(int(end_time[:2]), int(end_time[2:4]), int(end_time[4:]))
end_time = end_time.strftime("%H:%M:%S")
endDateTime = end_date + ' ' + end_time
endDateTime = datetime.datetime.strptime(endDateTime, format)

diff = str(endDateTime - startDateTime)

cal = Calendar()


# morning = 8am-12pm
preference = 'morning'

problem = Problem()
problem.addVariable("a", [1,2,3])
problem.addVariable("b", [4,5,6])
# print(problem.getSolutions())
problem.addConstraint(lambda a, b: a*2 == b,
                        ("a", "b"))
# print(problem.getSolutions())
