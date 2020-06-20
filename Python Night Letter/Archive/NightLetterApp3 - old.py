from PyQt5 import QtWidgets #, uic
from TestMain import MainWindow
import sys
import sqlite3
from sqlite3 import Error


#class Car(object):

  #def __init__(self, model, color, company, speed_limit):
    #self.color = color
    #self.company = company

def setupButtons():      
    print("running")
    #btn1 = win.QPushButton("savePB")
    #btn1.clicked.connect(self.buttonClicked) 
    #win.setWindowTitle('Night Letter')
    #print(win.QPushButton("savePB").name)
        
def buttonClicked(self):
    #sender = self.sender()
    print("Saving...")

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
    cursorObj.execute("CREATE TABLE employees(id integer PRIMARY KEY, name text, salary real, department text, position text, hireDate text)")
    con.commit()
    


if __name__ == "__main__": 
    app = QtWidgets.QApplication([])
    app.setStyle('PrettyGUI')


    con = sql_connection()
    #save_record(con)

    setupButtons()


    #win = uic.loadUi("TestMain.ui") #specify the location of your .ui file

    #btn1.clicked.connect(self.buttonClicked) 

    app.setWindowTitle('Night Letter')
    #   print(win.QPushButton("savePB").name)

    #win.show()
    sys.exit(app.exec())


#Loop through all widgets of a type
#for widget in centralwidget.children():
#    if isinstance(widget, QLineEdit):
#        print "linedit: %s  - %s" %(widget.objectName(),widget.text())

#    if isinstance(widget, QCheckBox):
#        print "checkBox: %s  - %s" %(widget.objectName(),widget.checkState()) https://stackoverflow.com/questions/5150182/loop-over-widgets-in-pyqt-layout

#compile command pyuic5 form1.ui > form1.py