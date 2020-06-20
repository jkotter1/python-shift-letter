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
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QFile, QTextStream, QEvent

from DefineUI import Ui_MainWindow  # importing our generated file
# Note: file generate from Qt5 as TestMain.ui - need to conver to .py and rename to DefineUI
#Use command "pyuic5 TestMain.ui > DefineUI.py"

class mywindow(QtWidgets.QMainWindow):
 
    def __init__(self, parent=None):

        super(mywindow, self).__init__(parent=parent)
 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initWidgets()

    def initWidgets(self):
        
        self.ui.savePB.clicked.connect(lambda: self.save_record())       
        self.ui.Safety.installEventFilter(self)

    def eventFilter(self, obj, event):  
        
        if event.type() == QEvent.FocusOut:
            if obj == self.ui.Safety:
                print("Saving Changes")
                self.save_record()
        
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
        #finally:
        #   con.close() 
    
    def save_record(self):
        con = self.sql_connection()
        cursorObj = con.cursor()
        
        if self.view_latest_record() == self.ui.latest_record:
            queryString = "UPDATE NightLetterData2 SET Safety = '" + self.ui.Safety.toPlainText() + "' WHERE LetterID = '" + self.ui.LetterID.toPlainText() + "'"
            cursorObj.execute(queryString)
            con.commit()
            con.close() 
        else:
            print("Record has been changed by another user. Please copy your changes, reload the form, and reenter the changes to save.")

    def load_latest_record(self):
        con = application.sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT LetterID, Safety FROM NightLetterData2 WHERE LetterID = 2")
        vals = cursorObj.fetchall()
        self.ui.LetterID.setText(vals[0][0])
        self.ui.Safety.setText(vals[0][1])
        self.ui.latest_record = vals[0][1]
        con.close() 

    def view_latest_record(self):
        con = application.sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT Safety FROM NightLetterData2 WHERE LetterID = 2")
        vals = cursorObj.fetchall()
        return vals[0][0]
        con.close() 

    def load_all_fields(self):
        #con = application.sql_connection()
        #cursorObj = con.cursor()

#        layout = self.ui.WidgetGridLayout
        
#        for i in range(layout.count()):
#            item = layout.itemAt(i)
            #print(item.widget().objectName())
#            itemName = item.widget().objectName()
            #if type(item) == QtGui.QLayoutItem:
#            try:
#                cursorObj.execute("SELECT " + itemName + " FROM NightLetterData2 WHERE LetterID = 2")
#            except OperationalError:
#                continue
#            vals = cursorObj.fetchall()
#            item.widget().setText(vals[0][0])
#        con.close() 
        try:
            sqliteConnection = application.sql_connection()
            cursor = sqliteConnection.cursor()
            #print("Database created and Successfully Connected to SQLite")

            for w in self.allWidgets():
                wName = w.widget().objectName()
                if isinstance(wName.lbl, QTextEdit)
                    sqlite_select_Query = "SELECT " + wName + " FROM NightLetterData2 WHERE LetterID = 2"
                    cursor.execute(sqlite_select_Query)
                    record = cursor.fetchall()
                    w.widget().setText(record[0][0])
                
                #try:  
                #    sqlite_select_Query = "SELECT " + wName + " FROM NightLetterData2 WHERE LetterID = 2"
                #    cursor.execute(sqlite_select_Query)
                #    record = cursor.fetchall()
                #    w.widget().setText(record[0][0])                    
                #except sqlite3.Error as error:
                #    print("Error while querying to sqlite", error) #This occurs when the program tries to query the values for label widgets, which do not exist in the database
                #except AttributeError:
                #    try:
                #        w.widget().dateTimeFromText(record[0][0])
                #    except AttributeError:
                #        w.widget().setItemText(0, record[0][0])
            cursor.close()

        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The SQLite connection is closed")

    def allWidgets(self):
        layout = self.ui.WidgetGridLayout
        return (layout.itemAt(i) for i in range(layout.count()))

app = QtWidgets.QApplication([])

application = mywindow()


application.load_latest_record()
application.load_all_fields()
 
application.show()

sys.exit(app.exec())

# To do next:
#    Add Refresh button
#    Add Dialog if there is a save conflict
#    Confirmation dialog after Save button is clicked
#    Loop through all fields to load.