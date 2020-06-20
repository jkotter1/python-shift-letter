#Note: convert this file to a .exe with the cx_Freeze python module and the command "python setup.py build" (see link for more info https://stackoverflow.com/questions/41570359/how-can-i-convert-a-py-to-exe-for-python)

import sys
import os
import subprocess
import shutil 
import sqlite3
from sqlite3 import Error
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QCalendarWidget
from PyQt5.QtCore import QFile, QTextStream, QEvent, QTimer, QUrl, QDate
from datetime import datetime
#import qdarkstyle
from NightLetterAppStyleSheet import loadStyleSheet

from DefineUI import Ui_MainWindow  # importing our generated file
# Note: file generate from Qt5 as TestMain.ui - need to conver to .py and rename to DefineUI
#Use command "pyuic5 TestMain.ui > DefineUI.py"


class mywindow(QtWidgets.QMainWindow):
 
    def __init__(self, parent=None):

        super(mywindow, self).__init__(parent=parent)
 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.AutoSaveActive = False
        self.ui.AttachmentPB.clicked.connect(lambda: self.attach_document(self.openFileNameDialog()))
        #Riley
        self.ui.pushButton.clicked.connect(self.changeRecordDown)
        self.ui.pushButton_2.clicked.connect(self.changeRecordUp)
        self.ui.calendarWidget.clicked.connect(self.calendar)
        #Riley
        self.ui.Attachments.anchorClicked.connect(self.linkClicked)
        self.ui.Attachments.setOpenLinks(False)

    def linkClicked(self, url):
        linkPath = "\"" + url.toString().replace("%5C", "/") + "\""
        os.startfile(linkPath)

#Riley
    def changeRecordDown(self):
        downValue = self.ui.LetterID.toPlainText()
        downValue = int(downValue)
        downValue = downValue - 1
        downValue = str(downValue)
        print(downValue)  # the following is copied code modified
        con = application.sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT " + downValue + " FROM NightLetterData2")
        vals = cursorObj.fetchall()
        con.close()
        latestRecordNum = vals[0][0]
        self.load_all_fields(latestRecordNum)
#Riley
#Riley
    def changeRecordUp(self):
        upValue = self.ui.LetterID.toPlainText()
        upValue = int(upValue)
        upValue = upValue + 1
        upValue = str(upValue)
        print(upValue) 
        con = application.sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT " + upValue + " FROM NightLetterData2")
        vals = cursorObj.fetchall()
        con.close()
        latestRecordNum = vals[0][0]
        self.load_all_fields(latestRecordNum)
#Riley 

#Riley

    def calendar(self):
        dateSel = self.ui.calendarWidget.selectedDate()
        #dateSel.toString('%m/%d/%Y')
        date_Selected = datetime.strftime(dateSel.toPyDate(), '%m/%d/%Y')
        print(date_Selected)
        con = application.sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT * FROM NightLetterData2 WHERE Date= '" + date_Selected +  "'")
        vals = cursorObj.fetchall()
        con.close()
        latestRecordNum = vals[0][0]
        self.load_all_fields(latestRecordNum)
        #datestring = datetime.strftime(dateSel.toPyDate(), '%m/%d/%Y')
        #print(datestring)
        #self.ui.Date.setDate(dateSel)
      

        
