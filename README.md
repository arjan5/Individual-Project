# Individual-Project
## Timetable Assistant


This projects aim is to aid students/staff members when updating their individual university timetables.
Only works with UK Universities.

Please ensure that a version of Python 3 is installed on your machine before attempting to install.

Application runs on Windows 7/8/10, MacOS 10.13 and later versions along with Ubuntu Linux 20.04 and later.
The application can also be built from the Python source code with the module pyinstaller installed:

```
pip install pyinstaller
pyinstaller --onefile --windowed timetable.py
```
The output is put in the folder where the timetable.py file is stored, recommended to store in a single folder as there are a lot of output files.
Open the dist folder and the application for your system should be ready to run

Once the application is running, select your .ics file to load your university timetable.
x-special/nautilus-clipboard
copy
file:///home/arjan/Pictures/Screenshot%20from%202021-08-07%2016-11-04.png


You can select the week of the timetable in the dropdown box in the top left box or select a date in the interactive calendar on the far right.
Now you should be able to see your asynchronous tasks in the bottom left box.
The top right box allows you to input custom tasks, note that the task added will use the selected date in the calendar, so select a date beforehand.
The bottom right box contains the amount of changes made to the asynchronous tasks and the amount of custom tasks that have been added.
Finally, you have the 'Generate new timetable' which will run your changes against the constraint solver and output a new calendar (.ics) file to your desktop.

