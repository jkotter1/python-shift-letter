#Note: convert this file to a .exe with the cx_Freeze python module and the command "python setup.py build" (see link for more info https://stackoverflow.com/questions/41570359/how-can-i-convert-a-py-to-exe-for-python)
import getpass
import platform
import sys
import os
import subprocess
import shutil 
import sqlite3
from sqlite3 import Error
from PyQt5 import QtCore
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QDialog, QCheckBox, QCalendarWidget
from PyQt5.QtCore import QFile, QTextStream, QEvent, QTimer, QUrl, QEvent
from datetime import datetime, date

#import qdarkstyle
from NightLetterAppStyleSheet import loadStyleSheet
from DefineUI import Ui_MainWindow  # importing our generated file
from RemoveAttachDiag import Ui_RemAtDiag
from DatePickerDiag import Ui_dateDialog
# Note: file generate from Qt5 Designer as TestMain.ui - need to convert it to .py and rename to DefineUI.py
#Use command "pyuic5 TestMain.ui > DefineUI.py"


# __________________Date Picker Dialog Code__________________
class DatePickerDialog(QDialog):

    def __init__(self): 
        super(DatePickerDialog, self).__init__()
        self.ui = Ui_dateDialog()
        self.ui.setupUi(self)
        self.ui.calendarWidget.clicked.connect(self.calendar)

    def calendar(self):
        dateSelection = self.ui.calendarWidget.selectedDate()
        date_Selected = datetime.strftime(dateSelection.toPyDate(), '%m/%d/%Y')
        #print(date_Selected)
        con = application.sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT * FROM NightLetterData2 WHERE Date= '" + date_Selected +  "'")
        vals = cursorObj.fetchall()
        con.close()
        self.ui.AutoSaveActive = False
        if vals != []:
            chosenRecordNum = vals[0][0]
            #print (chosenRecordNum)
            NightLetterMain.load_all_fields(application, chosenRecordNum)
        else:
            print("There is no record for the date selected.") # Maybe a dialog box for this at some point?
        self.ui.AutoSaveActive = True
        self.reject()
        #datestring = datetime.strftime(dateSel.toPyDate(), '%m/%d/%Y')
        #print(datestring)
        #self.ui.Date.setDate(dateSel)

# __________________Remove Attachments Dialog Code__________________
class RemoveAttachmentDialog(QDialog):

    def __init__(self, fileDict): 
        super(RemoveAttachmentDialog, self).__init__()
        self.ui = Ui_RemAtDiag()
        self.ui.setupUi(self)
        for index, item in enumerate(fileDict):
            if item != "":
                self.ui.selectionLayout.addWidget(QCheckBox(item),index,0)
        self.ui.buttonBox.accepted.connect(self.RemoveFiles)

    def RemoveFiles(self):
        layout = self.ui.selectionLayout
        attachFieldString = application.ui.Attachments.toHtml()
        for i in range(layout.count()):
            checkBox = layout.itemAt(i).widget()
            cbName = checkBox.text()
            if checkBox.isChecked():
                AttachmentStoragePath = "W:\\CLTBODY\\Kotter\\Projects\\Night Letter Updates\\Python Night Letter\\Attachments\\"
                try:
                    os.remove(AttachmentStoragePath+cbName)
                except FileNotFoundError:
                    print("The file has already been removed.") # Probably should add a dialog box for this at some point.
                attachFieldString = attachFieldString.replace(cbName,"")
        self.ui.AutoSaveActive = False
        application.ui.Attachments.setText(attachFieldString)
        self.removeEmptyLines()
        application.save_field(application.ui.Attachments)
        self.ui.AutoSaveActive = True
    
    def removeEmptyLines(self):
        attachFieldString = application.ui.Attachments.toHtml()
        emptyCheckBox = "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>"
        attachFieldString = attachFieldString.replace(emptyCheckBox,"")
        application.ui.Attachments.setText(attachFieldString)


