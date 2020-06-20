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

class mywindow(QtWidgets.QMainWindow):
 
    def __init__(self, parent=None):

        super(mywindow, self).__init__(parent=parent)
 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initWidgets()

    def initWidgets(self):
        
        self.ui.savePB.clicked.connect(lambda: self.save_record())       
        self.ui.textEdit_3.installEventFilter(self)

    def eventFilter(self, obj, event):  
        
        if event.type() == QEvent.FocusOut:
            if obj == self.ui.textEdit_3:
                print("Saving Changes")
                self.save_record()
        
        if event.type() == QEvent.FocusIn:
            if obj == self.ui.textEdit_3:
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
            queryString = "UPDATE NightLetterData1 SET Safety = '" + self.ui.textEdit_3.toPlainText() + "' WHERE LetterID = '" + self.ui.textEdit_24.toPlainText() + "'"
            cursorObj.execute(queryString)
            con.commit()
            con.close() 
        else:
            print("Record has been changed by another user. Please copy your changes, reload the form, and reenter the changes to save.")

    def load_latest_record(self):
        con = application.sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT LetterID, Safety FROM NightLetterData1 WHERE LetterID = 2019122")
        vals = cursorObj.fetchall()
        self.ui.textEdit_24.setText(vals[0][0])
        self.ui.textEdit_3.setText(vals[0][1])
        self.ui.latest_record = vals[0][1]
        con.close() 

    def view_latest_record(self):
        con = application.sql_connection()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT Safety FROM NightLetterData1 WHERE LetterID = 2019122")
        vals = cursorObj.fetchall()
        return vals[0][0]
        con.close() 

app = QtWidgets.QApplication([])

application = mywindow()


application.load_latest_record()
 
application.show()

sys.exit(app.exec())

# To do next:
#    Add Refresh button
#    Add Dialog if there is a save conflict