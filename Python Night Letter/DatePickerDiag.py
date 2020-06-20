# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DatePickerDiag.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dateDialog(object):
    def setupUi(self, dateDialog):
        dateDialog.setObjectName("dateDialog")
        dateDialog.resize(442, 241)
        self.calendarWidget = QtWidgets.QCalendarWidget(dateDialog)
        self.calendarWidget.setGeometry(QtCore.QRect(10, 10, 421, 221))
        self.calendarWidget.setObjectName("calendarWidget")

        self.retranslateUi(dateDialog)
        QtCore.QMetaObject.connectSlotsByName(dateDialog)

    def retranslateUi(self, dateDialog):
        _translate = QtCore.QCoreApplication.translate
        dateDialog.setWindowTitle(_translate("dateDialog", "Date Calendar"))
