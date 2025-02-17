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
        vals = application.executeQuery("SELECT * FROM {0} WHERE Date= '{1}'".format(application.DBDataSource, date_Selected))
        self.ui.AutoSaveActive = False
        if vals != []: #vals != []:
            NightLetterMain.load_all_fields(application, vals[0][0])
        else:
            print("There is no record for the date selected.") # Maybe a dialog box for this at some point?
        self.ui.AutoSaveActive = True
        self.reject()

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
            letterID = application.ui.LetterID.toPlainText()
            if checkBox.isChecked():
                AttachmentStoragePath = application.AttachmentFolderPath #Should have this reference the same global variable as the attach file function
                try:
                    os.remove(AttachmentStoragePath+letterID+"\\"+cbName)
                except FileNotFoundError:
                    print("The file was not found in the attachments folder.") # Probably should add a dialog box for this at some point.
                attachFieldString = attachFieldString.replace(cbName,"")
        application.ui.AutoSaveActive = False
        application.update_field("Attachments", attachFieldString)
        self.removeEmptyLines()
        application.save_field(application.ui.Attachments)
        application.ui.AutoSaveActive = True
    
    def removeEmptyLines(self):
        attachFieldString = application.ui.Attachments.toHtml()
        emptyCheckBox = "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>"
        application.update_field("Attachments", attachFieldString.replace(emptyCheckBox,""))


# __________________Setup Main Form Code__________________ (makes connections for event handlers and widget signals)
class NightLetterMain(QtWidgets.QMainWindow):
 
    def __init__(self, parent=None):

        super(NightLetterMain, self).__init__(parent)
 
        self.ui = Ui_MainWindow()
        self.DBDataSource = "NightLetterData" #Important: This tells the application which table to query in the DB.
        self.AttachmentFolderPath = "W:\\CLTBODY\\Kotter\\Projects\\Night Letter Updates\\Data\\Attachments"
        self.ui.setupUi(self)
        self.ui.AutoSaveActive = False
        self.ui.AttachmentPB.clicked.connect(lambda: self.attach_document(self.openFileNameDialog())) 

        self.ui.PrevRecordPB.clicked.connect(lambda: self.goToRecord("prev"))
        self.ui.NextRecordPB.clicked.connect(lambda: self.goToRecord("next"))

        self.ui.RemoveAttachmentPB.clicked.connect(self.remove_attachment)
        self.ui.Attachments.anchorClicked.connect(self.linkClicked)
        self.ui.Attachments.setOpenLinks(False)

        #self.ui.Date.installEventFilter(self)
        self.ui.GoToDate.clicked.connect(self.datePicker)

    
    #def eventFilter(self, source, event):
    #    self.ui.Date.mousePressEvent = self.datePicker
    #    return super(NightLetterMain, self).eventFilter(source, event)


