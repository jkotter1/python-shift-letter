# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RemoveAttachDiag.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_RemAtDiag(object):
    def setupUi(self, RemAtDiag):
        RemAtDiag.setObjectName("RemAtDiag")
        RemAtDiag.resize(471, 300)
        self.gridLayout = QtWidgets.QGridLayout(RemAtDiag)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(RemAtDiag)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(RemAtDiag)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.selectionLayout = QtWidgets.QGridLayout()
        self.selectionLayout.setObjectName("selectionLayout")
        self.gridLayout.addLayout(self.selectionLayout, 1, 0, 1, 1)

        self.retranslateUi(RemAtDiag)
        self.buttonBox.accepted.connect(RemAtDiag.accept)
        self.buttonBox.rejected.connect(RemAtDiag.reject)
        QtCore.QMetaObject.connectSlotsByName(RemAtDiag)

    def retranslateUi(self, RemAtDiag):
        _translate = QtCore.QCoreApplication.translate
        RemAtDiag.setWindowTitle(_translate("RemAtDiag", "Remove Attachment"))
        self.label.setText(_translate("RemAtDiag", "Choose attachments to remove:"))