#Riley



    def attach_document(self, docPath):
        NightLetterPath = os.path.dirname(os.path.abspath(__file__)).replace("%5C", "//")
        #print(NightLetterPath)
        attachLoc = "\\Attachments" # Must have a folder named Attachments in the same directory as running script
        fileName = self.getFileName(docPath)
        newDocPath = NightLetterPath + attachLoc + "\\" + fileName
        shutil.copyfile(docPath, newDocPath)
        fileLink = '<span><a href=\"{0}\">{1}</a></span>'.format(newDocPath, fileName)
        self.ui.Attachments.append(fileLink)
        #self.save_field(self.ui.Attachments)
        try:
            fieldName = "Attachments"
            fieldval = fileLink
            letterID = self.ui.LetterID.toPlainText()
            valdict = self.ui.LatestValueDict
            lastLoadFieldValue = valdict[fieldName]
            
            con = self.sql_connection()
            cursorObj = con.cursor()
            if self.query_latest_record(fieldName, letterID) == lastLoadFieldValue:
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
        #print(docPath)

    def fileExists(self, filepath):
        try:
            os.path.isfile(filepath)
        except IOError:
            return False
        return True

    def getFileName(self, path):
        head, tail = os.path.split(path)
        return tail or os.path.basename(head)

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
            elif fieldtype == "QTextEdit":
                fieldval = obj.toPlainText()
            elif fieldtype == "QTextBrowser":
                fieldval = obj.toPlainText()
                #print(fieldval)
            letterID = self.ui.LetterID.toPlainText()
            valdict = self.ui.LatestValueDict
            if fieldName in valdict:
                lastLoadFieldValue = valdict[fieldName]
                con = self.sql_connection()
                cursorObj = con.cursor()
                if self.query_latest_record(fieldName, letterID) == lastLoadFieldValue:
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
        self.load_all_fields(latestRecordNum)
    
    def query_latest_record(self, fieldname, letterID): # Finds the letter number of the letter with the most recent date
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
            sqlite_select_Query = "SELECT " + FieldNames + " FROM NightLetterData2 WHERE LetterID = " + str(recordNum)
            cursor.execute(sqlite_select_Query)
            record = cursor.fetchall()
            self.latest_record = record
            cursor.close()
        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()

        FieldValueList = record[0]
        self.ui.LatestValueDict = dict(zip(FieldNameList, FieldValueList))
        LastVal = self.ui.LatestValueDict       #Dictionary of all the most recently queried values for each field from the database. Get the queried values by giving it the field name (i.e. LastVal[Safety] )
        
        for w in self.allWidgets():
            wName = w.widget().objectName() 
            wType = w.widget().__class__.__name__
            if wType  == "QTextEdit" or wType == "QTextBrowser":
                w.widget().setText(str(LastVal[wName]))
            elif wType == "QDateEdit":
                date_str = LastVal[wName]
                date_object = datetime.strptime(date_str, '%m/%d/%Y').date()
                w.widget().setDate(date_object)
            elif wType == "QComboBox":
                currentIndex = w.widget().findText(str(LastVal[wName]))
                w.widget().setCurrentIndex(currentIndex)

        self.ui.AutoSaveActive = True # have to turn back on to save as the user types
    
    def allWidgets(self): # returns a list of all widgets 
        layout = self.ui.WidgetGridLayout
        return (layout.itemAt(i) for i in range(layout.count()))

    def openFileNameDialog(self): # Launches a file picker dialog that allows the user to browse and choose a file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            return fileName

    def update_field(self, fieldname, newval): # Inserts a new value into a field
        for w in self.allWidgets():
            wName = w.widget().objectName() 
            if wName == fieldname:
                fieldtype = w.widget().__class__.__name__
                self.ui.AutoSaveActive = False
                if fieldtype  == "QTextEdit" or fieldtype == "QTextBrowser":
                    w.widget().setText(str(newval))
                elif fieldtype == "QDateEdit":
                    date_str = newval
                    date_object = datetime.strptime(date_str, '%m/%d/%Y').date()
                    w.widget().setDate(date_object)
                elif fieldtype == "QComboBox":
                    currentIndex = w.widget().findText(str(newval))
                    w.widget().setCurrentIndex(currentIndex)
                self.ui.AutoSaveActive = True

    def check_if_refresh_needed(self): # Check if changes to a record have occured in the database since the record was last loaded. If a change has occured, reload the record.
        print("Checking for db changes")
        letterID = self.ui.LetterID.toPlainText()
        for fieldname in self.ui.LatestValueDict:
            fname = str(fieldname)
            fieldval = self.ui.LatestValueDict[fname]
            dbval = self.query_latest_record(fieldname, letterID)
            if dbval != fieldval:
                print("Update needed")
                self.update_field(fieldname, dbval)
                self.ui.LatestValueDict[fname] = dbval
        print("Done checking")
    
    #def loadStyleSheet(self):
    #    styleSheetFile="NightLetterAppStyleSheet.py"
    #    fileContents = open(styleSheetFile,"r")
    #    StylesheetString = str(fileContents.read())
    #    self.setStyleSheet(StylesheetString) 

if __name__ == "__main__": 
      
    app = QtWidgets.QApplication([])
    app.setStyle('Fusion')

    application = mywindow()

    #dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5() 
    #application.setStyleSheet(dark_stylesheet)
    #application.setStyleSheet("/NightLetterAppStyleSheet.py")
    application.setStyleSheet(loadStyleSheet())              

    application.load_most_recently_created_record()
 
    application.show()



    # timer = QTimer(application)
     #timer.timeout.connect(application.check_if_refresh_needed)
    # timer.start(5000)



    sys.exit(app.exec()) 

# To do next:
# Allow user to select and attach PDFs and other files - Maybe a central Attachements field instead of 5 separate fields?
#  -Copy user selected files and store in central W: Drive folder
#  -Store links to the files in db
#  -Open files on command
#  -Not crash if user exits out of file picker

# Get Date picker for date field

# Store rich text formatting in database?
# Hide/minimize field if empty?
# Make START Card Audits a number-only entry field?

# Allow navigation between letters - select by date, go to previous/next, filter by weekend/shutdown dates?
# Text search (possibly fuzzy?)
# Export record as PDF functionality, although would prefer the MainWindow to be sufficiently readable as-is
# Query START card audits by month
# Add pictures/colors to labels/menu bar