# __________________Date Change/Record Navigation Code__________________ (works with Date Picker Dialog)
    def datePicker(self, obj):
        dpicker = DatePickerDialog()
        dpicker.setStyleSheet(loadStyleSheet())
        dpicker.exec_()    

    def linkClicked(self, url):
        try:
            linkPath = "\"" + url.toString().replace("%5C", "/") + "\""
            os.startfile(linkPath)
        except FileNotFoundError:
            print("The requested file is no longer available.") # Probably should add a dialog box for this at some point.
        except OSError:
            print("There is not default software for opening this file. Please right click the link, choose copy link location, then try to open the link with different software.")

    def goToRecord(self, direction): #combine with goToNextRecord?

        letterID = int(self.ui.LetterID.toPlainText())
        if direction == "prev":
            self.goToPreviousRecord(letterID) # = str(letterID - 1)
        elif direction == "next":
            #print("GoToRecord #"+str(letterID))
            self.goToNextRecord(letterID) # = str(letterID + 1)
        else:
            print("An error occured.")

    def goToPreviousRecord(self, recurseLetterId): # 
        
        OldestLetterID = int(self.get_newestORoldest_LetterID("oldest"))
        
        if recurseLetterId > OldestLetterID: # Normal case - go to the next oldest record
            prevLetterID = recurseLetterId - 1
        elif recurseLetterId == OldestLetterID: # Special case - you are already at the oldest record. You cannot go any farther back.
            prevLetterID = recurseLetterId
        else:                                # Not sure how you could get here
            print("The program attempted to access a record older than any record in the database, but it could only load the oldest record.")
            prevLetterID = recurseLetterId
        
        LatestValueDict = self.query_all_record_fields(prevLetterID)       #Dictionary of all the most recently queried values for each field from the database. Get the queried values by giving it the field name (i.e. self.ui.LatestValueDict[Safety] )
        
        if LatestValueDict == "Record Not Found" and prevLetterID > -1: # If the specific record number was not found in the database, try again with a smaller number to get to the correct previous record id. If you get to -1, you have gone too far.
            self.goToPreviousRecord(prevLetterID)
        else:
            self.load_all_fields(prevLetterID)

    def goToNextRecord(self, letterID): # Go to the next newest record. If currently at the newest record, create a new record with a higher LetterID
        
        NewestLetterID = int(self.get_newestORoldest_LetterID("newest"))
        nextLetterID = letterID + 1
        
        if letterID == NewestLetterID:
            New_Record_Query = "INSERT INTO {0} (LetterID, Date) VALUES (\"{1}\",\"{2}\")".format(self.DBDataSource, nextLetterID, date.today().strftime("%m/%d/%Y"))
            test = self.executeQuery(New_Record_Query)
            if test != "Record Not Found": #Make sure the record is added to the DB without errors before we try to load it
                self.load_all_fields(nextLetterID)
        else:
            LatestValueDict = self.query_all_record_fields(nextLetterID)       #Dictionary of all the most recently queried values for each field from the database. Get the queried values by giving it the field name (i.e. self.ui.LatestValueDict[Safety] )
            if LatestValueDict == "Record Not Found": # If the specific record number was not found in the database, try again with a incrementally larger number to get to the correct next record id.
                self.goToNextRecord(nextLetterID)
            else:
                self.load_all_fields(nextLetterID)