# __________________Setup Main Form Code__________________ (makes connections for event handlers and widget signals)
class NightLetterMain(QtWidgets.QMainWindow):
 
    def __init__(self, parent=None):

        super(NightLetterMain, self).__init__(parent)
 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.AutoSaveActive = False
        self.ui.AttachmentPB.clicked.connect(lambda: self.attach_document(self.openFileNameDialog()))

        self.ui.PrevRecordPB.clicked.connect(lambda: self.goToRecord("prev"))
        self.ui.NextRecordPB.clicked.connect(lambda: self.goToRecord("next"))

        self.ui.RemoveAttachmentPB.clicked.connect(self.remove_attachment)
        self.ui.Attachments.anchorClicked.connect(self.linkClicked)
        self.ui.Attachments.setOpenLinks(False)

        self.ui.Date.installEventFilter(self)
    
    def eventFilter(self, source, event):
        self.ui.Date.mousePressEvent = self.datePicker
        return super(NightLetterMain, self).eventFilter(source, event)


# __________________Date Change/Record Navigation Code__________________ (works with Date Picker Dialog)
    def datePicker(self, obj):
        dpicker = DatePickerDialog()
        dpicker.setStyleSheet(loadStyleSheet())
        dpicker.exec_()    

    def linkClicked(self, url):
        linkPath = "\"" + url.toString().replace("%5C", "/") + "\""
        try:
            os.startfile(linkPath)
        except FileNotFoundError:
            print("The requested file is no longer available.") # Probably should add a dialog box for this at some point.
        except OSError:
            print("There is not default software for opening this file. Please right click the link, choose copy link location, then try to open the link with different software.")

    def goToRecord(self, direction): #combine with goToNextRecord?

        letterID = int(self.ui.LetterID.toPlainText())
        if direction == "prev":
            self.goToPreviousRecord() # = str(letterID - 1)
        elif direction == "next":
            self.goToNextRecord() # = str(letterID + 1)
        else:
            print("An error occured.")
        #con = application.sql_connection()
        #cursorObj = con.cursor()
        #cursorObj.execute("SELECT " + nextLetterID + " FROM NightLetterData2")
        #vals = cursorObj.fetchall()
        #con.close()
        #latestRecordNum = vals[0][0]
        #print(latestRecordNum)
        #self.load_all_fields(latestRecordNum)

    def goToPreviousRecord(self): #combine with goToNextRecord?
        prevValue = self.ui.LetterID.toPlainText()
        prevValue = int(prevValue)
        prevValue = prevValue - 1
        prevValue = str(prevValue)
        print(prevValue)  # the following is copied code modified
        con = application.sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT " + prevValue + " FROM NightLetterData2")
        vals = cursorObj.fetchall()
        con.close()
        latestRecordNum = vals[0][0]
        self.load_all_fields(latestRecordNum)

    def goToNextRecord(self): #need bug fix for next button on last record crashing the form
        
        letterID = int(self.ui.LetterID.toPlainText())
        NewestLetterID = int(self.get_newest_LetterID())
        nextValue = str(letterID + 1)
        if letterID == NewestLetterID:
            New_Record_Query = "INSERT INTO NightLetterData2 (LetterID, Date) VALUES ({0},{1})".format(nextValue, date.today().strftime("%m/%d/%Y"))
            try:
                con = application.sql_connection()
                cursorObj = con.cursor()
                cursorObj.execute(New_Record_Query)
                vals = cursorObj.fetchall()
                con.close()
                self.load_all_fields(letterID + 1)
            except sqlite3.Error as error:
                print("Error while connecting to sqlite", error)
        else:
            try:
                con = application.sql_connection()
                cursorObj = con.cursor()
                cursorObj.execute("SELECT " + nextValue + " FROM NightLetterData2")
                vals = cursorObj.fetchall()
                con.close()
                latestRecordNum = vals[0][0]
                self.load_all_fields(latestRecordNum)
            except sqlite3.Error as error:
                print("Error while connecting to sqlite", error)

