import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os
import datetime

class Test(QWidget):

    def __init__(self):
        super().__init__()

        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                    'Saturday', 'Sunday']

        self.partOfDay = {'Early Morning': '05:00:00 - 08:00:00',
                        'Late Morning': '08:00:00 - 12:00:00',
                        'Afternoon': '12:00:00 - 17:00:00',
                        'Evening': '17:00:00 - 21:00:00',
                        'Early Night': '21:00:00 - 00:00:00',
                        'Late Night': '00:00:00 - 05:00:00'}

        os.chdir('/users/arjan/downloads/uni yr3/Individual Project/ics files/')
        self.main = []
        temp = []
        with open('main.ics', 'r') as f:
            for line in f:
                if line.strip() == 'BEGIN:VEVENT':
                    temp = []
                    temp.append(line.strip())
                elif line.strip() == 'END:VEVENT':
                    temp.append(line.strip())
                    self.main.append(temp)
                    temp = []
                elif line.strip() == 'BEGIN:VCALENDAR':
                    continue
                else:
                    temp.append(line.strip())

        status = []
        for i in range(len(self.main)):
            loc = [s for s in self.main[i] if 'LOCATION' in s][0]
            n = loc.split(' ')[-1].replace('(', '').replace(')', '')
            status.append(n)

        indexes = [i for i, x in enumerate(status) if x == 'Asynchronous']
        self.asyn = []
        for i in indexes:
            stuff = self.getAsynInfo(i)
            # 0 = module, 1 = date, 2 = length
            self.asyn.append(stuff)

        self.initUI()


    def initUI(self):

        self.label = QLabel('stuff', self)
        self.label.setGeometry(50, 50, 50, 30)

        self.dayOfWeek = QListWidget(self)
        self.dayOfWeek.setGeometry(20, 100, 100, 30)
        self.dayOfWeek.addItems(self.days)
        self.dayOfWeek.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.dayOfWeek.setMinimumHeight(130)

        self.list_wid = QListWidget(self)
        self.list_wid.setGeometry(130, 100, 100, 30)
        self.list_wid.addItems(self.partOfDay)
        self.list_wid.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_wid.setMinimumHeight(110)

        self.lis = [x[0] + ' ' + x[1] for x in self.asyn if x[0] and x[1]]

        self.combo_box = QComboBox(self)
        self.combo_box.setGeometry(50, 230, 100, 30)
        self.combo_box.addItems(self.lis)
        item = self.lis[0]
        self.combo_box.setCurrentText(item)
        self.combo_box.adjustSize()
        self.combo_box.activated[str].connect(self.onActivated)

        self.bt1 = QPushButton('push me', self)
        self.bt1.setGeometry(75, 260, 100, 30)
        self.bt1.clicked.connect(self.doSomething)

        self.tree = QTreeWidget(self)
        self.tree.setGeometry(250, 20, 200, 200)
        self.headerItem = QTreeWidgetItem()
        self.item = QTreeWidgetItem()
        for i in range(len(self.asyn)):
            parent = QTreeWidgetItem(self.tree)
            parent.setText(0, self.lis[i])
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for x in range(5):
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, "Child {}".format(x))
                child.setCheckState(0, Qt.Unchecked)
        self.tree.show()

        self.setGeometry(300, 300, 500, 400)
        self.setWindowTitle('Test')
        self.show()

    def onActivated(self, text):
        index = self.combo_box.currentIndex()
        self.label.setText(self.asyn[index][0] + ' on ' + self.asyn[index][1] + ' lasts for ' + self.asyn[index][2])
        self.label.adjustSize()


    def doSomething(self):
        try:
            print(self.dayOfWeek.selectedItems()[0].text())
            print(self.list_wid.selectedItems()[0].text())
        except IndexError as ie:
            print('err out u idiot')


    def getAsynInfo(self, listIndex):
        format = '%d/%m/%Y %H:%M:%S'
        current_asyn = self.main[listIndex]
        module = [m for m in current_asyn if 'DESCRIPTION' in m]
        module = module[0].split(':')[1].split('T')[0]

        module = [m for m in current_asyn if 'DESCRIPTION' in m]
        module = module[0].split(':')[1].split('\\')[0]

        start_data = [d for d in current_asyn if 'DTSTART' in d][0]
        start_date = start_data.split(':')[1].split('T')[0]
        start_time = start_data.split(':')[1].split('T')[1].split('Z')[0]
        start_date = datetime.datetime(int(start_date[:4]), int(start_date[4:6]), int(start_date[6:]))
        start_date = start_date.strftime("%d/%m/%Y")
        start_time = datetime.time(int(start_time[:2]), int(start_time[2:4]), int(start_time[4:]))
        start_time = start_time.strftime("%H:%M:%S")
        startDateTime = start_date + ' ' + start_time
        startDateTime = datetime.datetime.strptime(startDateTime, format)

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
        return [module, start_date, diff]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("calendar.png"))
    main = Test()
    app.setQuitOnLastWindowClosed(True)
    sys.exit(app.exec_())