# __________________File Attachment/Removal Functions__________________ (works with Remove Attachments Dialog)
    def attach_document(self, docPath):
        
        letterID = self.ui.LetterID.toPlainText()
        
        #If the dialog is closed by the user, the docPath is None and we end here
        if docPath is None:
            return
        fileName = self.getFileName(docPath)
        
        #If no name is entered by the user, the fileName is None and we end here
        if fileName == False:
            return

        #Check if an attachment folder for this letter ID exists
        letterIDAttachFolder = self.AttachmentFolderPath + "\\" + letterID
        if not os.path.isdir(letterIDAttachFolder): #If the folder does not exist, make it
            os.mkdir(letterIDAttachFolder)

        newDocPath = "{0}\\{1}".format(letterIDAttachFolder, fileName)
        copyNum = 0
        
        #if a file of the same name exists in the folder we are using, add a number in parenthesis to the end to avoid errors from having two files of the same name
        while os.path.isfile(newDocPath): 
            newDocPath= "{0}\\{1}\\{2}({3}).{4}".format(self.AttachmentFolderPath, letterID, fileName.rsplit('.', 1)[0], str(copyNum), fileName.rsplit('.', 1)[1])
            copyNum += 1        
        if copyNum > 0:
            fileName = "{0}({2}).{1}".format(*fileName.rsplit('.', 1) + [copyNum])
        
        shutil.copyfile(docPath, newDocPath)
        fileLink = '<a href=\"{0}\">{1}</a>'.format(newDocPath, fileName)
        self.ui.Attachments.append(fileLink)
        self.save_field(self.ui.Attachments)
        #print(self.ui.Attachments.toPlainText())
        #self.ui.Attachments.setText(self.ui.Attachments.toPlainText().split("</p>")[0] + fileLink + self.ui.Attachments.toPlainText().split("</p>")[1])
        
    
    def remove_attachment(self): #Launch the remove attachments dialog only if there are actually attachments to remove
        attachList =  self.ui.Attachments.toPlainText().split("\n")
        if attachList == ['']: #If there are no attachments to remove, do not open the removal dialog
            return
        rad = RemoveAttachmentDialog(attachList)
        rad.setStyleSheet(loadStyleSheet())
        rad.exec_()

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

    def updateAttachmentLinks(self): 
        #Used during migration to reformat all links from an Access dump to refer to the new Attachment file locations
        #Caution! No attachment links can have HTML formatting, or this function will mess them up.
        #In order to run this function, I had to map it to a button and call it once the form loaded.
        getAllAttachmentText = "SELECT LetterID, Attachments from NightLetterData"
        SQLData = self.executeQuery(getAllAttachmentText)
        for LetterIDandAttachmentPair in SQLData:
            fileNames = LetterIDandAttachmentPair[1].split("\n")
            linkStringList = []
            for name in fileNames:
                if name != '':
                    linkStringList.append("<a href=\"{0}\">{1}</a>".format(self.AttachmentFolderPath + "\\" + str(LetterIDandAttachmentPair[0]) + "\\" + name, name))
            if linkStringList != []:
                self.load_all_fields(LetterIDandAttachmentPair[0])
                self.ui.Attachments.setText("")
                for link in linkStringList:
                    self.ui.Attachments.append(link)
                    self.save_field(self.ui.Attachments)


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
    
    def executeQuery(self, queryString, htmlarg = ""): #function for communicating with the sqlite3 db. It executes a given query string, using a special format if the query includes a html string from a field.
        try:
            sqliteConnection = sqlite3.connect('Night Letter 2.0 data.db')
            cursor = sqliteConnection.cursor()
            if htmlarg != "":
                cursor.execute(queryString, [htmlarg]) # Have to use this format to write html strings, otherwise the "<" and ">" cause errors when writing to the sqlite db
            else:
                cursor.execute(queryString)
            sqliteConnection.commit()
            SQLrecord = cursor.fetchall()
            cursor.close()
            return SQLrecord
        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
            return "Record Not Found"

    def save_field(self, obj): #saves an individual field by writing its current value to the db
        try:
            fieldName = obj.objectName()
            fieldtype = obj.__class__.__name__
            if fieldtype == "QDateEdit":
                fieldval = datetime.strftime(obj.date().toPyDate(), '%m/%d/%Y')
            elif fieldtype == "QComboBox":
                fieldval = str(obj.currentText())
            elif fieldtype == "QTextEdit" or fieldtype == "QTextBrowser":
                fieldval = obj.toHtml()
            letterID = self.ui.LetterID.toPlainText()
            valdict = self.ui.LatestValueDict
            
            if fieldName in valdict:
                lastLoadFieldValue = valdict[fieldName]
                currentDBFieldValue = self.executeQuery("SELECT {0} FROM {1} WHERE LetterID = '{2}'".format(fieldName, self.DBDataSource, letterID))[0][0] 
                                                        
                if currentDBFieldValue == lastLoadFieldValue or currentDBFieldValue == None:
                    queryString = "UPDATE {0} SET {1} = ? WHERE LetterID = '{2}'".format(self.DBDataSource, fieldName, letterID)

                    self.executeQuery(queryString, fieldval)   
                    self.ui.LatestValueDict[fieldName] = fieldval
                else:
                    self.load_all_fields(letterID)
                    print("Record has been changed by another user. Please copy your changes, reload the form, and reenter the changes to save.")
        except AttributeError:
            if type(obj) == 'NoneType':
                print("No field currently in focus.")
            else:
                 raise AttributeError

    def load_most_recently_created_record(self): # Finds and loads the record with the most recent date
        latestRecordNum = self.executeQuery("SELECT max(LetterID) FROM {0}".format(self.DBDataSource))[0][0]
        self.load_all_fields(latestRecordNum)

    def get_newestORoldest_LetterID(self, indicator): # Finds and loads the oldest or most recent record 
        if indicator == "newest":
            return self.executeQuery("SELECT max(LetterID) FROM {0}".format(self.DBDataSource))[0][0]
        elif indicator == "oldest":
            return self.executeQuery("SELECT min(LetterID) FROM {0}".format(self.DBDataSource))[0][0]
        else:
            print("The get_firstORlast_LetterID function needs an argument that says either \"newest\" or \"oldest\". It didn't get either, so you probably got an error.")
        return RecordNum
    
    def list_all_fields(self): # Get a list of all the fields that can be updated. This will later be used to query the info needed from the db
        FieldNames = ""
        FieldNameList = []
        for w in self.allWidgets():
            try:
                wName = w.widget().objectName()
                wType = w.widget().__class__.__name__
                if wType == "QTextEdit" or wType == "QTextBrowser" or wType == "QDateEdit" or wType == "QComboBox":
                    FieldNameList.append(wName)
                    if FieldNames == "":
                        FieldNames = wName
                    else:
                        FieldNames = FieldNames + ", " + wName
            except AttributeError:
                continue
        return FieldNames, FieldNameList

    def query_all_record_fields(self, recordNum): # Query the db for all the record fields associated with a particular LetterID, then store that info in a dictionary for future use
        fields = self.list_all_fields()
        FieldNames = fields[0]
        FieldNameList = fields[1]

        SQLrecord = self.executeQuery("SELECT {0} FROM {1} WHERE LetterID = {2}".format(FieldNames, self.DBDataSource, str(recordNum)))

        if SQLrecord == []:
            return "Record Not Found"

        FieldValueList = list(SQLrecord[0])
        for index, item in enumerate(FieldValueList):
            if item == None:
                FieldValueList[index] = ""

        LatestValueDict = dict(zip(FieldNameList, FieldValueList))
        return LatestValueDict
        
    def load_all_fields(self, recordNum): # Queries the values for all fields from the database and inserts the values into the fields for the letter form
        self.ui.AutoSaveActive = False    # so we don't recursively call save_field on textChanged() forever

        self.ui.LatestValueDict = self.query_all_record_fields(recordNum)       #Dictionary of all the most recently queried values for each field from the database. Get the queried values by giving it the field name (i.e. self.ui.LatestValueDict[Safety] )

        #Adjust navigation buttons if we are the first or last record
        if self.ui.LatestValueDict["LetterID"] == self.get_newestORoldest_LetterID("newest"):
            self.ui.NextRecordPB.setText("New...")
        else:
            self.ui.NextRecordPB.setText("Next")

        if self.ui.LatestValueDict["LetterID"] == self.get_newestORoldest_LetterID("oldest"):
            self.ui.PrevRecordPB.hide()
        else:
            self.ui.PrevRecordPB.show()
        
        #Go through each QWidget and see if it is a type that can be updated. If it can, update the field with a value from the LastestValDict that we just queried from the db
        for w in self.allWidgets():
            try:
                wName = w.widget().objectName() 
                wType = w.widget().__class__.__name__
                if wType  == "QTextEdit" or wType == "QTextBrowser" or wType == "QComboBox":
                    NewVal = str(self.ui.LatestValueDict[wName])
                    self.update_field(wName,NewVal)
            except AttributeError:
                pass
            except KeyError:
                print(NewVal)

        self.ui.AutoSaveActive = True # have to turn back on to save as the user types
    
    def findAllWidgets(self, layout): # returns a list of all widgets 
        return (layout.itemAt(i) for i in range(layout.count()))

    def allWidgets(self):

        layouts = [self.ui.WidgetLayout1, self.ui.WidgetLayout2, self.ui.WidgetLayout3, self.ui.WidgetLayout4]
        itemlist = []
        for layout in layouts:
            for i in range(layout.count()):
                itemlist.append(layout.itemAt(i))
        return itemlist

    def update_field(self, fieldname, newval): # Inserts a new value into a field
        for w in self.allWidgets():
            try:
                wName = w.widget().objectName() 
                if wName == fieldname:
                    fieldtype = w.widget().__class__.__name__
                    self.ui.AutoSaveActive = False
                    if fieldtype  == "QTextEdit" or fieldtype == "QTextBrowser":
                        w.widget().setText(str(newval))
                    elif fieldtype == "QComboBox":
                        currentIndex = w.widget().findText(str(newval))
                        w.widget().setCurrentIndex(currentIndex)
                    self.ui.AutoSaveActive = True
            except AttributeError:
                continue

    def check_if_refresh_needed(self): # Check if changes to a record have occured in the database since the record was last loaded. If a change has occured, reload the record.
        letterID = str(self.ui.LetterID.toPlainText())
        NewestLetterID = str(self.get_newestORoldest_LetterID("newest"))
        LatestVals = self.query_all_record_fields(letterID)  #Dictionary of all the most recently queried values for each field from the database. Get the queried values by giving it the field name (i.e. LatestVals[Safety] )

        if letterID != NewestLetterID:
            self.ui.NextRecordPB.setText("Next") # If this is not the newest record in the database, don't promise the user that they can make a new record from the middle of the database.

        for fieldname in self.ui.LatestValueDict:
            fname = str(fieldname)
            fieldval = self.ui.LatestValueDict[fname]
            dbval = LatestVals[fieldname]
            if dbval != fieldval:
                self.update_field(fieldname, dbval)
                self.ui.LatestValueDict[fname] = dbval