# __________________File Attachment/Removal Functions__________________ (works with Remove Attachments Dialog)
    def attach_document(self, docPath):
        if docPath is None:
            return
        NightLetterPath = "W:\\CLTBODY\\Kotter\\Projects\\Night Letter Updates\\Python Night Letter"
        attachLoc = "\\Attachments" # Must have a folder named Attachments in the same directory as running script
        recordDate = self.ui.Date.toPlainText().replace("/", "-") #recordDate = datetime.strftime(self.ui.Date.date().toPyDate(), '%m-%d-%y')
        fileName = "{0}-{1}".format(recordDate, self.getFileName(docPath))
        if fileName == False:
            return
        newDocPath = NightLetterPath + attachLoc + "\\" + fileName
        copyNum = 1
        while self.fileExists(newDocPath):
            newDocPath= "{0}{1}\\{2}({3}).{4}".format(NightLetterPath, attachLoc, fileName.rsplit('.', 1)[0], str(copyNum), fileName.rsplit('.', 1)[1]) #NightLetterPath + attachLoc + "\\" + recordDate + "(" + str(copyNum) + ")" + fileName
            #print(newDocPath)
            copyNum += 1
        if copyNum > 1:
            fileName = "{0}({2}).{1}".format(*fileName.rsplit('.', 1) + [copyNum - 1])
        shutil.copyfile(docPath, newDocPath)
        fileLink = '<span><a href=\"{0}\">{1}</a></span>'.format(newDocPath, fileName)
        self.ui.Attachments.append(fileLink)
        self.save_field(self.ui.Attachments)
    
    def remove_attachment(self):
        print("work in progress")    
        attachList =  self.attachDict()
        if attachList == ['']:
            return
        rad = RemoveAttachmentDialog(attachList)
        rad.setStyleSheet(loadStyleSheet())
        rad.exec_()

    def attachDict(self):
        attachString = self.ui.Attachments.toPlainText().split("\n")
        print(attachString)
        return attachString

    def fileExists(self, filepath):
        if os.path.isfile(filepath):
            print("The file already exists!")
            return True
        return False

    def getFileName(self, path):
        if path.__class__.__name__ == "NoneType":
            return False
        head, tail = os.path.split(path)
        return tail or os.path.basename(head)

    def openFileNameDialog(self): # Launches a file picker dialog that allows the user to browse and choose a file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            return fileName

