# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\query.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(688, 481)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 20, 661, 381))
        self.groupBox.setObjectName("groupBox")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(40, 40, 51, 21))
        self.label.setObjectName("label")
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(110, 40, 121, 22))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.textEdit = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit.setGeometry(QtCore.QRect(10, 80, 641, 291))
        self.textEdit.setObjectName("textEdit")
        self.queryBtn = QtWidgets.QPushButton(self.centralwidget)
        self.queryBtn.setGeometry(QtCore.QRect(10, 410, 93, 28))
        self.queryBtn.setObjectName("queryBtn")
        self.clearBtn = QtWidgets.QPushButton(self.centralwidget)
        self.clearBtn.setGeometry(QtCore.QRect(130, 410, 93, 28))
        self.clearBtn.setObjectName("clearBtn")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.queryBtn.clicked.connect(MainWindow.query)
        self.clearBtn.clicked.connect(MainWindow.clear)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "查询城市天气"))
        self.label.setText(_translate("MainWindow", "城市"))
        self.comboBox.setItemText(0, _translate("MainWindow", "北京"))
        self.comboBox.setItemText(1, _translate("MainWindow", "天津"))
        self.comboBox.setItemText(2, _translate("MainWindow", "深圳"))
        self.queryBtn.setText(_translate("MainWindow", "查询"))
        self.clearBtn.setText(_translate("MainWindow", "清空"))