# __________________Launch Application if File is Executed__________________
if __name__ == "__main__": 
      
    app = QtWidgets.QApplication([])
    app.setStyle('Fusion')

    application = NightLetterMain()

    #dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5() 
    #application.setStyleSheet(dark_stylesheet)
    application.setStyleSheet(loadStyleSheet())
    
    

    newestRecordNum = application.get_newestORoldest_LetterID("newest")
    application.load_all_fields(newestRecordNum)
 
    application.showMaximized()

    

    timer = QTimer(application)
    timer.timeout.connect(application.check_if_refresh_needed)
    timer.start(5000)
    

    sys.exit(app.exec()) 

#_____To do next_____


# Allow navigation between letters - select by date, go to previous/next, filter by weekend/shutdown dates?
# Text search (possibly fuzzy?) - priority from Dan


#_____Cosmetic_____
# Grow text fields based on size?
# Add pictures/colors to labels/menu bar


#_____Functional_____

# 
# Make the Date field editable. Use a separate date picker dialog to jump to a letter from a certain date (Maybe grey out dates that don't have letters on file?)
# Make START Card Audits a number-only entry field?
# Export record as PDF functionality
# Query START card audits by month
# Search all letters for specific search terms, return a set of letters that have search results

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
# Make None text go away when loading Null SQL fields
# Allow user to select and attach PDFs and other files - Maybe a central Attachements field instead of 5 separate fields?
#  -Copy user selected files and store in central W: Drive folder
#  -Store links to the files in db
#  -Open files on command
#  -Not crash if user exits out of file picker
#Needs function to parse HTML into a dictionary of the paths and filenames in the Attachments field. Display the list in a dialog box to the user and allow them to choose which files to remove. Delete the files from both the Attachments field and the Attachments folder. 
# Get Date picker for date field
# Store rich text formatting in database
# Make the Next button change to New Record if viewing the current record.
# The load function should be rewritten so that all the data is obtained in 1 query and then distributed to the fields via a loop.