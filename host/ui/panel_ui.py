# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'panel_ui.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.table_nodes = QtWidgets.QTableView(self.centralwidget)
        self.table_nodes.setGeometry(QtCore.QRect(160, 70, 451, 441))
        self.table_nodes.setObjectName("table_nodes")
        self.button_refresh = QtWidgets.QPushButton(self.centralwidget)
        self.button_refresh.setGeometry(QtCore.QRect(490, 520, 113, 32))
        self.button_refresh.setObjectName("button_refresh")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.button_refresh.setText(_translate("MainWindow", "Refresh"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
