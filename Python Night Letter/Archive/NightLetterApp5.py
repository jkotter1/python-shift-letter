#from PyQt5 import QtWidgets, uic
#import sys
#app = QtWidgets.QApplication([])
#app.setStyle('PrettyGUI')
#win = uic.loadUi("TestMain.ui") #specify the location of your .ui file 
#win.show()
#sys.exit(app.exec())



import sys
import sqlite3
from sqlite3 import Error
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtCore import QFile, QTextStream, QEvent
from datetime import datetime


from DefineUI import Ui_MainWindow  # importing our generated file
# Note: file generate from Qt5 as TestMain.ui - need to conver to .py and rename to DefineUI
#Use command "pyuic5 TestMain.ui > DefineUI.py"

class mywindow(QtWidgets.QMainWindow):
 
    def __init__(self, parent=None):

        super(mywindow, self).__init__(parent=parent)
 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #self.initWidgets()
    
    def savefield(self):
        print(self.focusWidget())
        self.save_field (self.focusWidget())

    def initWidgets(self):  
        
        #self.ui.savePB.clicked.connect(lambda: self.save_field())  # need to design a save_all_records function for the Save button     
        #self.ui.Safety.installEventFilter(self)
        #print(type(self.ui.Safety))
        #print(type(self.ui.WidgetGridLayout))
        for widget in self.allWidgets():
            print(type(widget))
            widget.installEventFilter(self)

    def eventFilter(self, obj, event):  #don't think I am going to use this in my final product - it is too cumbersome to install the filter for each object. I will use the savefield connection from QT Designer instead.
        wType = obj.__class__.__name__
        if event.type() == QEvent.FocusOut:
            #if wType == "QTextEdit" or wType == "QDateEdit" or wType == "QComboBox":
            print("Saving Changes")
            self.save_field(obj)
        if event.type() == QEvent.FocusIn:
            if obj == self.ui.Safety:
                print("")
                #print("Loading Latest Version")
                #self.load_latest_record()
   
            #elif obj == self.pushButton:
            #    print("pushbutton")
            #elif obj == self.comboBox:
            #    print("combobox")

        return super(mywindow, self).eventFilter(obj, event)

    def sql_connection(self):
        try:
            con = sqlite3.connect('Night Letter 2.0 data.db')
            return con
        except Error:
            print(Error)
    
    def save_field(self, obj):
        try:
            fieldName = obj.objectName()
            fieldval = obj.toPlainText()
            letterID = self.ui.LetterID.toPlainText()
            lastLoadFieldValue = self.ui.LatestValueDict[obj.objectName()]
            con = self.sql_connection()
            cursorObj = con.cursor()
        
            if self.query_latest_record(fieldName, letterID) == lastLoadFieldValue:
                queryString = "UPDATE NightLetterData2 SET " + fieldName + " = '" + fieldval + "' WHERE LetterID = '" + letterID + "'"
                print(queryString)
                cursorObj.execute(queryString)
                con.commit()
                con.close() 

                lastLoadFieldValue = fieldval
            else:
                print("Record has been changed by another user. Please copy your changes, reload the form, and reenter the changes to save.")
        except AttributeError:
            if type(obj) == 'NoneType':
                print("No field currently in focus.")

    def load_latest_record(self):
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
    
    def allWidgets(self):
        layout = self.ui.WidgetGridLayout
        return (layout.itemAt(i) for i in range(layout.count()))

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)

app = QtWidgets.QApplication([])

application = mywindow()

application.load_latest_record()

#application.openFileNameDialog()
 
application.show()

sys.exit(app.exec()) 

# To do next:
#    Add Refresh button
#    Add Dialog if there is a save conflict
#    Confirmation dialog after Save button is clicked
#    Loop through all fields to load. Check!