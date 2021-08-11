import sys, os, uuid, platform, getpass
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Timetable(QWidget):

    def __init__(self, icsFile):
        super().__init__()

        self.icsFile = icsFile

        self.data = []
        self.weeks = []
        self.days = []
        self.sorted_dates = {}
        self.num_of_weeks = 0
        self.custom_tasks = {}
        self.weeks_of_the_year = []
        self.asyn_data = {}
        self.preferences = []
        self.weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        self.asyn_idx_changed = []
        self.asyn_choices = {}

        self.final_dict = {}

        self.read_file()
        self.sort_dates()
        self.sort_asynchronous()
        self.sort_weekly()
        self.init_custom()
        self.init_final_dict()
        self.initUI()

    def initUI(self):

        self.uni_week = QComboBox(self)
        self.uni_week.addItems(['Week ' + str(x) for x in range(1, self.num_of_weeks+1)])
        self.uni_week.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.uni_week.currentTextChanged.connect(self.update_week)
        self.uni_week.setFixedSize(100, 30)

        # Asynchronous Data ------------------------------------------------------------------------------------

        self.asyn_label = QLabel(self)
        self.asyn_label.setText('Asynchronous tasks in the week HH:MM:SS, Weekday')
        self.asyn_label.adjustSize()
        self.asyn_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.asyn_combo = QComboBox(self)
        self.asyn_combo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.asyn_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.asyn_combo.currentIndexChanged.connect(self.update_box)

        self.date_label = QLabel(self)
        self.date_label.setText('Select a day to complete the task on')
        self.date_label.adjustSize()
        self.date_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.asyn_days_combo = QComboBox(self)
        self.asyn_days_combo.addItems(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        self.asyn_days_combo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.asyn_days_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.time_label = QLabel(self)
        self.time_label.setText('Select a time to complete the task at')
        self.time_label.adjustSize()
        self.time_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.asyn_task_time1 = QComboBox(self)
        self.asyn_task_time1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.asyn_task_time1.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.asyn_task_time1.addItems([str(x) for x in range(1, 13)])

        self.asyn_task_time2 = QComboBox(self)
        self.asyn_task_time2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.asyn_task_time2.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.asyn_task_time2.addItems(['00', '15', '30', '45'])

        self.asyn_task_ampm = QComboBox(self)
        self.asyn_task_ampm.addItems(['AM', 'PM'])

        self.h1 = QHBoxLayout()
        self.h1.addWidget(self.asyn_task_time1)
        self.h1.addWidget(self.asyn_task_time2)
        self.h1.addWidget(self.asyn_task_ampm)

        self.week_checkbox = QCheckBox("Do for each week")
        self.week_checkbox.setChecked(False)

        self.asyn_button = QPushButton('Add Preference')
        self.asyn_button.clicked.connect(self.update_asyn_preference)

        # Calendar --------------------------------------------------------------------------------------------

        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        calendar_start = list(self.sorted_dates.values())[0]
        q_cal_start = QDate(int(calendar_start.split('/')[2]), int(calendar_start.split('/')[1]), int(calendar_start.split('/')[0]))
        calendar_end = list(self.sorted_dates.values())[-1]
        q_cal_end = QDate(int(calendar_end.split('/')[2]), int(calendar_end.split('/')[1]), int(calendar_end.split('/')[0]))
        self.calendar.setDateRange(q_cal_start, q_cal_end)
        self.calendar.setSelectedDate(q_cal_start)
        self.calendar.clicked[QDate].connect(self.update_day)
        self.calendar.setFixedSize(450, 250)

        self.day_label = QLabel(self)
        self.day_label.setText('Select Date')

        self.widget = QWidget(self)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.day_label)
        self.widget.setLayout(self.vbox)

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        # Custom Task Data -----------------------------------------------------------------------------------

        self.custom_task_error_label = QLabel(self)
        self.custom_task_error_label.setText('Please enter a task')
        self.custom_task_error_label.setStyleSheet('color: red')
        self.custom_task_error_label.hide()
        
        self.custom_task_label = QLabel(self)
        self.custom_task_label.setText('Enter a task')

        self.custom_task_tedit = QTextEdit(self)
        self.custom_task_tedit.setPlaceholderText('Task Name')

        self.custom_task_time_label = QLabel(self)
        self.custom_task_time_label.setText('Please select a day from the calendar first')

        self.custom_task_time1 = QComboBox(self)
        self.custom_task_time1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.custom_task_time1.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.custom_task_time1.addItems([str(x) for x in range(1, 13)])

        self.custom_task_time2 = QComboBox(self)
        self.custom_task_time2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.custom_task_time2.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        mins = []
        for i in range(0, 56, 5):
            if len(str(i)) == 1:
                j = str(0) + str(i)
                mins.append(j)
            else:
                mins.append(str(i))
        self.custom_task_time2.addItems(mins)

        self.custom_task_ampm = QComboBox(self)
        self.custom_task_ampm.addItems(['AM', 'PM'])
        self.custom_task_ampm.adjustSize()

        self.duration_label = QLabel(self)
        self.duration_label.setText('Duration format is HH:MM:SS')

        self.custom_task_duration = QLineEdit(self)
        self.custom_task_duration.setPlaceholderText('Duration')

        self.custom_error_label = QLabel(self)
        self.custom_error_label.setText('Please put in a duration')
        self.custom_error_label.setStyleSheet('color: red')
        self.custom_error_label.hide()

        self.custom_checkbox = QCheckBox('Do for each week')
        self.custom_checkbox.setChecked(False)

        self.add_custom_task = QPushButton('Add Custom Task')
        self.add_custom_task.clicked.connect(self.add_task_connect)

        self.custom_tasks_combo = QComboBox(self)
        self.custom_tasks_combo.currentIndexChanged.connect(self.custom_combo_changed)

        self.h2 = QHBoxLayout()
        self.h2.addWidget(self.custom_task_time1)
        self.h2.addWidget(self.custom_task_time2)
        self.h2.addWidget(self.custom_task_ampm)

        # Finalize -------------------------------------------------------------------------------------------------

        self.num_of_asyn = QLabel(self)
        self.num_of_asyn.setText('Number of asyn tasks updated: 0')

        self.num_of_custom = QLabel(self)
        self.num_of_custom.setText('Number of custom tasks added: 0')

        self.button = QPushButton('Generate new timetable')
        self.button.clicked.connect(self.constraint_solver)

        group_box1 = QGroupBox('User Data')
        group_box2 = QGroupBox('Calendar Data')
        group_box3 = QGroupBox('Week')
        group_box4 = QGroupBox('Asynchronous')
        group_box5 = QGroupBox('Custom tasks')
        group_box6 = QGroupBox('Finalise')

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.grid = QGridLayout()
        self.v2 = QVBoxLayout()
        self.v3 = QVBoxLayout()
        self.v4 = QVBoxLayout()
        self.v5 = QVBoxLayout()
        self.v6 = QVBoxLayout()

        self.layout.addWidget(group_box1)
        self.layout.addWidget(group_box2)

        self.grid.addWidget(group_box3, 0, 0)
        self.grid.addWidget(group_box4, 1, 0)
        self.grid.addWidget(group_box5, 0, 1)
        self.grid.addWidget(group_box6, 1, 1)

        self.v2.addWidget(self.calendar)
        self.v2.addWidget(self.scroll)

        self.v3.addWidget(self.uni_week)
        
        self.v4.addWidget(self.asyn_label)
        self.v4.addWidget(self.asyn_combo)
        self.v4.addWidget(self.date_label)
        self.v4.addWidget(self.asyn_days_combo)
        self.v4.addWidget(self.time_label)
        self.v4.addLayout(self.h1)
        self.v4.addWidget(self.week_checkbox)
        self.v4.addWidget(self.asyn_button)
        
        self.v5.addWidget(self.custom_task_label)
        self.v5.addWidget(self.custom_task_error_label)
        self.v5.addWidget(self.custom_task_tedit)
        self.v5.addWidget(self.custom_task_time_label)
        self.v5.addLayout(self.h2)
        self.v5.addWidget(self.duration_label)
        self.v5.addWidget(self.custom_error_label)
        self.v5.addWidget(self.custom_task_duration)
        self.v5.addWidget(self.custom_checkbox)
        self.v5.addWidget(self.add_custom_task)
        self.v5.addWidget(self.custom_tasks_combo)
        
        self.v6.addWidget(self.num_of_asyn)
        self.v6.addWidget(self.num_of_custom)
        self.v6.addWidget(self.button)

        group_box1.setLayout(self.grid)
        group_box2.setLayout(self.v2)
        group_box3.setLayout(self.v3)
        group_box4.setLayout(self.v4)
        group_box5.setLayout(self.v5)
        group_box6.setLayout(self.v6)


        self.setGeometry(100, 100, 1000, 400)
        self.setWindowTitle('Timetable')
        self.show()


    def constraint_solver(self):
        # iterate through each in the timetable
        for week in self.weeks_of_the_year:
            # get the week index for dict/list reference
            week_idx = self.weeks_of_the_year.index(week)

            # iterate through each day in the current week
            for day in self.days[week_idx]:
                # iterate through each task in the current day
                for task in day:
                    # checks if the task is not asynchronous
                    task = int(task)
                    if task not in self.asyn_indexes:
                        # if the task is synchronous add it to the final dictionary
                        task_data = self.get_more_task_info(task)
                        task_data.append(task)
                        self.final_dict[week][self.days[week_idx].index(day)].append(task_data)
                        year = task_data[1].year

                    elif task in self.asyn_indexes and task not in self.asyn_idx_changed:
                        asyn_data = self.get_more_task_info(task)
                        asyn_data.append(task)
                        self.final_dict[week][self.days[week_idx].index(day)].append(asyn_data)


            # add asynchronous tasks into the final dictionary
            # check if the week exists in the key as certain weeks may be term breaks
            if week in self.asyn_choices.keys():
                # check if the user has provided a preference
                if len(self.asyn_choices[week]) > 0:
                    # if true, iterate through each preference for that weekday
                    for asyn_task in self.asyn_choices[week]:
                        # print('asyn task')
                        # print(asyn_task)
                        # store the important details that will need to be compared against
                        task = asyn_task[0][0]
                        duration = asyn_task[0][1]
                        original_weekday = asyn_task[0][2]
                        new_weekday = asyn_task[1]
                        hour = asyn_task[2]
                        mins = asyn_task[3]
                        ampm = asyn_task[4]
                        idx = asyn_task[6]
                        # convert the time to 24hours if necessary
                        if ampm == 'PM':
                            hour = int(hour) + 12
                        repeat = asyn_task[5]
                        # get the weekday index to allow comparison to the synchronous tasks on the same day
                        weekday_idx = self.weekdays.index(new_weekday)
                        # get a datetime object with the start and end times
                        asyn_pref_dt_obj = self.pref_to_dt(task, year, week-1, new_weekday, hour, mins, duration)
                        asyn_check = False
                        if len(self.final_dict[week][weekday_idx]) > 0:
                            for i in self.final_dict[week][weekday_idx]:
                                if i[1] < asyn_pref_dt_obj[1] < i[2]:
                                    asyn_check = True
                                elif i[2] == asyn_pref_dt_obj[1]:
                                    # starts at the end of a previous task
                                    asyn_check = False
                                elif i[1] == asyn_pref_dt_obj[1]:
                                    # starts at the same time as another task
                                    asyn_check = True
                                elif i[1] < asyn_pref_dt_obj[2] < i[2]:
                                    # ends during another task
                                    asyn_check = True
                            if asyn_check == False:
                                # false means that there are no conflicting tasks
                                asyn_pref_dt_obj.append(idx)
                                self.final_dict[week][weekday_idx].append(asyn_pref_dt_obj)
                            elif asyn_check == True:
                                # if there are conflicting tasks, set the task to be completed at the original time
                                original = self.pref_to_dt(task, year, week-1, original_weekday, hour, mins, duration)
                                original.append(idx)
                                self.final_dict[week][weekday_idx].append(original)
                        else:
                            # there are no tasks on the same day, most likely the weekend
                            asyn_pref_dt_obj.append(idx)
                            self.final_dict[week][weekday_idx].append(asyn_pref_dt_obj)


            if week in self.custom_tasks.keys():
                # check if there are custom tasks to compare
                if len(self.custom_tasks[week]) > 0:
                    for custom in self.custom_tasks[week]:
                        custom_dt = self.custom_to_dt(custom[0], year, week-1, self.weekdays[(custom[4]-1)], custom[1], custom[2], custom[5], custom[3])
                        custom_check = False
                        weekday_idx = custom[4]
                        if len(self.final_dict[week][weekday_idx-1]) > 0:

                            for i in self.final_dict[week][weekday_idx-1]:
                                if i[1] < custom_dt[1] < i[2]:
                                    custom_check = True
                                elif i[2] == custom_dt[1]:
                                    custom_check = False
                                elif i[1] == custom_dt[1]:
                                    custom_check = True
                                elif i[1] < custom_dt[2] < i[2]:
                                    custom_check = True

                            if custom_check == False:
                                self.final_dict[week][weekday_idx].append(custom_dt)

                            elif custom_check == True:
                                print('true')
                                #TODO: add another check for an hour earlier or later
                                # checks hour later
                                custom_dt_start = custom_dt[1] + timedelta(hours=1)
                                custom_dt_end = custom_dt[1] + timedelta(hours=1)
                                for i in self.final_dict[week][weekday_idx-1]:
                                    if i[1] < custom_dt_start < i[2]:
                                        custom_check = True
                                    elif i[2] == custom_dt_start:
                                        custom_check = False
                                    elif i[1] == custom_dt_start:
                                        custom_check = True
                                    elif i[1] < custom_dt_end < i[2]:
                                        custom_check = True

                                if custom_check == False:
                                    custom_dt[1] += timedelta(hours=1)
                                    custom_dt[2] += timedelta(hours=1)
                                    print(custom_dt)
                                    self.final_dict[week][weekday_idx].append(custom_dt)

                                else:
                                    custom_dt_start = custom_dt[1] + timedelta(hours=-1)
                                    custom_dt_end = custom_dt[1] + timedelta(hours=-1)
                                    for i in self.final_dict[week][weekday_idx-1]:
                                        if i[1] < custom_dt_start < i[2]:
                                            custom_check = True
                                        elif i[2] == custom_dt_start:
                                            custom_check = False
                                        elif i[1] == custom_dt_start:
                                            custom_check = True
                                        elif i[1] < custom_dt_end < i[2]:
                                            custom_check = True

                                    if custom_check == False:
                                        custom_dt[1] += timedelta(hours=-1)
                                        custom_dt[2] += timedelta(hours=-1)
                                        self.final_dict[week][weekday_idx].append(custom_dt)
                        else:
                            self.final_dict[week][weekday_idx].append(custom_dt)

        self.generate_ical()


    def generate_ical(self):
        # create the calendar object
        cal = Calendar()
        # add important details to the calendar object
        cal.add('method', 'publish')
        cal.add('version', '2.0')
        cal.add('x-wr-calname', 'Aston University Teaching Timetable')
        cal.add('prodid', '-//CELCAT//CalendarFeed//EN')

        # dtstamp is the date and time the calendar was created
        dtstamp = datetime.now()

        for week in self.weeks_of_the_year:
            # iterate through each day in the current week
            for day in self.final_dict[week]:
                # iterate through each task in the current days
                for task in day:
                    # get important info for the calendar
                    dtstart = task[1]
                    dtend = task[2]
                    # task is originally from the university timetable
                    if isinstance(task[-1], int):
                        uid = [u for u in self.data[task[-1]] if 'UID' in u][0].split(':')[1]
                        summary = [s for s in self.data[task[-1]] if 'SUMMARY' in s][0].split(':')[1]
                        location = [l for l in self.data[task[-1]] if 'LOCATION' in l][0].split(':')[1]
                        description = [d for d in self.data[task[-1]] if 'DESCRIPTION' in d][0].split(':')[1]
                        sequence = int([sq for sq in self.data[task[-1]] if 'SEQUENCE' in sq][0].split(':')[1]) + 1
                    # task is custom
                    else:
                        uid = uuid.uuid4()
                        summary = task[0].title()
                        location = ''
                        description = ''
                        sequence = int([sq for sq in self.data[0] if 'SEQUENCE' in sq][0].split(':')[1]) + 1


                    # create the event object for each task
                    event = Event()
                    # add the data for the task
                    event.add('uid', str(uid))
                    event.add('dtstart', dtstart)
                    event.add('dtend', dtend)
                    event.add('dtstamp', dtstamp)
                    event.add('summary', str(summary))
                    event.add('location', str(location))
                    event.add('description', str(description))
                    event.add('sequence', str(sequence))

                    # add the event to the calendar
                    cal.add_component(event)

                    # get the username of the user from the computer
                    user = getpass.getuser()
                    # get the type of system
                    system = platform.system()
                    if system == 'Linux':
                        os.chdir('/home/' + str(user) + '/Desktop/')
                    elif system == 'Windows':
                        os.chdir('c:\\Users\\' + str(user) + '\\Desktop\\')
                    elif system == 'Darwin':
                        os.chdir('/Users/' + str(user) + '/Desktop/')

        # open the ics file to be written to
        f = open(os.path.join(os.getcwd(), 'timetable.ics'), 'wb')
        # write the calendar data to the ics file
        f.write(cal.to_ical())
        f.close()


    def custom_to_dt(self, task_info, year, week, weekday, hour, mins, duration, ampm):
        if ampm == 'PM':
            hour = int(hour) + 12
        d = str(year) + '-W' + str(week) + '-' + weekday + '-' + str(hour) + '-' + mins
        dt_obj_start = datetime.strptime(d, "%Y-W%W-%A-%H-%M")
        td = timedelta(hours=int(duration))
        dt_obj_end = dt_obj_start + td
        return [task_info, dt_obj_start, dt_obj_end]


    def pref_to_dt(self, task_info, year, week, weekday, hour, mins, duration):
        d = str(year) + '-W' + str(week) + '-' + weekday + '-' + str(hour) + '-' + mins
        dt_obj_start = datetime.strptime(d, "%Y-W%W-%A-%H-%M")
        split = duration.split(':')
        td = timedelta(hours=int(split[0]), minutes=int(split[1]))
        dt_obj_end = dt_obj_start + td
        return [task_info, dt_obj_start, dt_obj_end]

    
    def init_final_dict(self):
        for week in self.weeks_of_the_year:
            self.final_dict[week] = []
        for key in self.final_dict.keys():
            for i in range(7):
                self.final_dict[key].append([])

    
    def init_custom(self):
        for i in self.weeks_of_the_year:
            if i in self.custom_tasks.keys():
                if not self.custom_tasks.get(i):
                    self.custom_tasks[i] = []
            else:
                if not self.custom_tasks.get(i):
                    self.custom_tasks[i] = []


    def custom_combo_changed(self, num):
        data = self.custom_tasks_combo.currentText()
        split_data = data.split(' ')


    def update_num_tasks(self):
        length = 0
        for i in self.custom_tasks.keys():
            length += len(self.custom_tasks[i])
        print('custom', length)
        asyn_length = 0
        asyn_length += len(self.asyn_idx_changed)
        print('asyn', asyn_length)


    def add_task_connect(self):
        day = self.calendar.selectedDate().dayOfWeek()
        d = self.calendar.selectedDate().toString('dddd')
        week = self.calendar.selectedDate().weekNumber()[0]
        task = self.custom_task_tedit.toPlainText()
        hour = self.custom_task_time1.currentText()
        min = self.custom_task_time2.currentText()
        ampm = self.custom_task_ampm.currentText()
        duration = self.custom_task_duration.text()

        if str(task) != '' and str(duration) != '':
            custom_task = [task, hour, min, ampm, day, duration]
            self.custom_tasks[week].append(custom_task)
            readable_task = task.upper() + ', ' + hour + ':' + min + ampm + ', ' + duration + 'hrs'
            self.custom_tasks_combo.addItem(readable_task)
            self.custom_task_tedit.clear()
            self.custom_task_time1.setCurrentIndex(0)
            self.custom_task_time2.setCurrentIndex(0)
            self.custom_task_ampm.setCurrentIndex(0)
            self.custom_task_duration.clear()
            self.custom_task_error_label.hide()
            self.custom_error_label.hide()
        elif str(task) == '' and str(duration) == '':
            self.custom_task_error_label.show()
            self.custom_error_label.show()
        elif str(duration) == '':
            self.custom_error_label.show()
            self.custom_task_error_label.hide()       
        elif str(task) == '':
            self.custom_task_error_label.show()
            self.custom_error_label.hide()

        total = 0
        for i in self.custom_tasks.values():
            total += len(i)
        
        self.num_of_custom.setText('Number of custom tasks added: ' + str(total))


    def get_date_range(self, year, week):
        days = []
        form = str(year) + '-W' + str(week)
        first_day = datetime.strptime(form + '-1', '%G-W%V-%u').date()
        for i in range(7):
            day = (first_day + timedelta(days=i))
            days.append(str(day.day) + '/' + str(day.month) + '/' + str(day.year))
        return days


    def reset_asyn(self):
        self.asyn_days_combo.setCurrentIndex(0)
        self.asyn_task_time1.setCurrentIndex(0)
        self.asyn_task_time2.setCurrentIndex(0)
        self.asyn_task_ampm.setCurrentIndex(0)
        self.week_checkbox.setCheckState(False)


    def update_box(self):
        # get the week for the selected date in calendar
        week = self.calendar.selectedDate().weekNumber()[0]

        # iterate through the choices if the week is in the dictionary
        if week in self.asyn_choices.keys():
            # get the data for the week
            data = self.asyn_choices[week]
            # iterate through each task
            for task in data:
                # check if the details match
                name = task[0][0] + ', ' + task[0][1] + ', ' + task[0][2] + ', ' + task[0][3]
                if name == self.asyn_combo.currentText():
                    self.asyn_days_combo.setCurrentText(task[1])
                    self.asyn_task_time1.setCurrentText(task[2])
                    self.asyn_task_time2.setCurrentText(task[3])
                    self.asyn_task_ampm.setCurrentText(task[4])
                    self.week_checkbox.setCheckState(task[5])
                else:
                    self.reset_asyn()


    def update_week(self, week):
        # week = ['Week', int('1')-1]
        week = int(week.split(' ')[1])-1
        # gets the mondays tasks
        idx = self.days[week][0][0]
        # gets the date of the monday
        week_start_date = self.sorted_dates[idx]
        # split to convert to QDate format
        split = week_start_date.split('/')
        qdate = QDate(int(split[2]), int(split[1]), int(split[0]))

        selected = self.calendar.selectedDate().weekNumber()[0]
        selected_week_idx = self.weeks_of_the_year.index(selected)

        if selected_week_idx != self.uni_week.currentIndex():
            # update the calendars current selected date to new one
            self.calendar.setSelectedDate(qdate)
            # update the label with the days tasks
            self.update_day(qdate)


    def update_day(self, qdate):
        # TODO: change the week in the combobox when the date is changed in the calendar
        # print(qdate)
        # convert the QDate object to string
        string_qdate = qdate.toString(Qt.ISODate).split('-')
        # convert the string to a datetime object
        datetime_obj = datetime(int(string_qdate[0]), int(string_qdate[1]), int(string_qdate[2]))
        # gets the integer week number in the year
        dt_week = datetime_obj.isocalendar()[1]
        # gets the integer number in the week
        dt_day = datetime_obj.isocalendar()[2]

        try:
            week_combo_idx = self.weeks_of_the_year.index(dt_week)
            self.uni_week.setCurrentIndex(week_combo_idx)
        except ValueError as ve:
            print('Week is not in the list, most likely half term')

        if dt_week in self.weeks_of_the_year:
            # gets the weeks index
            idx = self.weeks_of_the_year.index(dt_week)
            # gets the weeks task
            week_tasks = self.days[idx]
            # update the asyn combo with current weeks asynchronous tasks
            self.update_asyn(week_tasks)
            # gets the days tasks
            day_task = self.days[idx][dt_day-1]
            self.day_label.clear()
            module_details = []
            for task in day_task:
                details = self.get_task(int(task))
                module_details.append(details)
            sorted_details = self.sort_list(module_details)
            for i in sorted_details:
                if self.day_label.text() == '':
                    self.day_label.setText(i[1] + '-' + i[2] + '\n' + i[0])
                else:
                    content = self.day_label.text()
                    self.day_label.setText(content + '\n\n' + i[1] + '-' + i[2] + '\n' + i[0])
        else:
            self.day_label.clear()
            self.asyn_combo.clear()

        self.custom_tasks_combo.clear()
        if dt_week in self.custom_tasks.keys():
            if len(self.custom_tasks[dt_week]) > 0:
                for i in self.custom_tasks[dt_week]:
                    c_task = i[0].upper() + ', ' + i[1] + ':' + i[2] + i[3] + ', ' + i[5] + 'hrs'
                    self.custom_tasks_combo.addItem(c_task)


    def sort_list(self, sub_list):
        sub_list.sort(key = lambda x: x[1])
        return sub_list


    def get_more_task_info(self, idx):
        
        desc = [d for d in self.data[idx] if 'DESCRIPTION' in d][0].split(':')
        module = desc[1].split('\\n')[0]
        
        time_split_start = [t for t in self.data[idx] if 'DTSTART' in t][0].split(':')[1]
        time_split_end = [t for t in self.data[idx] if 'DTEND' in t][0].split(':')[1]
        
        start_time = time_split_start.split('T')[1].split('Z')[0]
        start_time = start_time[:2] + ':' + start_time[2:4] + ':' + start_time[4:]
        
        finish_time = time_split_end.split('T')[1].split('Z')[0]
        finish_time = finish_time[:2] + ':' + finish_time[2:4] + ':' + finish_time[4:]
        
        date = time_split_start.split('T')[0]
        time_start = time_split_start.split('T')[1].split('Z')[0]
        time_end = time_split_end.split('T')[1].split('Z')[0]
        
        dt_obj_start = datetime(int(date[:4]), int(date[4:6]), int(date[6:]), int(time_start[:2]), int(time_start[2:4]), int(time_start[4:]))
        dt_obj_end = datetime(int(date[:4]), int(date[4:6]), int(date[6:]), int(time_end[:2]), int(time_end[2:4]), int(time_end[4:]))
        # print(dt_obj_start.isocalendar()[1])

        return [module, dt_obj_start, dt_obj_end]


    def get_task(self, idx):
        # gets the description which contains the module name
        desc = [d for d in self.data[idx] if 'DESCRIPTION' in d][0].split(':')
        # retrieve the module from the string
        module = desc[1].split('\\n')[0]
        # find the start time and split it from the attached date which we already know
        start_time = [t for t in self.data[idx] if 'DTSTART' in t][0].split(':')[1].split('T')[1].split('Z')[0]
        # format the time so that it is user readable
        start_time = start_time[:2] + ':' + start_time[2:4] + ':' + start_time[4:]
        finish_time = [t for t in self.data[idx] if 'DTEND' in t][0].split(':')[1].split('T')[1].split('Z')[0]
        finish_time = finish_time[:2] + ':' + finish_time[2:4] + ':' + finish_time[4:]
        # return the data for use in the other functions
        return [module, start_time, finish_time]


    def update_asyn(self, week_tasks):
        # temporary array for storing the asynchronous tasks
        asyn_arr = []
        # iterate throught the days in the week
        for day_tasks in week_tasks:
            # iterate through each days tasks
            for task_id in day_tasks:
                # check if the task is an asynchronous one
                if int(task_id) in self.asyn_indexes:
                    # print(task_id + ' is asynchronous')
                    uid = [u for u in self.data[int(task_id)] if 'UID' in u][0].split(':')[1]
                    data = [d for d in self.data[int(task_id)] if 'DTSTART' in d][0].split(':')[1].split('T')[0]
                    dt_obj = datetime(int(data[:4]), int(data[4:6]), int(data[6:]))
                    week_day = dt_obj.strftime('%A')
                    week_num = dt_obj.isocalendar()[1]
                    # get the module name, start and finish times
                    task_info = self.get_task(int(task_id))
                    time_format = '%H:%M:%S'
                    # get the time difference between the start and finish
                    time_diff = datetime.strptime(task_info[2], time_format) - datetime.strptime(task_info[1], time_format)
                    module_string = str(task_info[0]) + ', ' + str(time_diff) + 'hrs' + ', ' + str(week_day) + ', ' + task_id
                    self.asyn_data[uid] = [str(task_info[0]), time_diff, week_day, week_num]
                    # add it to the array
                    asyn_arr.append(module_string)
        self.asyn_combo.clear()
        self.asyn_data.clear()
        self.asyn_combo.addItems(asyn_arr)


    def update_asyn_preference(self):
        # Get the days selected for the current asynchronous task in the list
        asyn_task = self.asyn_combo.currentText()
        asyn_task_split = asyn_task.split(', ')
        print('task', asyn_task_split)

        day = self.asyn_days_combo.currentText()
        hour = self.asyn_task_time1.currentText()
        minute = self.asyn_task_time2.currentText()
        ampm = self.asyn_task_ampm.currentText()
        every_week = self.week_checkbox.isChecked()
        idx = asyn_task_split[-1]

        preference = [asyn_task_split, day, hour, minute, ampm, every_week, int(idx)]
        print(preference)

        week = self.calendar.selectedDate().weekNumber()[0]

        if week in self.asyn_choices.keys():
            match = False
            for iteration, item in enumerate(self.asyn_choices[week]):
                print(iteration, item)
                if item[0] == asyn_task_split:
                    # replace the existing one
                    index = self.asyn_choices[week].index(item)
                    self.asyn_choices[week].pop(index)
                    self.asyn_choices[week].append(preference)
                    self.asyn_idx_changed.append(int(idx))

                    match = True
                    asyn_idx = item
                else:
                    self.asyn_choices[week].append(preference)
                    self.asyn_idx_changed.append(int(idx))
        else:
            self.asyn_choices[week] = [preference]
            self.asyn_idx_changed.append(int(idx))

        if every_week == True:
            index1 = datetime.strptime(asyn_task_split[2], '%A').weekday()
            for i in self.days:
                for j in i[index1]:
                    module = self.get_task(int(j))
                    duration = str(datetime.strptime(module[2], '%H:%M:%S') - datetime.strptime(module[1], '%H:%M:%S')) + 'hrs'
                    module = [module[0], duration, asyn_task_split[2]]
                    if asyn_task_split[0] == module[0]:
                        data = self.data[int(j)]
                        date = [d for d in data if 'DTSTART' in d][0].split('DTSTART:')[1].split('T')[0]
                        week_num = datetime(int(date[:4]), int(date[4:6]), int(date[6:])).isocalendar()[1]
                        print(week_num)

                        preference1 = [module, day, hour, minute, ampm, every_week]

                        if week_num in self.asyn_choices.keys():
                            for k in self.asyn_choices[week_num]:
                                if k[0] == module:
                                    idx = self.asyn_choices[week_num].index(k)
                                    self.asyn_choices[week_num].pop(idx)
                                    self.asyn_choices[week_num].append(preference1)
                                    self.asyn_idx_changed.append(int(idx))
                                    print(self.asyn_idx_changed)
                                else:
                                    self.asyn_choices[week_num].append(preference1)
                                    self.asyn_idx_changed.append(int(idx))
                        else:
                            self.asyn_choices[week_num] = [preference1]
                            print('added')
                            self.asyn_idx_changed.append(int(idx))     
        
        self.reset_asyn()


    def sort_weekly(self):
        # prepare arrays for storing the weekly tasks
        for i in range(self.num_of_weeks):
            # adds an array for each week in the ics file
            self.weeks.append([])

        for j in range(self.num_of_weeks):
            # adds the weeks into the days array
            self.days.append([])
        for k in range(len(self.days)):
            # adds the days of the week array for each week
            for l in range(7):
                self.days[k].append([])

        for k, v in self.sorted_dates.items():
            split = v.split('/')
            datetime_obj = datetime(int(split[2]), int(split[1]), int(split[0]))
            week_num = datetime_obj.isocalendar()[1]
            week_day_num = datetime_obj.isocalendar()[2]
            # compares the current date to the array for the index to use to store the data in the weeks array
            idx = self.weeks_of_the_year.index(week_num)
            # adds to the correct day in the week for each week
            # week day num -1 is due to datetime returning 1 for monday and our array starts at 0
            self.days[idx][week_day_num-1].append(k)
            # added to the correct week in the weeks array
            self.weeks[idx].append(k)


    def sort_asynchronous(self):
        # status array stores the (a)synchronous status for each task
        status = []
        for i in range(len(self.data)):
            # gets the location element in each array and stores it
            loc = [s for s in self.data[i] if 'LOCATION' in s][0]
            # each location element is formatted to get the status
            split = loc.split(' ')[-1].replace('(', '').replace(')', '')
            status.append(split)

        # stores the indexes for all asynchronous tasks for better access
        self.asyn_indexes = [i for i, x in enumerate(status) if x == 'Asynchronous']


    def sort_dates(self):
        # format is the date format we use in the UK
        format = "%d/%m/%Y"
        # temp dates stores the date and the id for the current task for ease of access later on
        temp_dates = {}
        week_numbers = []
        for i in self.data:
            # d is an array storing the dates & times for each task in self.data
            d = [m for m in i if 'DTSTART' in m][0]
            # date separates the date from the time
            date = d.split(':')[1].split('T')[0]
            # date is updated to fit the format in the datetime module (yyyy,mm,dd)
            date = datetime(int(date[:4]), int(date[4:6]), int(date[6:]))
            # gets the day of the week in an integer form
            week_day_num = date.isocalendar()[2]
            # gets the weeks number in th eyear (max 52)
            week_num = date.isocalendar()[1]
            # will be using the weeks to store the weekly tasks
            self.weeks_of_the_year.append(week_num)
            self.weeks_of_the_year = list(set(self.weeks_of_the_year))
            # stores the individual weeks in an array
            if week_num not in week_numbers:
                week_numbers.append(week_num)
            # date is now formatted to fit the format variable
            date = date.strftime(format)
            #  index from the data array and the date for the current task is added to the temp dictionary
            temp_dates[str(self.data.index(i))] = date
        # sorted dates sorts the temp dates dictionary by ascending date
        self.sorted_dates = dict(sorted(temp_dates.items(), key = lambda date: datetime.strptime(date[1], format)))
        # weeks stores the weeks numbered from 1 to the length of the week_num array
        self.numbered_weeks = ['Week' + str(x) for x in range(1, len(week_numbers)+1)]
        self.num_of_weeks = len(week_numbers)


    # reads the ics file
    def read_file(self):
        # temp data stores each individual task which is then added to the data array
        temp_data = []
        # with open('main.ics', 'r') as f:
        with open(file, 'r') as f:
            for line in f:
                # stores data between begin:vevent and end:vevent
                # as it contains the (a)synchronous task information
                if line.strip() == 'BEGIN:VEVENT':
                    # self.temp stores the line as a element in the array
                    temp_data = []
                    temp_data.append(line.strip())
                elif line.strip() == 'END:VEVENT':
                    # when we reach the end of the task we add temp as a collective
                    # to self.main which contains all of the tasks
                    # self.temp is cleared to store the next tasks information
                    temp_data.append(line.strip())
                    self.data.append(temp_data)
                    temp_data = []
                elif line.strip() == 'BEGIN:VCALENDAR':
                    continue
                else:
                    temp_data.append(line.strip())
        print(self.data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("calendar.png"))
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file, _ = QFileDialog.getOpenFileName(None, "ICS File", "", "ICS Files (*.ics)", options = options)
    main = Timetable('main.ics')
    app.setQuitOnLastWindowClosed(True)
    sys.exit(app.exec_())