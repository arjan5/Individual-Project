import sys
import os
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Timetable(QWidget):


    def __init__(self):
        super().__init__()

        # temporary but in final version it will allow user to upload a file
        os.chdir('/users/arjan/downloads/uni yr3/Individual Project/ics files/')
        # initialise the arrays that will be used to store data
        self.main = []
        self.temp = []
        self.asynchronousData = []

        self.days = []
        self.dayOfTheWeek = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
        4:'Thursday', 5:'Friday', 6: 'Saturday', 7:'Sunday'}
        self.numOfWeeks = []

        # stores the date with the id from main list
        self.datesDict = {}

        # calls the functions required to initalise the app
        self.readFile()
        self.findWeeks()
        self.sortAsynchronous()
        self.initUI()


    def initUI(self):

        self.uniWeek = QComboBox(self)
        self.uniWeek.setGeometry(50, 60, 100, 30)
        self.uniWeek.addItems(self.numOfWeeks)
        self.uniWeek.currentTextChanged.connect(self.lelel)

        self.label1 = QLabel('month and yr', self)
        self.label1.setGeometry(50, 150, 200, 30)

        self.setGeometry(300, 300, 500, 400)
        self.setWindowTitle('Timetable')
        self.show()


    def lelel(self, value):
        value = value.split(' ')[1]
        print(value)


    def findWeeks(self):
        format = "%d/%m/%Y"
        for i in self.main:
            d = [m for m in i if 'DTSTART' in m][0]
            date = d.split(':')[1].split('T')[0]
            date = datetime.datetime(int(date[:4]), int(date[4:6]), int(date[6:]))
            date = date.strftime(format)
            self.datesDict[str(self.main.index(i))] = date
        self.yuhsih = dict(sorted(self.datesDict.items(), key = lambda date: datetime.datetime.strptime(date[1], "%d/%m/%Y")))
        # print(self.yuhsih)
        weekNumArray = []
        for k,v in self.yuhsih.items():
            t = self.splitDate(v)
            if t[0] not in weekNumArray:
                weekNumArray.append(t[0])
            print(t)
        self.numOfWeeks = ['Week ' + str(x) for x in range(1, len(weekNumArray)+1)]


    def splitDate(self, date):
        split = date.split('/')
        datetimeObj = datetime.datetime(int(split[2]), int(split[1]), int(split[0]))
        day = split[0]
        weekDayNum = datetimeObj.isocalendar()[2]
        weekNum = datetimeObj.isocalendar()[1]
        return [weekNum, weekDayNum]


    def checkLen(self):
        if len(self.month) == len(self.main):
            return True
        else:
            return False


    # reads the file
    def readFile(self):
        with open('main.ics', 'r') as f:
            for line in f:
                # stores data between begin:vevent and end:vevent
                if line.strip() == 'BEGIN:VEVENT':
                    self.temp = []
                    self.temp.append(line.strip())
                elif line.strip() == 'END:VEVENT':
                    self.temp.append(line.strip())
                    self.main.append(self.temp)
                    self.temp = []
                elif line.strip() == 'BEGIN:VCALENDAR':
                    continue
                else:
                    self.temp.append(line.strip())


    def sortAsynchronous(self):
        status = []
        for i in range(len(self.main)):
            loc = [s for s in self.main[i] if 'LOCATION' in s][0]
            n = loc.split(' ')[-1].replace('(', '').replace(')', '')
            status.append(n)

        self.indexes = [i for i, x in enumerate(status) if x == 'Asynchronous']


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("calendar.png"))
    main = Timetable()
    app.setQuitOnLastWindowClosed(True)
    sys.exit(app.exec_())