# __________________Save and Load Functions__________________
    def savefield(self):  # Receives signals from QWidgets on textChanged
        if self.ui.AutoSaveActive:
            print("Saving Changes")
            self.save_field (self.focusWidget())

    def sql_connection(self): # Connects to sqlite database
        try:
            con = sqlite3.connect('Night Letter 2.0 data.db')
            return con
        except Error:
            print(Error)
    
    def save_field(self, obj): #saves an individual field
        try:
            fieldName = obj.objectName()
            fieldtype = obj.__class__.__name__
            if fieldtype == "QDateEdit":
                fieldval = datetime.strftime(obj.date().toPyDate(), '%m/%d/%Y')
            elif fieldtype == "QComboBox":
                fieldval = str(obj.currentText())
            elif fieldtype == "QTextEdit" or fieldtype == "QTextBrowser":
                fieldval = obj.toHtml()
                #print (fieldval)
            #elif fieldtype == "QTextBrowser":
            #    fieldval = obj.toPlainText()
                #print(fieldval)
            letterID = self.ui.LetterID.toPlainText()
            valdict = self.ui.LatestValueDict
            if fieldName in valdict:
                lastLoadFieldValue = valdict[fieldName]
                con = self.sql_connection()
                cursorObj = con.cursor()
                if self.query_field(fieldName, letterID) == lastLoadFieldValue:
                    queryString = "UPDATE NightLetterData2 SET " + fieldName + " = ? WHERE LetterID = '" + letterID + "'"
                    cursorObj.execute(queryString, [fieldval])
                    con.commit()
                    con.close() 
                    self.ui.LatestValueDict[fieldName] = fieldval
                else:
                    self.load_all_fields(letterID)
                    print("Record has been changed by another user. Please copy your changes, reload the form, and reenter the changes to save.")
        except AttributeError:
            if type(obj) == 'NoneType':
                print("No field currently in focus.")
            else:
                 raise AttribueError

    def load_most_recently_created_record(self): # Finds and loads the record with the most recent date
        con = application.sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT max(LetterID) FROM NightLetterData2")
        vals = cursorObj.fetchall()
        con.close()
        latestRecordNum = vals[0][0]
        self.ui.LatestRecordNum = latestRecordNum
        self.load_all_fields(latestRecordNum)

    def get_newest_LetterID(self): # Finds and loads the record with the most recent date
        con = application.sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT max(LetterID) FROM NightLetterData2")
        vals = cursorObj.fetchall()
        con.close()
        latestRecordNum = vals[0][0]
        self.ui.LatestRecordNum = latestRecordNum
        return latestRecordNum
    
    def query_field(self, fieldname, letterID): # Finds the letter number of the letter with the most recent date
        con = application.sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT " + fieldname + " FROM NightLetterData2 WHERE LetterID = '" + letterID + "'")
        vals = cursorObj.fetchall()
        return vals[0][0]
        con.close() 

    def load_all_fields(self, recordNum): # Queries the values for all fields from the database and inserts the values into the fields for the letter form
        self.ui.AutoSaveActive = False  #so we don't recursively call save_field on textChanged() forever
        FieldNames = ""
        FieldNameList = []
        for w in self.allWidgets():
            wName = w.widget().objectName()
            wType = w.widget().__class__.__name__
            if wType == "QTextEdit" or wType == "QTextBrowser" or wType == "QDateEdit" or wType == "QComboBox":
                FieldNameList.append(wName)
                if FieldNames == "":
                    FieldNames = wName
                else:
                    FieldNames = FieldNames + ", " + wName
        try:
            sqliteConnection = application.sql_connection()
            cursor = sqliteConnection.cursor()
            sqlite_select_Query = "SELECT " + FieldNames + " FROM NightLetterData2 WHERE LetterID = " + str(recordNum) #At some point, this should be rewritten so that all the data is obtained in 1 query and then distributed to the fields via a loop.
            cursor.execute(sqlite_select_Query)
            record = cursor.fetchall()
            self.latest_record = record
            FieldValueList = record[0]
            cursor.close()
        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
        self.ui.LatestValueDict = dict(zip(FieldNameList, FieldValueList))
        LastVal = self.ui.LatestValueDict       #Dictionary of all the most recently queried values for each field from the database. Get the queried values by giving it the field name (i.e. LastVal[Safety] )
        
        if LastVal["LetterID"] == self.ui.LatestRecordNum:
            self.ui.NextRecordPB.setText("New...")
        else:
            self.ui.NextRecordPB.setText("Next")

        for w in self.allWidgets():
            wName = w.widget().objectName() 
            wType = w.widget().__class__.__name__
            if wType  == "QTextEdit" or wType == "QTextBrowser":
                w.widget().setText(str(LastVal[wName]))
            #elif wType == "QDateEdit":                 #There are no date edits in the layout currently, but this could come in handy at some point
            #    date_str = LastVal[wName]
            #    date_object = datetime.strptime(date_str, '%m/%d/%Y').date()
            #    w.widget().setDate(date_object)
            elif wType == "QComboBox":
                currentIndex = w.widget().findText(str(LastVal[wName]))
                w.widget().setCurrentIndex(currentIndex)

        self.ui.AutoSaveActive = True # have to turn back on to save as the user types
    
    def allWidgets(self): # returns a list of all widgets 
        layout = self.ui.WidgetGridLayout
        return (layout.itemAt(i) for i in range(layout.count()))

    def update_field(self, fieldname, newval): # Inserts a new value into a field
        for w in self.allWidgets():
            wName = w.widget().objectName() 
            if wName == fieldname:
                fieldtype = w.widget().__class__.__name__
                self.ui.AutoSaveActive = False
                if fieldtype  == "QTextEdit" or fieldtype == "QTextBrowser":
                    w.widget().setText(str(newval))
                #elif fieldtype == "QDateEdit":
                #    date_str = newval
                #    date_object = datetime.strptime(date_str, '%m/%d/%Y').date()
                #    w.widget().setDate(date_object)
                elif fieldtype == "QComboBox":
                    currentIndex = w.widget().findText(str(newval))
                    w.widget().setCurrentIndex(currentIndex)
                self.ui.AutoSaveActive = True

    def check_if_refresh_needed(self): # Check if changes to a record have occured in the database since the record was last loaded. If a change has occured, reload the record.
        #print("Checking for db changes")
        letterID = str(self.ui.LetterID.toPlainText())
        #print(letterID)
        NewestLetterID = str(self.get_newest_LetterID())
        #print(NewestLetterID)

        if letterID != NewestLetterID:
            self.ui.NextRecordPB.setText("Next") # If this is not the newest record in the database, don't promise the user that they can make a new record from the middle of the database.

        for fieldname in self.ui.LatestValueDict:
            fname = str(fieldname)
            fieldval = self.ui.LatestValueDict[fname]
            dbval = self.query_field(fieldname, letterID)
            if dbval != fieldval:
                print("Update needed")
                self.update_field(fieldname, dbval)
                self.ui.LatestValueDict[fname] = dbval
        #print("Done checking")


