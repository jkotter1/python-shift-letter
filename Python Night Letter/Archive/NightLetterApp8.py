#Note: convert this file to a .exe with the cx_Freeze python module and the command "python setup.py build" (see link for more info https://stackoverflow.com/questions/41570359/how-can-i-convert-a-py-to-exe-for-python)

import sys
import sqlite3
from sqlite3 import Error
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtCore import QFile, QTextStream, QEvent, QTimer
from datetime import datetime


from DefineUI import Ui_MainWindow  # importing our generated file
# Note: file generate from Qt5 as TestMain.ui - need to conver to .py and rename to DefineUI
#Use command "pyuic5 TestMain.ui > DefineUI.py"


class mywindow(QtWidgets.QMainWindow):
 
    def __init__(self, parent=None):

        super(mywindow, self).__init__(parent=parent)
 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.AutoSaveActive = False
    
    def savefield(self):
        if self.ui.AutoSaveActive:
            print("Saving Changes")
            self.save_field (self.focusWidget())

    def sql_connection(self):
        try:
            con = sqlite3.connect('Night Letter 2.0 data.db')
            return con
        except Error:
            print(Error)
    
    def save_field(self, obj):
        try:
            fieldName = obj.objectName()
            fieldtype = obj.__class__.__name__
            if fieldtype == "QDateEdit":
                fieldval = datetime.strftime(obj.date().toPyDate(), '%m/%d/%Y')
            elif fieldtype == "QComboBox":
                fieldval = str(obj.currentText())
            elif fieldtype == "QTextEdit":
                fieldval = obj.toPlainText()
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

    def load_most_recently_created_record(self):
        con = application.sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT max(LetterID) FROM NightLetterData2")
        vals = cursorObj.fetchall()
        con.close()
        latestRecordNum = vals[0][0]
        self.load_all_fields(latestRecordNum)
    
    def query_latest_record(self, fieldname, letterID):
        con = application.sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT " + fieldname + " FROM NightLetterData2 WHERE LetterID = '" + letterID + "'")
        vals = cursorObj.fetchall()
        return vals[0][0]
        con.close() 

    def load_all_fields(self, recordNum):
        self.ui.AutoSaveActive = False  #so we don't recursively call save_field on textChanged() forever
        FieldNames = ""
        FieldNameList = []
        for w in self.allWidgets():
            wName = w.widget().objectName()
            wType = w.widget().__class__.__name__
            if wType == "QTextEdit" or wType == "QDateEdit" or wType == "QComboBox":
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
            if wType  == "QTextEdit":
                w.widget().setText(str(LastVal[wName]))
            elif wType == "QDateEdit":
                date_str = LastVal[wName]
                date_object = datetime.strptime(date_str, '%m/%d/%Y').date()
                w.widget().setDate(date_object)
            elif wType == "QComboBox":
                currentIndex = w.widget().findText(str(LastVal[wName]))
                w.widget().setCurrentIndex(currentIndex)

        self.ui.AutoSaveActive = True # have to turn back on to save as the user types
    
    def allWidgets(self):
        layout = self.ui.WidgetGridLayout
        return (layout.itemAt(i) for i in range(layout.count()))

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)

    def update_field(self, fieldname, newval):
        for w in self.allWidgets():
            wName = w.widget().objectName() 
            if wName == fieldname:
                fieldtype = w.widget().__class__.__name__
                self.ui.AutoSaveActive = False
                if fieldtype  == "QTextEdit":
                    w.widget().setText(str(newval))
                elif fieldtype == "QDateEdit":
                    date_str = newval
                    date_object = datetime.strptime(date_str, '%m/%d/%Y').date()
                    w.widget().setDate(date_object)
                elif fieldtype == "QComboBox":
                    currentIndex = w.widget().findText(str(newval))
                    w.widget().setCurrentIndex(currentIndex)
                self.ui.AutoSaveActive = True

    def check_if_refresh_needed(self):
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
    
if __name__ == "__main__": 
    app = QtWidgets.QApplication([])

    application = mywindow()

    application.load_most_recently_created_record()
 
    application.show()

    timer = QTimer(application)
    timer.timeout.connect(application.check_if_refresh_needed)
    timer.start(5000)

    sys.exit(app.exec()) 

# To do next:
# Allow user to select and attach PDFs and other files - Maybe a central Attachements field instead of 5 separate fields?
#  -Copy user selected files and store in central W: Drive folder
#  -Store links to the files in db
#  -Open files on command
# Store rich text formatting?
# Hide/minimize field if empty?
# Make START Card Audits a number-only entry field?
# Get Date picker for date field
# Allow navigation between letters - select by date, go to previous/next, filter by weekend/shutdown dates?
# Text search (possibly fuzzy?)
# Export record as PDF functionality, although would prefer the MainWindow to be sufficiently readable as-is
# Query START card audits by month
# Add pictures/colors to labels/menu bar
