#from PyQt5 import QtWidgets, uic
#import sys
#app = QtWidgets.QApplication([])
#app.setStyle('PrettyGUI')
#win = uic.loadUi("TestMain.ui") #specify the location of your .ui file 
#win.show()
#sys.exit(app.exec())




from PyQt5 import QtWidgets
from PyQt5.QtCore import QFile, QTextStream

#import breeze_resources

from TestMain import Ui_MainWindow  # importing our generated file
import sys
import sqlite3
from sqlite3 import Error

class mywindow(QtWidgets.QMainWindow):
 
    def __init__(self):
 
        super(mywindow, self).__init__()
 
        self.ui = Ui_MainWindow()
    
        self.ui.setupUi(self)

def sql_connection():
    try:
        con = sqlite3.connect('Night Letter 2.0 data.db')
        return con
    except Error:
        print(Error)
    #finally:
    #   con.close() 

def save_record(con):
    cursorObj = con.cursor()
    #cursorObj.execute("CREATE TABLE employees(id integer PRIMARY KEY, name text, salary real, department text, position text, hireDate text)")
    con.commit()

def load_latest_record(con):
    cursorObj = con.cursor()
    cursorObj.execute("SELECT * FROM NightLetterData1 WHERE LetterID = 2019122")
    row = cursorObj.fetchall()
    print(row)
 

app = QtWidgets.QApplication([])

con = sql_connection()
load_latest_record(con)
#print('data saved?')

#file = QFile(":/dark.qss")
#file.open(QFile.ReadOnly | QFile.Text)
#stream = QTextStream(file)
#app.setStyleSheet(stream.readAll())

application = mywindow()
 
application.show()

sys.exit(app.exec())