# __________________Lauch Application if File is Executed__________________
if __name__ == "__main__": 
      
    app = QtWidgets.QApplication([])
    app.setStyle('Fusion')

    application = NightLetterMain()

    #dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5() 
    #application.setStyleSheet(dark_stylesheet)
    application.setStyleSheet(loadStyleSheet())              

    newestRecordNum = application.get_newest_LetterID()
    application.load_all_fields(newestRecordNum)
 
    application.show()

    timer = QTimer(application)
    timer.timeout.connect(application.check_if_refresh_needed)
    timer.start(5000)

    sys.exit(app.exec()) 

#_____To do next_____

# Get Date picker for date field
# Allow navigation between letters - select by date, go to previous/next, filter by weekend/shutdown dates?
# Text search (possibly fuzzy?) - priority from Dan
# Make the Next button change to New Record if viewing the current record.

#_____Cosmetic_____
# Grow text fields based on size?
# Add pictures/colors to labels/menu bar

#_____Functional_____
#The load function should be rewritten so that all the data is obtained in 1 query and then distributed to the fields via a loop.
# # Make START Card Audits a number-only entry field?
# Export record as PDF functionality, although would prefer the MainWindow to be sufficiently readable as-is
# Query START card audits by month

#Code from Riley for verifying user ID and permission level from UserLevel Database
#UserName = getpass.getuser()
#        print(UserName) #username
#        con = application.sql_connection()
#        cursorObj = con.cursor()
#        cursorObj.execute("SELECT Level FROM UsersInfo Where UserName = '" + UserName + "' ")
#        vals = cursorObj.fetchall()
#        print(vals)
#        con.close()

#_____Done_____
# Allow user to select and attach PDFs and other files - Maybe a central Attachements field instead of 5 separate fields?
#  -Copy user selected files and store in central W: Drive folder
#  -Store links to the files in db
#  -Open files on command
#  -Not crash if user exits out of file picker
#Needs function to parse HTML into a dictionary of the paths and filenames in the Attachments field. Display the list in a dialog box to the user and allow them to choose which files to remove. Delete the files from both the Attachments field and the Attachments folder. 

# Store rich text formatting in database